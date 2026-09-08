import os

import pytest

from genizah_mcp.client import GenizahClient
from genizah_mcp.config import Settings

pytestmark = pytest.mark.live


@pytest.mark.asyncio
async def test_live_search_contract() -> None:
    if os.getenv("GENIZAH_RUN_LIVE_TESTS") != "1":
        pytest.skip("set GENIZAH_RUN_LIVE_TESTS=1 to run public API smoke tests")
    client = GenizahClient(Settings())
    try:
        body = await client.search({"query": "ויאמר", "search_mode": "exact", "limit": 1})
        assert isinstance(body.get("results"), list)
        if body["results"]:
            hit = body["results"][0]
            locator = hit.get("locator", {})
            if hit.get("uid") and locator.get("sys_id"):
                page = await client.browse({"sys_id": locator["sys_id"], "uid": hit["uid"]})
                assert isinstance(page.get("locator"), dict)
        parallels = await client.parallels({"text": "ויאמר משה", "chunk_size": 2, "mode": "exact"})
        assert isinstance(parallels.get("results"), list)
    finally:
        await client.aclose()
