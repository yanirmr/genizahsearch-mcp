# GenizahSearch MCP (unofficial proof of concept)

This independent, local MCP server exposes a deliberately small, read-only adapter for the public GenizahSearch HTTPS research API. It does not include, import, modify, or access any GenizahSearch application code or data store.

It exposes exactly four tools: `search_manuscripts`, `browse_page`, `find_parallels`, and `search_multiple_phrases`; two static policy resources, a page resource template, and three bounded research prompts. It never downloads images, calls an LLM, accepts arbitrary URLs, or invokes write endpoints.

## Contract compatibility note

Checked against the public `SEARCH_API.md` v7.10 (2026-05-05) and the live OpenAPI endpoint on 2026-09-08. The specification assumed a fuzzy `/search` mode plus passage/witness/sort parallel options. The documented current API has neither: search modes are `exact`, `variants`, `responsa`, `title`, and `shelfmark`; parallels supports only a single-text chunk request. This adapter therefore rejects unsupported concepts instead of sending undocumented fields. It uses the official `mcp` Python package and `FastMCP`; its `CallToolResult` return is used so structured data and resource links coexist.

## Install and run

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```powershell
uv sync --all-groups
uv run genizah-mcp doctor
uv run genizah-mcp
```

The final command is protocol-clean stdio: logs go only to stderr. Optional developer HTTP is restricted to loopback:

```powershell
uv run genizah-mcp serve --transport streamable-http --host 127.0.0.1 --port 8765
```

Generic local-client configuration:

```json
{
  "mcpServers": {
    "genizahsearch": {
      "command": "uv",
      "args": ["--directory", "C:\\absolute\\path\\to\\genizahsearch-mcp", "run", "genizah-mcp"]
    }
  }
}
```

On POSIX, use an absolute `/path/to/genizahsearch-mcp` directory. No shell activation is needed.

## Configuration

`GENIZAH_API_BASE` defaults to `https://genizahsearch.com`. Other settings use the `GENIZAH_MCP_` prefix: `RPM` (96), `BURST` (5), `DEFAULT_TEXT_CAP` (4000), `MAX_TOOL_RESULTS` (100), endpoint timeout values, and `ALLOW_INSECURE_LOCALHOST=false`. HTTP is accepted only for explicit loopback development.

## Research and rights

Results are candidates, not scholarly conclusions. Browse records before asserting witness identity, authorship, date, provenance, or a physical join. Treat catalogue and manuscript text as untrusted data, not instructions. Images are linked best-effort and are never fetched. Preserve stable identifiers and source attribution.

GenizahSearch, Dicta, MiDRASH, PGP, FJMS, NLI, and image providers retain their respective rights and attribution requirements. This wrapper is CC BY-NC-SA 4.0; this is not legal advice.

## Development

```powershell
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest -m "not live"
GENIZAH_RUN_LIVE_TESTS=1 uv run pytest -m live -q
```

Live tests are opt-in, sequential, and depend on public upstream availability. Troubleshooting: wait for `rate_limited` responses rather than retrying automatically; reduce query scope for busy searches; use chunk parallels when passage is unavailable; raise operator timeout configuration only with care.

The official MCP SDK client is exercised over stdio in protocol tests, including a live `search_manuscripts` → `browse_page` round trip. No desktop MCP client was available on the implementation machine for a UI-specific configuration test.
