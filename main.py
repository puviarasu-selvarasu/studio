"""Studio composition root and command-line entry point."""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    """Create the Studio command-line argument parser.

    Returns:
        Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="studio",
        description=(
            "Studio — local-first AI-assisted 2D animation "
            "production engine."
        ),
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Studio 0.1.0",
    )

    return parser


def main() -> int:
    """Run the Studio command-line entry point.

    Returns:
        Process exit code.
    """
    parser = build_parser()
    parser.parse_args()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())