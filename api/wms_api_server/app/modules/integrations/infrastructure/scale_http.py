"""Bounded HTTPS gateway adapter; Basic identity belongs to a dedicated sender."""
import base64
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from ..contracts_scales import ScaleGatewayError


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req: Any, fp: Any, code: int, msg: str,
                         headers: Any, newurl: str) -> None:
        return None


class HttpScaleGateway:
    def __init__(self, origin: str, username: str, password: str, timeout: float = 5,
                 allow_loopback_http: bool = False) -> None:
        parsed = urlsplit(origin)
        loopback = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
        if (parsed.scheme != "https" and not (allow_loopback_http and loopback and parsed.scheme == "http")):
            raise ValueError("SCALE_HTTPS_REQUIRED")
        if not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in {"", "/"}:
            raise ValueError("SCALE_API_ORIGIN_INVALID")
        if not username or not password or ":" in username or any(c in username + password for c in "\r\n"):
            raise ValueError("SCALE_SENDER_IDENTITY_INVALID")
        if not 0 < timeout <= 10:
            raise ValueError("SCALE_HTTP_TIMEOUT_INVALID")
        self.origin = origin.rstrip("/")
        self.timeout = timeout
        self._authorization = "Basic " + base64.b64encode((username + ":" + password).encode("utf-8")).decode("ascii")
        self._opener = build_opener(_NoRedirect())

    def _request(self, path: str, body: bytes | None = None, protocol_version: str = "1.0") -> bytes:
        if protocol_version not in {"1.0", "1.1", "1.2"}:
            raise ScaleGatewayError("SCALE_PROTOCOL_VERSION_UNSUPPORTED")
        headers = {"Authorization": self._authorization, "Accept": "application/json", "X-Scale-Protocol-Version": protocol_version}
        if body is not None:
            headers["Content-Type"] = "application/json"
        try:
            request = Request(self.origin + path, data=body, headers=headers)
            with self._opener.open(request, timeout=self.timeout) as response:
                result = response.read(65537)
                if len(result) > 65536:
                    raise ScaleGatewayError("SCALE_HTTP_RESPONSE_TOO_LARGE")
                if response.headers.get_content_type() != "application/json":
                    raise ScaleGatewayError("SCALE_HTTP_JSON_REQUIRED")
                return result
        except HTTPError as exc:
            raise ScaleGatewayError("SCALE_HTTP_" + str(exc.code), exc.code >= 500 or exc.code in {408, 429}) from None
        except (URLError, TimeoutError, OSError):
            raise ScaleGatewayError("SCALE_HTTP_UNAVAILABLE", True) from None

    def requests(self, device_id: str) -> list[dict[str, Any]]:
        raw = self._request("/api/delivery/store-scales/gateway/requests?" + urlencode({"device_id": device_id}))
        try:
            result = json.loads(raw)
            items = result["items"]
            if not isinstance(items, list) or len(items) > 50 or any(not isinstance(item, dict) for item in items):
                raise ValueError()
            return items
        except (KeyError, TypeError, ValueError):
            raise ScaleGatewayError("SCALE_REQUEST_LIST_INVALID") from None

    def post_capture(self, body: bytes) -> bytes:
        return self._request("/api/delivery/store-scales/captures", body)
