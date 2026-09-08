"""Validated MCP inputs and deliberately small public projections."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .links import UID_RE


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SearchFilters(StrictModel):
    domains: list[str] | None = None
    authors: list[str] | None = None
    works: list[str] | None = None
    library: list[str] | None = None
    library_filter_mode: Literal["include", "exclude"] | None = None
    materials: list[str] | None = None
    date_from: int | None = None
    date_to: int | None = None


class ResponsaOptions(StrictModel):
    variants: bool = False
    ja: bool = False
    flex_spacing: bool = False
    bidirectional: bool = False


class SearchInput(StrictModel):
    query: str = Field(min_length=1, max_length=1000)
    search_mode: Literal["exact", "variants", "responsa", "title", "shelfmark"] = "exact"
    gap: int = Field(default=0, ge=0)
    limit: int | None = Field(default=None, ge=1, le=100)
    filters: SearchFilters | None = None
    responsa_options: ResponsaOptions | None = None

    @model_validator(mode="after")
    def validate_coupling(self) -> "SearchInput":
        self.query = self.query.strip()
        if not self.query:
            raise ValueError("query must not be empty")
        if self.responsa_options is not None and self.search_mode != "responsa":
            raise ValueError("responsa_options is only valid for responsa search")
        if self.gap and self.search_mode in {"title", "shelfmark"}:
            raise ValueError("gap must be zero for title and shelfmark search")
        return self


class BrowseInput(StrictModel):
    sys_id: str = Field(min_length=1, max_length=128)
    uid: str | None = None
    p_num: int | None = Field(default=None, ge=1)
    volume_ie: str | None = None
    fl_id: str | None = None
    text_cap: int | None = Field(default=None, ge=100, le=10000)

    @model_validator(mode="after")
    def validate_locator(self) -> "BrowseInput":
        if not any((self.uid, self.p_num, self.fl_id)):
            raise ValueError("supply uid, p_num, or fl_id with sys_id")
        if self.uid and not UID_RE.fullmatch(self.uid):
            raise ValueError("uid must use the public IE..._P..._FL... format")
        if self.uid:
            volume, page, folio = self.uid.split("_")
            if self.volume_ie and self.volume_ie != volume:
                raise ValueError("uid conflicts with volume_ie")
            if self.p_num and self.p_num != int(page[1:]):
                raise ValueError("uid conflicts with p_num")
            if self.fl_id and self.fl_id != folio:
                raise ValueError("uid conflicts with fl_id")
        return self


class ParallelsInput(StrictModel):
    text: str = Field(min_length=1, max_length=20000)
    method: Literal["chunk"] = "chunk"
    chunk_size: int = Field(default=5, ge=2, le=20)
    mode: Literal["exact", "variants", "fuzzy"] = "exact"
    max_freq: float | None = Field(default=None, ge=1)
    boundary_mode: Literal["full", "boundary", "combined"] = "full"
    filters: SearchFilters | None = None

    @model_validator(mode="after")
    def nonempty(self) -> "ParallelsInput":
        self.text = self.text.strip()
        if not self.text:
            raise ValueError("text must not be empty")
        return self


class MultiPhraseInput(StrictModel):
    phrases: list[str] = Field(min_length=1, max_length=5)
    search_mode: Literal["exact", "variants", "responsa"] = "exact"
    limit_per_phrase: int = Field(default=25, ge=1, le=100)
    filters: SearchFilters | None = None
    responsa_options: ResponsaOptions | None = None

    @model_validator(mode="after")
    def distinct_phrases(self) -> "MultiPhraseInput":
        values = [phrase.strip() for phrase in self.phrases]
        if any(not phrase or len(phrase) > 1000 for phrase in values):
            raise ValueError("phrases must be non-empty and at most 1000 characters")
        if len(set(values)) != len(values):
            raise ValueError("phrases must be distinct")
        self.phrases = values
        if self.responsa_options and self.search_mode != "responsa":
            raise ValueError("responsa_options is only valid for responsa search")
        return self


class WarningDTO(BaseModel):
    code: str
    message: str


class ImageSourceDTO(BaseModel):
    name: str


class SearchHit(BaseModel):
    uid: str | None
    sys_id: str | None
    volume_ie: str | None = None
    p_num: int | None = None
    fl_id: str | None = None
    shelfmark: str | None = None
    title: str | None = None
    library_code: str | None = None
    library_name: str | None = None
    domains: list[str] = Field(default_factory=list)
    score: float | None = None
    snippet: str | None = None
    excerpt: str | None = None
    match_terms: list[str] = Field(default_factory=list)
    is_synthetic: bool = False
    image_url: str | None = None
    browse_url: str | None = None
    resource_uri: str | None = None


class SearchToolResult(BaseModel):
    schema_version: Literal[1] = 1
    upstream_schema_version: int | str | None = None
    source: str = "search"
    generated_at: str | None = None
    query: str
    search_mode: str
    returned_count: int
    upstream_total: int | None = None
    warnings: list[WarningDTO] = Field(default_factory=list)
    results: list[SearchHit]


class BrowseToolResult(BaseModel):
    schema_version: Literal[1] = 1
    upstream_schema_version: int | str | None = None
    source: str = "browse"
    generated_at: str | None = None
    uid: str | None = None
    sys_id: str
    volume_ie: str | None = None
    p_num: int | None = None
    fl_id: str | None = None
    shelfmark: str | None = None
    title: str | None = None
    library_code: str | None = None
    library_name: str | None = None
    text: str = ""
    text_source: str = "none"
    text_truncated: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
    image_url: str | None = None
    image_provider: str | None = None
    image_sources: list[ImageSourceDTO] = Field(default_factory=list)
    warnings: list[WarningDTO] = Field(default_factory=list)
    evidence_notice: str | None = None
    browse_url: str
    resource_uri: str | None = None
