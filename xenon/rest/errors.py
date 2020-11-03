import json

from ..errors import XenonException


__all__ = (
    "HTTPException",
    "HTTPNotFound",
    "HTTPForbidden",
    "HTTPBadRequest"
)


class HTTPException(XenonException):
    def __init__(self, resp, message):
        self.response = resp
        self.status = resp.status
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

        fmt = '{0.status} {0.reason} (error code: {1}): {2}'
        super().__init__(fmt.format(self.response, self.code, self.text))


class HTTPBadRequest(HTTPException):
    pass


class HTTPForbidden(HTTPException):
    pass


class HTTPNotFound(HTTPException):
    pass
