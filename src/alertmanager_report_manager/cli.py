"""Command line interface for local project operations."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from alertmanager_report_manager import __version__
from alertmanager_report_manager.storage.sqlite import initialize_database


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="alertmanager-report-manager",
        description="Alertmanager reporting and analytics utilities.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subcommands = parser.add_subparsers(dest="command")

    init_db = subcommands.add_parser("init-db", help="Initialize a SQLite database file.")
    init_db.add_argument(
        "database",
        type=Path,
        help="Path to the SQLite database file to create or update.",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init-db":
        initialize_database(args.database)
        print(f"Initialized SQLite database at {args.database}")
        return 0

    parser.print_help()
    return 0
