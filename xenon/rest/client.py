import asyncio
import orjson
from urllib.parse import quote as urlquote
import aiohttp

from entities import *
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

    def __init__(self, method, path, max_tries=5, **params):
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

    @property
    def bucket(self):
        if self._webhook_id is not None:
            return self._webhook_id

        else:
            return '{0._channel_id}:{0._guild_id}:{0.path}'.format(self)

    def cancel(self):
        self.task.cancel()

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

    async def _perform_request(self, req, converter=None, **kwargs):
        headers = {
            "User-Agent": "",
            "Authorization": f"Bot {self._token}"
        }

        if "json" in kwargs:
            headers["Content-Type"] = "application/json"
            kwargs["data"] = orjson.dumps(kwargs.pop("json"))

        if "reason" in kwargs:
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
                    req.ratelimit = Ratelimit(reset_after, remaining)
                    await self._ratelimits.set_bucket(req.bucket, reset_after, remaining)

                if converter is not None:
                    req.future.set_result(converter(data))

                else:
                    req.future.set_result(data)

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
                    req.future.set_exception(HTTPException(resp, data))

            elif resp.status >= 500:
                raise HTTPException(resp, data)

            elif resp.status == 403:
                req.future.set_exception(HTTPForbidden(resp, data))

            elif resp.status == 404:
                req.future.set_exception(HTTPNotFound(resp, data))

            elif resp.status == 400:
                req.future.set_exception(HTTPNotFound(resp, data))

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

            await self._check_ratelimits(req)
            try:
                await self._perform_request(req, **kwargs)
                break
            except HTTPException as e:
                last_error = e
                await asyncio.sleep(i)
            except Exception as e:
                req.future.set_exception(e)
                break
        else:
            req.future.set_exception(last_error)

    def start_request(self, req, **kwargs):
        if self._session is None:
            self._session = aiohttp.ClientSession(loop=self.loop)

        req.task = self.loop.create_task(self._request_task(req, **kwargs))
        return req.task

    def get_guild(self, guild_id):
        req = Request("GET", "/guilds/{guild_id}", guild_id=guild_id)
        self.start_request(req)
        return req
