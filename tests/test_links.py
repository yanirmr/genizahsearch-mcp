import pytest

from genizah_mcp.errors import GenizahAPIError
from genizah_mcp.links import page_uri


def test_page_uri() -> None:
    assert page_uri("9900", "IE1_P2_FL3") == "genizah://page/9900/IE1_P2_FL3"


def test_bad_page_uri_rejected() -> None:
    with pytest.raises(GenizahAPIError):
        page_uri("../x", "IE1_P2_FL3")
