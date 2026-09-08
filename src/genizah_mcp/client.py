"""Allowlisted, pooled HTTPS client for documented public API endpoints only."""

import logging
from typing import Any, Literal

import httpx

from .config import Settings
from .errors import GenizahAPIError
from .throttle import TokenBucket

LOGGER = logging.getLogger(__name__)
Endpoint = Literal["search", "browse", "parallels"]
PATHS: dict[Endpoint, str] = {
    "search": "/api/search",
    "browse": "/api/browse",
    "parallels": "/api/parallels",
}


class GenizahClient:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self.settings = settings
        self.client = client or httpx.AsyncClient(
            base_url=settings.api_base,
            follow_redirects=False,
            headers={"User-Agent": "GenizahSearch-MCP-PoC/0.1", "Accept": "application/json"},
            timeout=httpx.Timeout(settings.search_timeout, connect=settings.connect_timeout),
        )
        self._owned_client = client is None
        self.buckets = {name: TokenBucket(settings.rpm, settings.burst) for name in PATHS}

    async def aclose(self) -> None:
        if self._owned_client:
            await self.client.aclose()

    async def _call(
        self,
        endpoint: Endpoint,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        await self.buckets[endpoint].acquire()
        timeout = {
            "search": self.settings.search_timeout,
            "browse": self.settings.browse_timeout,
            "parallels": self.settings.parallels_timeout,
        }[endpoint]
        try:
            response = await self.client.request(
                "GET" if endpoint == "browse" else "POST",
                PATHS[endpoint],
                json=json,
                params=params,
                timeout=httpx.Timeout(timeout, connect=self.settings.connect_timeout),
            )
        except httpx.TimeoutException as exc:
            raise GenizahAPIError(
                "upstream_timeout", "The upstream service timed out.", retriable=True
            ) from exc
        except httpx.RequestError as exc:
            raise GenizahAPIError(
                "upstream_unavailable", "The upstream service is unavailable.", retriable=True
            ) from exc
        try:
            body = response.json()
        except ValueError as exc:
            raise GenizahAPIError(
                "invalid_upstream_response", "The upstream service returned invalid JSON."
            ) from exc
        if not isinstance(body, dict):
            raise GenizahAPIError(
                "invalid_upstream_response", "The upstream service returned an invalid envelope."
            )
        error = body.get("error")
        if response.is_error or isinstance(error, dict):
            code = (
                str(error.get("code", "upstream_error"))
                if isinstance(error, dict)
                else "upstream_error"
            )
            message = (
                str(error.get("message", "The upstream service rejected the request."))
                if isinstance(error, dict)
                else "The upstream service rejected the request."
            )
            retry_after = response.headers.get("Retry-After")
            seconds = int(retry_after) if retry_after and retry_after.isdigit() else None
            raise GenizahAPIError(
                code,
                message[:500],
                response.status_code,
                seconds,
                response.status_code >= 500 or response.status_code == 429,
            )
        return body

    async def search(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._call("search", json=payload)

    async def browse(self, params: dict[str, Any]) -> dict[str, Any]:
        return await self._call("browse", params=params)

    async def parallels(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._call("parallels", json=payload)

    async def doctor(self) -> dict[str, Any]:
        try:
            response = await self.client.get(
                "/api/openapi.json", timeout=self.settings.browse_timeout
            )
            document = response.json()
        except (httpx.RequestError, ValueError) as exc:
            raise GenizahAPIError(
                "upstream_unavailable", "Unable to fetch the upstream OpenAPI contract."
            ) from exc
        if not isinstance(document, dict):
            raise GenizahAPIError("invalid_upstream_response", "The OpenAPI contract is invalid.")
        return document
