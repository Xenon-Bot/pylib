import asyncio
from enum import Enum
from os import environ as env
from urllib.parse import quote as urlquote

import aiohttp
import orjson

from .errors import *
from ..entities import *
from ..flags import *

__all__ = (
    "Route",
    "HTTPClient",
    "File"
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


class Route:
    BASE = env.get('DISCORD_API_URL', 'https://discord.com')

    def __init__(self, method, path, api_prefix=True, **params):
        self.method = method
        self.path = path.strip("/")

        self.full_path = self.path.format(**{k: urlquote(str(v)) for k, v in params.items()})
        self.url = f"{self.BASE}{'/api/v9' if api_prefix else ''}/{self.full_path}"

        self._channel_id = params.get("channel_id")
        self._guild_id = params.get("guild_id")
        self._webhook_id = params.get("webhook_id")


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
        return self.request(Route("DELETE", "/guilds/{guild_id}", guild_id=entity_or_id(guild)))

    def get_guild_widget(self, guild):
        return self.request(
            Route("GET", "/guilds/{guild_id}/widget.json", guild_id=entity_or_id(guild)),
            auth=""
        )

    def get_guild_preview(self, guild):
        return self.request(
            Route("GET", "/guilds/{guild_id}/preview", guild_id=entity_or_id(guild)),
        )

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
            Route("PATCH", "/guilds/{guild_id}/members/{user_id}",
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
            Route("DELETE", "/guilds/{guild_id}/bans/{user_id}",
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
            json={"content": content, **kwargs},
            converter=Message
        )

    def pin_message(self, channel, message):
        return self.request(
            Route("PUT", "/channels/{channel_id}/pins/{message_id}",
                  channel_id=entity_or_id(channel), message_id=entity_or_id(message))
        )

    def unpin_message(self, channel, message):
        return self.request(
            Route("DELETE", "/channels/{channel_id}/pins/{message_id}",
                  channel_id=entity_or_id(channel), message_id=entity_or_id(message))
        )

    def delete_message(self):
        pass

    def bulk_delete_messages(self):
        pass

    def get_reactions(self, channel, message, emoji, limit=100, after=None):
        params = {"limit": str(limit)}
        if after is not None:
            params["after"] = entity_or_id(after)

        return self.request(
            Route("GET", "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}",
                  channel_id=entity_or_id(channel), message_id=entity_or_id(message), emoji=emoji),
            converter=lambda d: [User(u) for u in d],
            params=params
        )

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
            Route("GET", "/users/{user_id}", user_id=entity_or_id(user)),
            converter=User
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

    def create_webhook_message(self, webhook, wait=False, thread_id=None, files=None, **options):
        params = {"wait": "true" if wait else "false"}
        if thread_id:
            params["thread_id"] = thread_id

        return self.request(
            Route("POST", "/webhooks/{webhook_id}/{webhook_token}",
                  webhook_id=webhook.id, webhook_token=webhook.token),
            json=make_json(options),
            files=files,
            params=params,
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

    def exchange_oauth_token(self, client_id, client_secret, redirect_uri, code):
        return self.request(
            Route("POST", "/oauth2/token"),
            auth="",
            data=make_json({
                "grant_type": "authorization_code",
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "code": code
            })
        )

    def refresh_oauth_token(self, client_id, client_secret, refresh_token):
        return self.request(
            Route("POST", "/oauth2/token"),
            auth="",
            data=make_json({
                "grant_type": "refresh_token",
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token
            })
        )

    def get_oauth_user(self, token):
        return self.request(
            Route("GET", "/users/@me"),
            auth=f"Bearer {token}",
            converter=User
        )

    def get_oauth_guilds(self, token):
        return self.request(
            Route("GET", f"/users/@me/guilds"),
            auth=f"Bearer {token}"
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

    def create_interaction_response(self, interaction_token, files=None, **options):
        return self.request(
            Route("POST", "/webhooks/{application_id}/{webhook_token}",
                  application_id=self.application_id, webhook_token=interaction_token),
            files=files,
            json=make_json(options),
            converter=Message
        )

    def edit_interaction_response(self, interaction_token, message="@original", files=None, **options):
        return self.request(
            Route("PATCH", "/webhooks/{application_id}/{webhook_token}/messages/{message_id}",
                  application_id=self.application_id, webhook_token=interaction_token,
                  message_id=entity_or_id(message)),
            files=files,
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

    def set_command_guild_permissions(self, guild, command, permissions):
        return self.request(
            Route("PUT", "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions",
                  application_id=self.application_id, guild_id=entity_or_id(guild), command_id=entity_or_id(command)),
            json={"permissions": permissions}
        )

    def get_command_guild_permissions(self, guild, command):
        return self.request(
            Route("GET", "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions",
                  application_id=self.application_id, guild_id=entity_or_id(guild), command_id=entity_or_id(command))
        )

    async def get_ratelimit_bucket(self, route: Route):
        resp = await self.request(Route("GET", "/bucket", api_prefix=False), params={
            "method": route.method.upper(),
            "path": f"/{route.full_path}"
        })
        data = orjson.loads(resp)
        if data["found"]:
            return data["bucket"]
        else:
            return None


class HTTPClient(RouteMixin):
    def __init__(self, token, **kwargs):
        self._token = token
        self._session = kwargs.get("session")
        self.application_id = kwargs.get("application_id")

        self.max_retries = kwargs.get("max_retries", 5)

    async def close(self):
        if self._session is not None:
            await self._session.close()

    async def _perform_request(self, route, **kwargs):
        headers = {
            "User-Agent": "",
            "Authorization": kwargs.pop("auth", f"Bot {self._token}")
        }

        if "json" in kwargs:
            data = kwargs.pop("json")
            if data is not None:
                headers["Content-Type"] = "application/json"
                kwargs["data"] = orjson.dumps(data)

        if "reason" in kwargs:
            headers["X-Audit-Log-Reason"] = urlquote(kwargs.pop("reason") or "", safe="/ ")

        timeout = aiohttp.ClientTimeout(total=300)
        async with self._session.request(
                method=route.method,
                url=route.url,
                headers=headers,
                raise_for_status=False,
                timeout=timeout,
                **kwargs
        ) as resp:
            data = await json_or_text(resp)

            if 300 > resp.status >= 200:
                return data

            raise HTTPException(resp.status, data)

    async def request(self, route, converter=None, files=None, **kwargs):
        if self._session is None:
            bind_to = env.get("BIND_INTERFACE")
            if bind_to is not None:
                connector = aiohttp.TCPConnector(local_addr=(bind_to, 0))
            else:
                connector = aiohttp.TCPConnector()

            self._session = aiohttp.ClientSession(connector=connector)

        for i in range(self.max_retries):
            options = kwargs.copy()

            try:
                if files is not None:
                    for file in files:
                        file.reset()

                    data = options.get("data", aiohttp.FormData())
                    if "json" in options:
                        data.add_field("payload_json", orjson.dumps(options.pop("json")).decode("utf-8"))

                    for i, file in enumerate(files):
                        data.add_field(f"file{i}", file.fp, filename=file.filename,
                                       content_type='application/octet-stream')

                    options["data"] = data

                result = await self._perform_request(route, **options)

                if converter:
                    return converter(result)

                return result
            except asyncio.TimeoutError:
                await asyncio.sleep(i)
            except HTTPException as e:
                if e.status == 400:
                    raise HTTPBadRequest(e.text)

                elif e.status == 401:
                    raise HTTPUnauthorized(e.text)

                elif e.status == 403:
                    raise HTTPForbidden(e.text)

                elif e.status == 404:
                    raise HTTPNotFound(e.text)

                elif e.status == 429:
                    await asyncio.sleep(i)

                elif e.status < 500 or i == self.max_retries - 1:
                    raise e

                else:
                    await asyncio.sleep(i)
