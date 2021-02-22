import json

from ..errors import XenonException


__all__ = (
    "HTTPException",
    "HTTPNotFound",
    "HTTPForbidden",
    "HTTPBadRequest",
    "HTTPTooManyRequests",
    "HTTPUnauthorized"
)


class HTTPException(XenonException):
    def __init__(self, status, message):
        self.status = status
        if isinstance(message, dict):
            self.code = message.get("code", 0)
            base = message.get("message", "")
            errors = message.get("errors")
            if errors is not None:
                self.text = f"{base}\n{json.dumps(errors)}"

            else:
                self.text = base

        else:
            self.text = message
            self.code = 0

        fmt = '{0.status} (error code: {1}): {2}'
        super().__init__(fmt.format(self, self.code, self.text))


class HTTPBadRequest(HTTPException):
    def __init__(self, message):
        super().__init__(400, message)


class HTTPUnauthorized(HTTPException):
    def __init__(self, message):
        super().__init__(401, message)


class HTTPForbidden(HTTPException):
    def __init__(self, message):
        super().__init__(403, message)


class HTTPNotFound(HTTPException):
    def __init__(self, message):
        super().__init__(404, message)


class HTTPTooManyRequests(HTTPException):
    def __init__(self, message):
        super().__init__(429, message)
