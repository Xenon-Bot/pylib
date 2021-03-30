import asyncio
import orjson
from urllib.parse import quote as urlquote
import aiohttp
from enum import Enum

from ..entities import *
from ..flags import *
from .errors import *

__all__ = (
    "Route",
    "HTTPClient",
    "File",
    "BucketValues"
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
        self.fp.seek(0)

    def close(self):
        self.fp.close = self._closer
        self._closer()


class BucketValues:
    def __init__(self, delta, remaining=None, is_global=False):
        self.delta = delta
        self.remaining = remaining
        self.is_global = is_global

    def __str__(self):
        return f"{'global' if self.is_global else ''} {self.remaining} {self.delta}"

    async def wait(self):
        if self.remaining == 0:
            await asyncio.sleep(self.delta)


class Route:
    BASE = 'https://discord.com/api/v8'

    def __init__(self, method, path, **params):
        self.method = method
        self.path = path.strip("/")

        self.url = f"{self.BASE}/{self.path}".format(**{k: urlquote(str(v)) for k, v in params.items()})

        self._channel_id = params.get("channel_id")
        self._guild_id = params.get("guild_id")
        self._webhook_id = params.get("webhook_id")

    @property
    def bucket(self):
        if self._webhook_id is not None:
            return self._webhook_id

        else:
            return '{0._channel_id}:{0._guild_id}:{0.path}'.format(self)


class RouteMixin:
    application_id: str

    async def request(self, *args, **kwargs):
        # Must be overwritten by the deriving client
        pass

    def get_guild(self, guild):
        return self.request(
            Route("GET", "/guilds/{guild_id}", guild_id=entity_or_id(guild)),
            converter=Guild
        )

    def edit_guild(self, guild, **options):
        allowed_keys = ("name", "region", "verification_level", "default_message_notifications",
                        "explicit_content_filter", "afk_channel_id", "adk_timeout", "icon", "owner_id",
                        "splash", "banner", "system_channel_id", "rules_channel_id", "public_updates_channel_id",
                        "preferred_locale")

        return self.request(
            Route("PATCH", "/guilds/{guild_id}", guild_id=entity_or_id(guild)),
            converter=Guild,
            json=make_json(options, allowed_keys)
        )

    def delete_guild(self, guild):
        return self.request(Route("DELETE", "/guilds/{guild_id}", guild_id=guild.id))

    def get_guild_channels(self, guild):
        def _converter(data):
            return [Channel(c) for c in data]

        return self.request(
            Route("GET", "/guilds/{guild_id}/channels", guild_id=entity_or_id(guild)),
            converter=_converter
        )

    def create_guild_channel(self, guild, reason=None, **options):
        allowed_keys = ("name", "type", "topic", "bitrate", "user_limit", "rate_limit_per_user", "position",
                        "permission_overwrites", "parent_id", "nsfw")
        converters = {
            # "permission_overwrites": lambda v: v  # TODO: actually convert
        }
        return self.request(
            Route("POST", "/guilds/{guild_id}/channels", guild_id=entity_or_id(guild)),
            converter=Channel,
            json=make_json(options, allowed_keys, converters),
            reason=reason
        )

    def get_guild_members(self, guild, after=None, limit=1000):
        def _converter(data):
            return [Member(m) for m in data]

        params = {"limit": str(limit)}
        if after is not None:
            params["after"] = entity_or_id(after)

        return self.request(
            Route("GET", "/guilds/{guild_id}/members", guild_id=entity_or_id(guild)),
            converter=_converter,
            params=params
        )

    def get_guild_member(self, guild, user):
        return self.request(
            Route("GET", "/guilds/{guild_id}/members/{user_id}",
                  guild_id=entity_or_id(guild), user_id=entity_or_id(user)),
            converter=Member
        )

    def edit_guild_member(self, guild, user, **options):
        allowed_keys = ("nick", "roles", "mute", "deaf", "channel_id")
        converters = {
            "roles": lambda rs: [entity_or_id(r) for r in rs]
        }
        json = make_json(options, allowed_keys, converters)
        return self.request(
            Route("GET", "/guilds/{guild_id}/members/{user_id}",
                  guild_id=entity_or_id(guild), user_id=entity_or_id(user)),
            json=json
        )

    def remove_guild_member_role(self, guild, user, role):
        return self.request(
            Route("DELETE", "/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
                  guild_id=entity_or_id(guild), user_id=entity_or_id(user), role_id=entity_or_id(role))
        )

    def add_guild_member_role(self, guild, user, role):
        return self.request(
            Route("PUT", "/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
                  guild_id=entity_or_id(guild), user_id=entity_or_id(user), role_id=entity_or_id(role))
        )

    def remove_guild_member(self, guild, user):
        return self.request(
            Route("DELETE", "/guilds/{guild_id}/members/{user_id}",
                  guild_id=entity_or_id(guild), user_id=entity_or_id(user)),
        )

    def get_guild_bans(self, guild):
        # TODO: converter
        return self.request(
            Route("GET", "/guilds/{guild_id}/bans", guild_id=entity_or_id(guild))
        )

    def get_guild_ban(self, guild, user):
        # TODO: converter
        return self.request(
            Route("GET", "/guilds/{guild_id}/bans/{user_id}",
                  guild_id=entity_or_id(guild), user_id=entity_or_id(user))
        )

    def create_guild_ban(self, guild, user, **options):
        allowed_keys = ("delete_message_days", "reason")
        return self.request(
            Route("PUT", "/guilds/{guild_id}/bans/{user_id}",
                  guild_id=entity_or_id(guild), user_id=entity_or_id(user)),
            json=make_json(options, allowed_keys)
        )

    def remove_guild_ban(self, guild, user):
        return self.request(
            Route("PUT", "/guilds/{guild_id}/bans/{user_id}",
                  guild_id=entity_or_id(guild), user_id=entity_or_id(user))
        )

    def get_guild_roles(self, guild):
        def _converter(data):
            return [Role(r) for r in data]

        return self.request(
            Route("GET", "/guilds/{guild_id}/roles", guild_id=entity_or_id(guild)),
            converter=_converter
        )

    def get_guild_role(self, guild, role):
        return self.request(
            Route("GET", "/guilds/{guild_id}/roles/{role_id}",
                  guild_id=entity_or_id(guild), role_id=entity_or_id(role)),
            converter=Role
        )

    def create_guild_role(self, guild, reason=None, **options):
        allowed_keys = ("name", "permissions", "color", "hoist", "mentionable")
        return self.request(
            Route("POST", "/guilds/{guild_id}/roles", guild_id=entity_or_id(guild)),
            converter=Role,
            json=make_json(options, allowed_keys),
            reason=reason
        )

    def edit_guild_role(self, guild, role, reason=None, **options):
        allowed_keys = ("name", "permissions", "color", "hoist", "mentionable")
        json = make_json(options, allowed_keys)
        return self.request(
            Route("PATCH", "/guilds/{guild_id}/roles/{role_id}",
                  guild_id=entity_or_id(guild), role_id=entity_or_id(role)),
            converter=Role,
            json=json,
            reason=reason
        )

    def delete_guild_role(self, guild, role, reason=None):
        return self.request(
            Route("DELETE", "/guilds/{guild_id}/roles/{role_id}",
                  guild_id=entity_or_id(guild), role_id=entity_or_id(role)),
            reason=reason
        )

    def get_guild_invites(self):
        pass

    def get_channel(self, channel):
        return self.request(
            Route("GET", "/channels/{channel_id}", channel_id=entity_or_id(channel)),
            converter=Channel
        )

    def edit_channel(self, channel, reason=None, **options):
        allowed_keys = ("name", "type", "topic", "bitrate", "user_limit", "rate_limit_per_user", "position",
                        "permission_overwrites", "parent_id", "nsfw")
        converters = {
            # "permission_overwrites": lambda v: v  # TODO: actually convert
        }
        return self.request(
            Route("PATCH", "/channels/{channel_id}", channel_id=entity_or_id(channel)),
            converter=Channel,
            json=make_json(options, allowed_keys, converters),
            reason=reason
        )

    def edit_channel_permissions(self):
        pass

    def delete_channel_permission(self):
        pass

    def delete_channel(self, channel, reason=None):
        return self.request(
            Route("DELETE", "/channels/{channel_id}", channel_id=entity_or_id(channel)),
            reason=reason
        )

    def get_channel_invites(self):
        pass

    def create_channel_invite(self):
        pass

    def get_channel_messages(self, channel, limit=100, before=None):
        def _converter(data):
            return [Message(m) for m in data]

        params = {"limit": str(limit)}
        if before is not None:
            params["before"] = entity_or_id(before)

        return self.request(
            Route("GET", "/channels/{channel_id}/messages", channel_id=entity_or_id(channel)),
            converter=_converter,
            params=params
        )

    def get_pinned_channel_messages(self, channel):
        def _converter(data):
            return [Message(m) for m in data]

        return self.request(
            Route("GET", "/channels/{channel_id}/pins", channel_id=entity_or_id(channel)),
            converter=_converter
        )

    def get_channel_message(self, channel, message):
        return self.request(
            Route("GET", "/channels/{channel_id}/messages/{message_id}",
                  channel_id=entity_or_id(channel), message_id=entity_or_id(message)),
            converter=Message
        )

    def create_message(self, channel, content=None, **kwargs):
        return self.request(
            Route("POST", "/channels/{channel_id}/messages", channel_id=entity_or_id(channel)),
            json={"content": content, **kwargs},
            converter=Message
        )

    def edit_message(self, channel, message, content, **kwargs):
        return self.request(
            Route("PATCH", "/channels/{channel_id}/messages/{message_id}",
                  channel_id=entity_or_id(channel), message_id=entity_or_id(message)),
            converter=Message
        )

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

    def create_reaction(self, channel, message, emoji):
        return self.request(Route("PUT", "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
                                  channel_id=entity_or_id(channel), message_id=entity_or_id(message), emoji=emoji))

    def delete_own_reaction(self, channel, message, emoji):
        return self.request(Route("DELETE", "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
                                  channel_id=entity_or_id(channel), message_id=entity_or_id(message), emoji=emoji))

    def delete_user_reaction(self, channel, message, emoji, user):
        return self.request(Route("DELETE", "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}",
                                  channel_id=entity_or_id(channel), message_id=entity_or_id(message), emoji=emoji,
                                  user_id=entity_or_id(user)))

    def delete_all_reactions(self, message):
        return self.request(
            Route("DELETE", "/channels/{channel_id}/messages/{message_id}/reactions",
                  channel_id=message.channel_id, message_id=message.id)
        )

    def get_user(self, user):
        return self.request(
            Route("GET", "/users/{user_id}", user_id=entity_or_id(user), converter=User)
        )

    def get_me(self):
        return self.request(
            Route("GET", "/users/@me", converter=User)
        )

    def leave_guild(self, guild):
        return self.request(
            Route("DELETE", "/users/@me/guilds/{guild_id}", guild_id=entity_or_id(guild))
        )

    def edit_me(self):
        pass

    def create_dm(self):
        pass

    def get_channel_webhooks(self, channel):
        def _converter(data):
            return [Webhook(r) for r in data]

        return self.request(
            Route("GET", "/channels/{channel_id}/webhooks", channel_id=entity_or_id(channel)),
            converter=_converter
        )

    def get_guild_webhooks(self, guild):
        def _converter(data):
            return [Webhook(r) for r in data]

        return self.request(
            Route("GET", "/guilds/{guild_id}/webhooks", guild_id=entity_or_id(guild)),
            converter=_converter
        )

    def create_webhook(self, channel, reason=None, **options):
        return self.request(
            Route("POST", "/channels/{channel_id}/webhooks",
                  channel_id=entity_or_id(channel)),
            json=make_json(options, ("name", "avatar")),
            converter=Webhook
        )

    def create_webhook_message(self, webhook, wait=False, **options):
        return self.request(
            Route("POST", "/webhooks/{webhook_id}/{webhook_token}",
                  webhook_id=webhook.id, webhook_token=webhook.token),
            json=make_json(options),
            params={"wait": "true" if wait else "false"},
            converter=Message if wait else None
        )

    def edit_webhook_message(self, webhook, message, **options):
        pass

    def delete_webhook_message(self, webhook, message):
        pass

    def edit_webhook(self):
        pass

    def delete_webhook(self):
        pass

    def get_application(self):
        return self.request(
            Route("GET", "/oauth2/applications/@me")
        )

    def get_template(self, template_id):
        return self.request(
            Route("GET", "/guilds/templates/{template_id}", template_id=template_id)
        )

    def get_global_commands(self):
        return self.request(
            Route("GET", "/applications/{application_id}/commands", application_id=self.application_id)
        )

    def get_guild_commands(self, guild):
        return self.request(
            Route("GET", "/applications/{application_id}/guilds/{guild_id}/commands",
                  application_id=self.application_id, guild_id=entity_or_id(guild))
        )

    def get_global_command(self, command):
        return self.request(
            Route("GET", "/applications/{application_id}/commands/{command_id}",
                  application_id=self.application_id, command_id=entity_or_id(command))
        )

    def get_guild_command(self, guild, command):
        return self.request(
            Route("GET", "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}",
                  application_id=self.application_id, guild_id=entity_or_id(guild),
                  command_id=entity_or_id(command))
        )

    def create_global_command(self, data):
        return self.request(
            Route("POST", "/applications/{application_id}/commands",
                  application_id=self.application_id),
            json=data
        )

    def create_guild_command(self, guild, data):
        return self.request(
            Route("POST", "/applications/{application_id}/guilds/{guild_id}/commands",
                  application_id=self.application_id, guild_id=entity_or_id(guild)),
            json=data
        )

    def edit_global_command(self, command, data):
        return self.request(
            Route("PATCH", "/applications/{application_id}/commands/{command_id}",
                  application_id=self.application_id, command_id=entity_or_id(command)),
            json=data
        )

    def edit_guild_command(self, guild, command, data):
        return self.request(
            Route("PATCH", "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}",
                  application_id=self.application_id, guild_id=entity_or_id(guild), command_id=entity_or_id(command)),
            json=data
        )

    def delete_global_command(self, command):
        return self.request(
            Route("DELETE", "/applications/{application_id}/commands/{command_id}",
                  application_id=self.application_id, command_id=entity_or_id(command))
        )

    def delete_guild_command(self, guild, command):
        return self.request(
            Route("DELETE", "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}",
                  application_id=self.application_id, guild_id=entity_or_id(guild), command_id=entity_or_id(command))
        )

    def replace_global_commands(self, data):
        return self.request(
            Route("PUT", "/applications/{application_id}/commands", application_id=self.application_id),
            json=data
        )

    def replace_guild_commands(self, guild, data):
        return self.request(
            Route("PUT", "/applications/{application_id}/guilds/{guild_id}/commands",
                  application_id=self.application_id, guild_id=entity_or_id(guild)),
            json=data
        )

    def create_interaction_response(self, interaction_token, **options):
        return self.request(
            Route("POST", "/webhooks/{application_id}/{webhook_token}",
                  application_id=self.application_id, webhook_token=interaction_token),
            json=make_json(options),
            converter=Message
        )

    def edit_interaction_response(self, interaction_token, message="@original", **options):
        return self.request(
            Route("PATCH", "/webhooks/{application_id}/{webhook_token}/messages/{message_id}",
                  application_id=self.application_id, webhook_token=interaction_token,
                  message_id=entity_or_id(message)),
            json=make_json(options),
            converter=Message
        )

    def delete_interaction_response(self, interaction_token, message="@original"):
        return self.request(
            Route("DELETE", "/webhooks/{application_id}/{webhook_token}/messages/{message_id}",
                  application_id=self.application_id, webhook_token=interaction_token,
                  message_id=entity_or_id(message))
        )

    def get_interaction_response(self, interaction_token, message="@original"):
        # We currently have to use PATCH because discord didn't add a GET endpoint yet
        return self.request(
            Route("PATCH", "/webhooks/{application_id}/{webhook_token}/messages/{message_id}",
                  application_id=self.application_id, webhook_token=interaction_token,
                  message_id=entity_or_id(message)),
            json={},
            converter=Message
        )


class HTTPClient(RouteMixin):
    def __init__(self, token, redis, **kwargs):
        self._token = token
        self._redis = redis
        self._session = kwargs.get("session")
        self.loop = kwargs.get("loop", asyncio.get_event_loop())
        self.application_id = kwargs.get("application_id")

        self.max_retries = kwargs.get("max_retries", 5)
        self.semaphore = None
        self.semaphore = asyncio.Semaphore(kwargs.get("max_concurrency", 50))

    async def get_bucket(self, bucket):
        delta = await self._redis.pttl(f"ratelimits:{bucket}")
        if delta <= 0:
            return None

        remaining = await self._redis.get(f"ratelimits:{bucket}")
        if remaining is None:
            return None

        return BucketValues(delta / 1000, int(remaining))

    async def set_bucket(self, bucket, remaining, delta):
        await self._redis.setex(f"ratelimits:{bucket}", delta, remaining)

    async def set_global(self, delta):
        await self._redis.setex("ratelimits:global", delta, 0)

    async def get_global(self, delta):
        delta = await self._redis.pttl("ratelimits:global")
        if delta < 0:
            return None

        return BucketValues(delta / 1000, remaining=0, is_global=True)

    async def _perform_request(self, route, **kwargs):
        headers = {
            "User-Agent": "",
            "Authorization": f"Bot {self._token}"
        }

        if "json" in kwargs:
            data = kwargs.pop("json")
            if data is not None:
                headers["Content-Type"] = "application/json"
                kwargs["data"] = orjson.dumps(data)

        if "reason" in kwargs:
            headers["X-Audit-Log-Reason"] = urlquote(kwargs.pop("reason") or "", safe="/ ")

        async with self._session.request(
                method=route.method,
                url=route.url,
                headers=headers,
                raise_for_status=False,
                **kwargs
        ) as resp:
            data = await json_or_text(resp)

            if 300 > resp.status >= 200:
                remaining = resp.headers.get('X-Ratelimit-Remaining')
                reset_after = resp.headers.get('X-Ratelimit-Reset-After')
                if remaining is not None and reset_after is not None:
                    await self.set_bucket(route.bucket, int(remaining), float(reset_after))

                return data

            elif resp.status == 429:
                if resp.headers.get('Via'):
                    retry_after = data['retry_after']
                    is_global = data.get('global', False)
                    if is_global:
                        await self.set_global(retry_after)

                    else:
                        await self.set_bucket(route.bucket, 0, retry_after)

                else:
                    # Most likely cloudflare banned
                    await self.set_global(1)

            raise HTTPException(resp.status, data)

    async def request(self, route, converter=None, wait=True, files=None, **kwargs):
        if self._session is None:
            self._session = aiohttp.ClientSession(loop=self.loop)

        if files is not None:
            data = kwargs.get("data", aiohttp.FormData())
            if "json" in kwargs:
                data.add_field("payload_json", orjson.dumps(kwargs.pop("json")).decode("utf-8"))

            for file in files:
                data.add_field('file', file.fp, filename=file.filename, content_type='application/octet-stream')

            kwargs["data"] = data

        for i in range(self.max_retries):
            try:
                if files is not None:
                    for file in files:
                        file.reset()

                ratelimit = await self.get_bucket(route.bucket)
                if ratelimit:
                    if wait:
                        await ratelimit.wait()

                    else:
                        raise HTTPTooManyRequests("Bucket depleted")

                await self.semaphore.acquire()
                try:
                    result = await self._perform_request(route, **kwargs)
                finally:
                    self.semaphore.release()

                if converter:
                    return converter(result)

                return result
            except HTTPException as e:
                if e.status == 400:
                    raise HTTPBadRequest(e.text)

                elif e.status == 401:
                    raise HTTPUnauthorized(e.text)

                elif e.status == 403:
                    raise HTTPForbidden(e.text)

                elif e.status == 404:
                    raise HTTPNotFound(e.text)

                elif e.status == 429 and not wait:
                    raise HTTPTooManyRequests(e.text)

                elif i == self.max_retries - 1:
                    raise e

                else:
                    await asyncio.sleep(i)
