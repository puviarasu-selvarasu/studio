"""Studio composition root and command-line entry point."""

from __future__ import annotations

import argparse
from collections.abc import Sequence


def build_parser() -> argparse.ArgumentParser:
    """Create the Studio command-line argument parser."""

    parser = argparse.ArgumentParser(
        prog="studio",
        description=(
            "Studio - local-first AI-assisted animation "
            "production engine."
        ),
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Studio 0.1.0",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run Studio."""

    parser = build_parser()
    parser.parse_args(argv)

    from studio_ui.app import run

    return run(argv=[])


if __name__ == "__main__":
    raise SystemExit(main())