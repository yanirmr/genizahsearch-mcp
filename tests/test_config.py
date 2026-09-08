import pytest
from pydantic import ValidationError

from genizah_mcp.config import Settings


def test_base_normalizes_slash() -> None:
    assert Settings(api_base="https://example.test/").api_base == "https://example.test"


@pytest.mark.parametrize(
    "base", ["http://example.test", "https://x:y@example.test", "https://example.test/?x=1"]
)
def test_bad_base_rejected(base: str) -> None:
    with pytest.raises(ValidationError):
        Settings(api_base=base)


def test_local_http_needs_flag() -> None:
    assert (
        Settings(api_base="http://localhost", allow_insecure_localhost=True).api_base
        == "http://localhost"
    )
