"""Projection from additive upstream envelopes into wrapper-owned DTOs."""

from typing import Any, cast

from .links import browse_url, image_url, page_uri
from .models import BrowseToolResult, ImageSourceDTO, SearchHit, SearchToolResult, WarningDTO


def warnings(value: Any) -> list[WarningDTO]:
    return [
        WarningDTO(code=str(x.get("code", "warning")), message=str(x.get("message", "")))
        for x in value or []
        if isinstance(x, dict)
    ]


def search_result(
    body: dict[str, Any], query: str, mode: str, base: str, cap: int
) -> SearchToolResult:
    hits: list[SearchHit] = []
    for item in body.get("results", [])[:cap]:
        if not isinstance(item, dict):
            continue
        locator = (
            cast(dict[str, Any], item.get("locator"))
            if isinstance(item.get("locator"), dict)
            else {}
        )
        metadata = (
            cast(dict[str, Any], item.get("metadata"))
            if isinstance(item.get("metadata"), dict)
            else {}
        )
        uid, sys_id = item.get("uid"), locator.get("sys_id")
        resource = (
            page_uri(str(sys_id), str(uid))
            if isinstance(uid, str) and isinstance(sys_id, str)
            else None
        )
        hits.append(
            SearchHit(
                uid=uid if isinstance(uid, str) else None,
                sys_id=sys_id if isinstance(sys_id, str) else None,
                volume_ie=locator.get("volume_ie"),
                p_num=locator.get("p_num"),
                fl_id=locator.get("fl_id"),
                shelfmark=item.get("shelfmark"),
                title=item.get("title"),
                library_code=metadata.get("library"),
                library_name=metadata.get("library_name"),
                domains=metadata.get("domains") or [],
                score=item.get("score"),
                snippet=item.get("snippet"),
                excerpt=item.get("excerpt"),
                is_synthetic=bool(item.get("is_synthetic", False)),
                image_url=image_url(base, item.get("image_url")),
                browse_url=browse_url(base, str(sys_id), str(uid)) if sys_id else None,
                resource_uri=resource,
            )
        )
    return SearchToolResult(
        upstream_schema_version=body.get("schema_version"),
        source=str(body.get("source", "search")),
        generated_at=body.get("generated_at"),
        query=query,
        search_mode=mode,
        returned_count=len(hits),
        upstream_total=body.get("total"),
        warnings=warnings(body.get("warnings")),
        results=hits,
    )


def browse_result(body: dict[str, Any], base: str) -> BrowseToolResult:
    locator = (
        cast(dict[str, Any], body.get("locator")) if isinstance(body.get("locator"), dict) else {}
    )
    image = cast(dict[str, Any], body.get("image")) if isinstance(body.get("image"), dict) else {}
    source, text = str(body.get("text_source", "none")), str(body.get("text", ""))
    notice = None
    if source == "snippet":
        notice = f"Full text unavailable; evidence is based on a snippet of {len(text)} characters."
    elif source == "none":
        notice = "No transcription text is available for this page."
    elif source != "pgp_transcription":
        notice = "The transcription source is not recognized; treat this text conservatively."
    uid, sys_id = locator.get("uid"), str(locator.get("sys_id", ""))
    resource = page_uri(sys_id, uid) if isinstance(uid, str) else None
    metadata = (
        cast(dict[str, Any], body.get("metadata")) if isinstance(body.get("metadata"), dict) else {}
    )
    return BrowseToolResult(
        upstream_schema_version=body.get("schema_version"),
        source=str(body.get("source", "browse")),
        generated_at=body.get("generated_at"),
        uid=uid if isinstance(uid, str) else None,
        sys_id=sys_id,
        volume_ie=locator.get("volume_ie"),
        p_num=locator.get("p_num"),
        fl_id=locator.get("fl_id"),
        shelfmark=body.get("shelfmark"),
        title=body.get("title"),
        library_code=body.get("library_code"),
        library_name=body.get("library_name"),
        text=text,
        text_source=source,
        text_truncated=bool(body.get("text_truncated", False)),
        metadata=metadata,
        image_url=image_url(base, image.get("url")),
        image_provider=image.get("provider"),
        image_sources=[ImageSourceDTO(name=str(x)) for x in image.get("sources", [])],
        warnings=warnings(body.get("warnings")),
        evidence_notice=notice,
        browse_url=browse_url(base, sys_id, uid if isinstance(uid, str) else None),
        resource_uri=resource,
    )
