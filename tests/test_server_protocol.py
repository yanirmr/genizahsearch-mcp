from pathlib import Path

import pytest
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

EXECUTABLE = Path(".venv/Scripts/genizah-mcp.exe").resolve()


@pytest.mark.asyncio
async def test_stdio_initializes_and_exposes_only_public_surface() -> None:
    params = StdioServerParameters(command=str(EXECUTABLE), args=[])
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            prompts = await session.list_prompts()
            templates = await session.list_resource_templates()
    assert {tool.name for tool in tools.tools} == {
        "search_manuscripts",
        "browse_page",
        "find_parallels",
        "search_multiple_phrases",
    }
    assert {prompt.name for prompt in prompts.prompts} == {
        "find_witnesses",
        "inspect_manuscript",
        "find_composition_parallels",
    }
    assert any(
        template.uri_template == "genizah://page/{sys_id}/{uid}"
        for template in templates.resource_templates
    )
