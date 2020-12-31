import asyncio
import orjson
from urllib.parse import quote as urlquote
import aiohttp
from enum import Enum

from ..entities import *
from ..flags import *
from .ratelimits import *
from .errors import *

__all__ = (
    "Request",
    "HTTPClient",
)


async def json_or_text(response):
    text = await response.text(encoding='utf-8')
    try:
        if response.headers['content-type'] == 'application/json':
            return orjson.loads(text)
    except KeyError:
        pass

    return text


def entity_or_id(thing):
    if isinstance(thing, Entity):
        return thing.id

    return thing


def make_json(options, allowed=None, converters=None):
    json = options.pop("raw", {})
    json.update(options)

    def _default_converter(v):
        if isinstance(v, Enum) or isinstance(v, Flags):
            return v.value

        if isinstance(v, Entity):
            return v.id

        return v

    converters = converters or {}
    for k, v in json.items():
        converter = converters.get(k, _default_converter)
        json[k] = converter(v)

    if allowed is None:
        return json

    else:
        return {k: v for k, v in json.items() if k in allowed}


class File:
    __slots__ = ("fp", "filename", "_original_pos", "_closer")

    def __init__(self, fp, filename=None, *, spoiler=False):
        self.fp = fp
        self.filename = filename or getattr(fp, 'name', None)
        if spoiler:
            self.filename = f"SPOILER_{self.filename}"

        # aiohttp closes file objects automatically, we don't want that
        self._closer = self.fp.close
        self.fp.close = lambda: None

    def reset(self):
        self.fp.seek(self._original_pos)

    def close(self):
        self.fp.close = self._closer
        self._closer()


class Request:
    BASE = 'https://discord.com/api/v8'

    def __init__(self, method, path, max_tries=5, converter=None, **params):
        self.method = method
        self.path = path.strip("/")
        self.max_tries = max_tries

        self.url = f"{self.BASE}/{self.path}".format(**{k: urlquote(str(v)) for k, v in params.items()})

        self._channel_id = params.get("channel_id")
        self._guild_id = params.get("guild_id")
        self._webhook_id = params.get("webhook_id")

        self.ratelimit = None
        self.future = asyncio.Future()
        self.task = None

        self._converter = converter

    @property
    def bucket(self):
        if self._webhook_id is not None:
            return self._webhook_id

        else:
            return '{0._channel_id}:{0._guild_id}:{0.path}'.format(self)

    def cancel(self):
        self.task.cancel()

    def set_data(self, data):
        if not self.future.done():
            if self._converter is not None:
                data = self._converter(data)

            self.future.set_result(data)

    def set_exception(self, exc):
        if not self.future.done():
            self.future.set_exception(exc)

    def __await__(self):
        return self.future.__await__()


