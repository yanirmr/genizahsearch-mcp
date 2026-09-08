import os
from pathlib import Path

import pytest
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

pytestmark = pytest.mark.live
EXECUTABLE = Path(".venv/Scripts/genizah-mcp.exe").resolve()


@pytest.mark.asyncio
async def test_live_mcp_search_to_browse_round_trip() -> None:
    if os.getenv("GENIZAH_RUN_LIVE_TESTS") != "1":
        pytest.skip("set GENIZAH_RUN_LIVE_TESTS=1 to run public API smoke tests")
    params = StdioServerParameters(command=str(EXECUTABLE), args=[])
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            search = await session.call_tool(
                "search_manuscripts",
                {"input": {"query": "ויאמר", "search_mode": "exact", "limit": 1}},
            )
            assert not search.is_error
            data = search.structured_content
            assert isinstance(data, dict)
            hits = data.get("results")
            assert isinstance(hits, list)
            if hits and isinstance(hits[0], dict):
                hit = hits[0]
                if isinstance(hit.get("sys_id"), str) and isinstance(hit.get("uid"), str):
                    browse = await session.call_tool(
                        "browse_page",
                        {"input": {"sys_id": hit["sys_id"], "uid": hit["uid"]}},
                    )
                    assert not browse.is_error
                    assert isinstance(browse.structured_content, dict)
                    resource = await session.read_resource(hit["resource_uri"])
                    assert resource.contents


@pytest.mark.asyncio
async def test_live_mcp_bounded_candidate_workflow() -> None:
    if os.getenv("GENIZAH_RUN_LIVE_TESTS") != "1":
        pytest.skip("set GENIZAH_RUN_LIVE_TESTS=1 to run public API smoke tests")
    params = StdioServerParameters(command=str(EXECUTABLE), args=[])
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            merged = await session.call_tool(
                "search_multiple_phrases",
                {
                    "input": {
                        "phrases": ["ויאמר", "משה"],
                        "search_mode": "exact",
                        "limit_per_phrase": 2,
                    }
                },
            )
            assert not merged.is_error
            assert isinstance(merged.structured_content, dict)
            candidates = merged.structured_content.get("results")
            assert isinstance(candidates, list)
            assert len(candidates) <= 5
            parallels = await session.call_tool(
                "find_parallels",
                {"input": {"text": "ויאמר משה", "method": "chunk", "chunk_size": 2}},
            )
            assert not parallels.is_error
            assert isinstance(parallels.structured_content, dict)
