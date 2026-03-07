import argparse
import sys
from pathlib import Path
from rich.console import Console
from . import __version__
from .parser import parse_migration, parse_directory, is_alembic_migration
from .analyzer import analyze, has_dangerous, has_cautious_or_dangerous
from .report import render_table, render_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="schema-advisor",
        description="Analyze Alembic migrations for schema change risks",
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Path to a migration file or directory of migrations",
    )
    parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with non-zero code if dangerous changes found (for CI)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    args = parser.parse_args(argv)

    path: Path = args.path
    if not path.exists():
        print(f"Error: {path} does not exist", file=sys.stderr)
        return 1

    if path.is_file():
        if not is_alembic_migration(path):
            print(f"Error: {path} does not appear to be an Alembic migration", file=sys.stderr)
            return 1
        operations = parse_migration(path)
    else:
        operations = parse_directory(path)

    if not operations:
        print("No migration operations found.", file=sys.stderr)
        return 0

    findings = analyze(operations)

    if args.format == "json":
        print(render_json(findings))
    else:
        render_table(findings)

    if args.exit_code and has_dangerous(findings):
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
