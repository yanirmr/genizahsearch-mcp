# Tool contracts

The server exposes only `search_manuscripts`, `browse_page`, `find_parallels`, and `search_multiple_phrases`. Their JSON schemas are generated from the Pydantic inputs in `src/genizah_mcp/models.py` by the official MCP SDK. All results include wrapper schema version `1`, structured warnings where available, stable locators where resolvable, and candidate-language summaries.

`search_manuscripts` accepts exact, variants, Responsa, title, and shelfmark search. `browse_page` requires a `sys_id` and page locator. `find_parallels` accepts one text and uses supported chunk matching. `search_multiple_phrases` accepts at most five distinct phrases and merges page candidates deterministically into tiers A/B/C.

The current upstream does not support fuzzy manuscript search or passage/witness parallel search; this is intentionally not represented as a tool option.