class HTTPClient:
    def __init__(self, token, ratelimits, **kwargs):
        self._token = token
        self._ratelimits = ratelimits
        self._session = kwargs.get("session")
        self.loop = kwargs.get("loop", asyncio.get_event_loop())

    async def _check_ratelimits(self, req):
        global_rl = await self._ratelimits.get_global()
        if global_rl is not None:
            req.ratelimit = global_rl
            await global_rl.wait()

        bucket_rl = await self._ratelimits.get_bucket(req.bucket)
        if bucket_rl is not None:
            req.ratelimit = bucket_rl
            await bucket_rl.wait()

    async def _perform_request(self, req, **kwargs):
        headers = {
            "User-Agent": "",
            "Authorization": f"Bot {self._token}"
        }

        if "json" in kwargs:
            data = kwargs.pop("json")
            if data is not None:
                headers["Content-Type"] = "application/json"
                kwargs["data"] = orjson.dumps(data)

        if kwargs.get("reason") is not None:
            headers["X-Audit-Log-Reason"] = urlquote(kwargs.pop("reason"), safe="/ ")

        async with self._session.request(
                method=req.method,
                url=req.url,
                headers=headers,
                raise_for_status=False,
                **kwargs
        ) as resp:
            data = await json_or_text(resp)

            if 300 > resp.status >= 200:
                remaining = resp.headers.get('X-Ratelimit-Remaining')
                reset_after = resp.headers.get('X-Ratelimit-Reset-After')
                if remaining is not None and reset_after is not None:
                    req.ratelimit = Ratelimit(float(reset_after), int(remaining))
                    await self._ratelimits.set_bucket(req.bucket, float(reset_after), int(remaining))

                req.set_data(data)

            elif resp.status == 429:
                if resp.headers.get('Via'):
                    retry_after = data['retry_after']
                    is_global = data.get('global', False)
                    if is_global:
                        req.ratelimit = Ratelimit(retry_after, 0, is_global=True)
                        await self._ratelimits.set_global(retry_after)

                    else:
                        req.ratelimit = Ratelimit(retry_after, 0)
                        await self._ratelimits.set_bucket(req.bucket, retry_after, 0)

                    raise HTTPException(resp, data)

                else:
                    # Probably banned by cloudflare
                    req.set_exception(HTTPException(resp, data))

            elif resp.status >= 500:
                raise HTTPException(resp, data)

            elif resp.status == 403:
                req.set_exception(HTTPForbidden(resp, data))

            elif resp.status == 404:
                req.set_exception(HTTPNotFound(resp, data))

            elif resp.status == 400:
                req.set_exception(HTTPNotFound(resp, data))

            elif resp.status in (401, 405):
                req.set_exception(HTTPException(resp, data))

            else:
                raise HTTPException(resp, data)

    async def _request_task(self, req, files=None, **kwargs):
        if files is not None:
            data = kwargs.get("data", aiohttp.FormData())
            if "json" in kwargs:
                data.add_field("payload_json", orjson.dumps(kwargs.pop("json")))

            for file in files:
                data.add_field('file', file.fp, filename=file.filename, content_type='application/octet-stream')

        last_error = None
        for i in range(req.max_tries):
            if files is not None:
                for file in files:
                    file.reset()

            try:
                await self._check_ratelimits(req)
                await self._perform_request(req, **kwargs)
                break
            except HTTPException as e:
                last_error = e
                await asyncio.sleep(i)
            except Exception as e:
                req.set_exception(e)
                break
        else:
            req.set_exception(last_error)

    def start_request(self, req, **kwargs):
        if self._session is None:
            self._session = aiohttp.ClientSession(loop=self.loop)

        req.task = self.loop.create_task(self._request_task(req, **kwargs))
        return req.task

    def get_guild(self, guild):
        req = Request("GET", "/guilds/{guild_id}",
                      converter=Guild, guild_id=entity_or_id(guild))
        self.start_request(req)
        return req

    def edit_guild(self, guild, **options):
        req = Request("PATCH", "/guilds/{guild_id}",
                      converter=Guild, guild_id=entity_or_id(guild))

        allowed_keys = ("name", "region", "verification_level", "default_message_notifications",
                        "explicit_content_filter", "afk_channel_id", "adk_timeout", "icon", "owner_id",
                        "splash", "banner", "system_channel_id", "rules_channel_id", "public_updates_channel_id",
                        "preferred_locale")
        json = make_json(options, allowed_keys)
        self.start_request(req, json=json)
        return req

    def delete_guild(self, guild):
        req = Request("DELETE", "/guilds/{guild_id}", guild_id=guild.id)
        self.start_request(req)
        return req

    def get_guild_channels(self, guild):
        def _converter(data):
            return [Channel(c) for c in data]

        req = Request("GET", "/guilds/{guild_id}/channels",
                      converter=_converter, guild_id=entity_or_id(guild))
        self.start_request(req)
        return req

    def create_guild_channel(self, guild, reason=None, **options):
        req = Request("POST", "/guilds/{guild_id}/channels",
                      converter=Channel, guild_id=entity_or_id(guild))

        allowed_keys = ("name", "type", "topic", "bitrate", "user_limit", "rate_limit_per_user", "position",
                        "permission_overwrites", "parent_id", "nsfw")
        converters = {
            # "permission_overwrites": lambda v: v  # TODO: actually convert
        }
        json = make_json(options, allowed_keys, converters)
        self.start_request(req, json=json, reason=reason)
        return req

    def get_guild_members(self, guild, after=None):
        def _converter(data):
            return [Member(m) for m in data]

        req = Request("GET", "/guilds/{guild_id}/members",
                      converter=_converter, guild_id=entity_or_id(guild))
        self.start_request(req, params={"after": entity_or_id(after)})
        return req

    def get_guild_member(self, guild, user):
        req = Request("GET", "/guilds/{guild_id}/members/{user_id}", converter=Member,
                      guild_id=entity_or_id(guild), user_id=entity_or_id(user))
        self.start_request(req)
        return req

    def edit_guild_member(self, member, **options):
        req = Request("PATCH", "/guilds/{guild_id}/members/{user_id}",
                      guild_id=member.guild_id, user_id=member.id)

        allowed_keys = ("nick", "roles", "mute", "deaf", "channel_id")
        converters = {
            "roles": lambda rs: [entity_or_id(r) for r in rs]
        }
        json = make_json(options, allowed_keys, converters)
        self.start_request(req, json=json)
        return req

    def remove_guild_member_role(self, member, role):
        req = Request("DELETE", "/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
                      guild_id=member.guild_id, user_id=member.id, role_id=entity_or_id(role))

        self.start_request(req)
        return req

    def add_guild_member_role(self, member, role):
        req = Request("PUT", "/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
                      guild_id=member.guild_id, user_id=member.id, role_id=entity_or_id(role))

        self.start_request(req)
        return req

    def remove_guild_member(self, member):
        req = Request("DELETE", "/guilds/{guild_id}/members/{user_id}",
                      guild_id=member.guild_id, user_id=member.id)

        self.start_request(req)
        return req

    def get_guild_bans(self, guild):
        req = Request("GET", "/guilds/{guild_id}/bans",
                      guild_id=entity_or_id(guild))
        self.start_request(req)
        return req

    def get_guild_ban(self, guild, user):
        req = Request("GET", "/guilds/{guild_id}/bans/{user_id}",
                      guild_id=entity_or_id(guild), user_id=entity_or_id(user))

        self.start_request(req)
        return req

    def create_guild_ban(self, guild, user, **options):
        req = Request("PUT", "/guilds/{guild_id}/bans/{user_id}",
                      guild_id=entity_or_id(guild), user_id=entity_or_id(user))

        allowed_keys = ("delete_message_days", "reason")
        json = make_json(options, allowed_keys)
        self.start_request(req, json=json)
        return req

    def remove_guild_ban(self, guild, user):
        req = Request("DELETE", "/guilds/{guild_id}/bans/{user_id}",
                      guild_id=entity_or_id(guild), user_id=entity_or_id(user))

        self.start_request(req)
        return req

    def get_guild_roles(self, guild):
        def _converter(data):
            return [Role(r) for r in data]

        req = Request("GET", "/guilds/{guild_id}/roles", converter=_converter, guild_id=entity_or_id(guild))
        self.start_request(req)
        return req

    def get_guild_role(self, guild, role):
        req = Request("GET", "/guilds/{guild_id}/roles/{role_id}", converter=Role,
                      guild_id=entity_or_id(guild), role_id=entity_or_id(role))
        self.start_request(req)
        return req

    def create_guild_role(self, guild, reason=None, **options):
        req = Request("POST", "/guilds/{guild_id}/roles", converter=Role,
                      guild_id=entity_or_id(guild))

        allowed_keys = ("name", "permissions", "color", "hoist", "mentionable")
        json = make_json(options, allowed_keys)
        self.start_request(req, json=json, reason=reason)
        return req

    def edit_guild_role(self, guild, role, reason=None, **options):
        req = Request("PATCH", "/guilds/{guild_id}/roles/{role_id}", converter=Role,
                      guild_id=entity_or_id(guild), role_id=entity_or_id(role))

        allowed_keys = ("name", "permissions", "color", "hoist", "mentionable")
        json = make_json(options, allowed_keys)
        self.start_request(req, json=json, reason=reason)
        return req

    def delete_guild_role(self, guild, role, reason=None):
        req = Request("DELETE", "/guilds/{guild_id}/roles/{role_id}",
                      guild_id=entity_or_id(guild), role_id=entity_or_id(role))
        self.start_request(req, reason=reason)
        return req

    def get_guild_invites(self):
        pass

    def get_channel(self, channel):
        req = Request("GET", "/channels/{channel_id}",
                      converter=Channel, channel_id=entity_or_id(channel))
        self.start_request(req)
        return req

    def edit_channel(self, channel, reason=None, **options):
        req = Request("PATCH", "/channels/{channel_id}",
                      converter=Channel, channel_id=entity_or_id(channel))

        allowed_keys = ("name", "type", "topic", "bitrate", "user_limit", "rate_limit_per_user", "position",
                        "permission_overwrites", "parent_id", "nsfw")
        converters = {
            # "permission_overwrites": lambda v: v  # TODO: actually convert
        }
        json = make_json(options, allowed_keys, converters)
        self.start_request(req, json=json, reason=reason)
        return req

    def edit_channel_permissions(self):
        pass

    def delete_channel_permission(self):
        pass

    def delete_channel(self, channel, reason=None):
        req = Request("DELETE", "/channels/{channel_id}",
                      channel_id=entity_or_id(channel))
        self.start_request(req, reason=reason)
        return req

    def get_channel_invites(self):
        pass

    def create_channel_invite(self):
        pass

    def get_channel_messages(self):
        pass

    def get_pinned_channel_messages(self):
        pass

    def get_channel_message(self):
        pass

    def create_message(self):
        pass

    def edit_message(self):
        pass

    def pin_message(self):
        pass

    def unpin_message(self):
        pass

    def delete_message(self):
        pass

    def bulk_delete_messages(self):
        pass

    def get_reactions(self):
        pass

    def create_reaction(self, message, emoji):
        req = Request("PUT", "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
                      channel_id=message.channel_id, message_id=message.id, emoji=emoji)
        self.start_request(req)
        return req

    def delete_own_reaction(self, message, emoji):
        req = Request("DELETE", "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
                      channel_id=message.channel_id, message_id=message.id, emoji=emoji)
        self.start_request(req)
        return req

    def delete_user_reaction(self, message, emoji, user):
        req = Request("DELETE", "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}",
                      channel_id=message.channel_id, message_id=message.id, emoji=emoji, user_id=entity_or_id(user))
        self.start_request(req)
        return req

    def delete_all_reactions(self, message):
        req = Request("DELETE", "/channels/{channel_id}/messages/{message_id}/reactions",
                      channel_id=message.channel_id, message_id=message.id)
        self.start_request(req)
        return req

    def get_user(self):
        pass

    def get_me(self):
        req = Request("GET", "/users/@me", converter=User)
        self.start_request(req)
        return req

    def leave_guild(self, guild):
        req = Request("DELETE", "/users/@me/guilds/{guild_id}", guild_id=entity_or_id(guild))
        self.start_request(req)
        return req

    def edit_me(self):
        pass

    def create_dm(self):
        pass

    def create_webhook(self):
        pass

    def execute_webhook(self):
        pass

    def edit_webhook(self):
        pass

    def delete_webhook(self):
        pass

    def get_app_info(self):
        req = Request("GET", "/oauth2/applications/@me")
        self.start_request(req)
        return req

    def get_template(self, template_id):
        req = Request("GET", "/guilds/templates/{template_id}", template_id=template_id)
        self.start_request(req)
        return req
