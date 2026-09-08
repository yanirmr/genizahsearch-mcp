"""Safe, model-facing upstream error types."""

from dataclasses import dataclass


@dataclass(slots=True)
class GenizahAPIError(Exception):
    code: str
    message: str
    http_status: int | None = None
    retry_after_seconds: int | None = None
    retriable: bool = False

    def __str__(self) -> str:
        suffix = (
            f" Retry after {self.retry_after_seconds} seconds."
            if self.retry_after_seconds is not None
            else ""
        )
        return f"{self.code}: {self.message}{suffix}"
