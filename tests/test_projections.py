from genizah_mcp.projections import browse_result, search_result


def test_search_projection_is_bounded_and_links_relative_images() -> None:
    body = {
        "schema_version": 1,
        "results": [
            {
                "uid": "IE1_P2_FL3",
                "locator": {"sys_id": "99", "p_num": 2},
                "metadata": {"domains": ["Liturgy"]},
                "image_url": "/iiif/x",
                "unknown": "ignored",
            }
        ],
    }
    result = search_result(body, "אב", "exact", "https://example.test", 100)
    assert result.results[0].image_url == "https://example.test/iiif/x"


def test_snippet_notice() -> None:
    result = browse_result(
        {"locator": {"sys_id": "99", "uid": "IE1_P2_FL3"}, "text": "אב", "text_source": "snippet"},
        "https://example.test",
    )
    assert (
        result.evidence_notice
        == "Full text unavailable; evidence is based on a snippet of 2 characters."
    )
