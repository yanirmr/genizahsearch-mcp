"""Console entry point. Stdio is the safe default transport."""

import argparse
import asyncio
import json
import sys
from typing import cast

import mcp

from . import __version__
from .client import GenizahClient
from .config import Settings
from .errors import GenizahAPIError
from .server import configure_logging, create_server


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="genizah-mcp")
    sub = result.add_subparsers(dest="command")
    serve = sub.add_parser("serve")
    serve.add_argument("--transport", choices=["stdio", "streamable-http"], default="stdio")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8765)
    sub.add_parser("doctor")
    sub.add_parser("version")
    return result


async def run_doctor(settings: Settings) -> int:
    client = GenizahClient(settings)
    try:
        document = await client.doctor()
    except GenizahAPIError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    finally:
        await client.aclose()
    paths = (
        cast(dict[str, object], document.get("paths"))
        if isinstance(document.get("paths"), dict)
        else {}
    )
    # The document itself is served below /api, so FastAPI publishes paths relative to it.
    required = {"/search", "/browse", "/parallels"}
    missing = sorted(required - set(paths))
    if missing:
        print(f"Incompatible upstream: missing {', '.join(missing)}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "status": "compatible",
                "mcp_version": getattr(mcp, "__version__", "unknown"),
                "upstream_openapi": document.get("info", {}).get("version"),
            },
            ensure_ascii=False,
        )
    )
    return 0


def main() -> None:
    args = parser().parse_args()
    command = args.command or "serve"
    if command == "version":
        print(__version__)
        return
    try:
        settings = Settings()
    except Exception as exc:
        print(f"invalid configuration: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    if command == "doctor":
        raise SystemExit(asyncio.run(run_doctor(settings)))
    configure_logging(settings.log_level)
    transport = getattr(args, "transport", "stdio")
    host = getattr(args, "host", "127.0.0.1")
    port = getattr(args, "port", 8765)
    if transport == "streamable-http" and host not in {"127.0.0.1", "localhost", "::1"}:
        print("streamable HTTP may bind only to a loopback address", file=sys.stderr)
        raise SystemExit(2)
    server = create_server(settings)
    # Current official SDK uses the transport name directly. Host/port are intentionally
    # delegated only in developer HTTP mode; stdio never writes banners to stdout.
    if transport == "stdio":
        server.run(transport="stdio")
    else:
        server.run(transport="streamable-http", host=host, port=port)


if __name__ == "__main__":
    main()
