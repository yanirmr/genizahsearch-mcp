import pytest
from pydantic import ValidationError

from genizah_mcp.models import BrowseInput, MultiPhraseInput, SearchInput


def test_hebrew_is_preserved() -> None:
    assert SearchInput(query="  ויאמר  ").query == "ויאמר"


def test_invalid_search_coupling() -> None:
    with pytest.raises(ValidationError):
        SearchInput(query="x", search_mode="title", gap=1)


def test_browse_requires_locator() -> None:
    with pytest.raises(ValidationError):
        BrowseInput(sys_id="123")


def test_duplicate_phrases_rejected() -> None:
    with pytest.raises(ValidationError):
        MultiPhraseInput(phrases=["א", "א"])
