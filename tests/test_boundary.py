from pathlib import Path


def test_only_documented_endpoint_paths_are_used() -> None:
    production = "\n".join(path.read_text(encoding="utf-8") for path in Path("src").rglob("*.py"))
    for prohibited in ("/api/corrections", "/api/reviews", "supabase", "sqlite3", "requests"):
        assert prohibited not in production.lower()
