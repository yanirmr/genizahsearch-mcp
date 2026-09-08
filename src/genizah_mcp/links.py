"""Trusted upstream and MCP link construction."""

import re
from urllib.parse import quote, urlencode, urljoin

from .errors import GenizahAPIError

UID_RE = re.compile(r"^IE\d+_P\d+_FL\d+$")
SYS_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")


def validate_locator(sys_id: str, uid: str) -> None:
    if not SYS_ID_RE.fullmatch(sys_id) or not UID_RE.fullmatch(uid):
        raise GenizahAPIError(
            "invalid_locator", "The page locator has an invalid public identifier."
        )


def page_uri(sys_id: str, uid: str) -> str:
    validate_locator(sys_id, uid)
    return f"genizah://page/{quote(sys_id, safe='')}/{quote(uid, safe='')}"


def browse_url(base_url: str, sys_id: str, uid: str | None = None) -> str:
    params = {"sys_id": sys_id}
    if uid:
        params["uid"] = uid
    return f"{base_url}/browse?{urlencode(params)}"


def image_url(base_url: str, value: str | None) -> str | None:
    if not value:
        return None
    return urljoin(f"{base_url}/", value)
