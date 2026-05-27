"""Check IA Web Archive coverage for a site"""

import csv
import re
from pathlib import Path
from typing import Any, Generator

import click
from wayback import CdxRecord, WaybackClient


class DefaultCommandGroup(click.Group):
    """Use a default subcommand when the first token is not a known command."""

    def __init__(self, *args: Any, default_command: str, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.default_command = default_command

    def parse_args(self, ctx: click.Context, args: list[str]) -> list[str]:
        if args and args[0] not in self.commands and args[0] not in {"-h", "--help"}:
            args.insert(0, self.default_command)
        return super().parse_args(ctx, args)


def sanitize_filename(name: str) -> str:
    """Sanitize a string to be safe for use as a filename."""
    safe_name: str = name.lower().strip()
    safe_name = re.sub(r"[^\w]+", "-", safe_name)
    # macOS has 255 char limit & we leave space for .csv extension
    return safe_name[0:250]


def _timestamp_order_key(timestamp: str) -> str:
    """Build a sort key for timestamps in coverage CSV rows."""
    digits: str = "".join(ch for ch in timestamp if ch.isdigit())
    return digits[0:14] if len(digits) >= 14 else ""


def compact_coverage_csv(input_csv: Path, output_csv: Path) -> tuple[int, int]:
    """Trim a coverage CSV to latest capture per SURT and write output CSV."""
    with open(input_csv, "r", newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        if reader.fieldnames is None:
            raise click.ClickException("Input CSV is missing a header row")

        required_fields: set[str] = {"sorting key", "timestamp"}
        missing_fields: set[str] = required_fields.difference(reader.fieldnames)
        if missing_fields:
            missing: str = ", ".join(sorted(missing_fields))
            raise click.ClickException(
                f"Input CSV is missing required columns: {missing}"
            )

        latest_by_surt: dict[str, dict[str, str]] = {}
        row_count: int = 0
        for row in reader:
            row_count += 1
            surt: str = row.get("sorting key", "")
            current_timestamp: str = row.get("timestamp", "")
            previous: dict[str, str] | None = latest_by_surt.get(surt)
            if previous is None:
                latest_by_surt[surt] = row
                continue

            previous_timestamp: str = previous.get("timestamp", "")
            if _timestamp_order_key(current_timestamp) >= _timestamp_order_key(
                previous_timestamp
            ):
                latest_by_surt[surt] = row

    with open(output_csv, "w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=reader.fieldnames)
        writer.writeheader()
        for row in latest_by_surt.values():
            writer.writerow(row)

    return row_count, len(latest_by_surt)


@click.group(cls=DefaultCommandGroup, default_command="search")
@click.help_option("-h", "--help")
def cli() -> None:
    """Check IA Web Archive coverage and post-process coverage CSVs."""


@cli.command("search")
@click.argument("query", nargs=1, required=True, type=str)
@click.option(
    "--match-type",
    "--mt",
    type=click.Choice(["exact", "prefix", "host", "domain"]),
    help="Type of match to perform",
)
@click.option(
    "--limit",
    "-l",
    type=int,
    help="Maximum results per API request (NOT per query)",
)
@click.option(
    "--from",
    "from_date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Captures after this date (YYYY-MM-DD)",
)
@click.option(
    "--to",
    "to_date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Captures before this date (YYYY-MM-DD)",
)
@click.option(
    "--mime",
    type=str,
    help="Filter to captures with MIME type (regex, ex. 'text/.*' for all text types)",
)
@click.option(
    "--status",
    type=str,
    help="Filter to captures with HTTP status (regex, ex. '2..' for 200 status codes)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, writable=True, resolve_path=True),
    help="Output CSV file path (defaults to sanitized query with .csv extension)",
)
# TODO debug print parameters before request, can we print number of results?
def search_wayback(
    query: str,
    match_type: str | None,
    limit: int | None,
    from_date,
    to_date,
    mime: str | None,
    status: str | None,
    output: str | None,
) -> None:
    """Check Internet Archive Web Archive coverage for a site/domain."""
    client: WaybackClient = WaybackClient()
    # Construct query parameters
    params: dict[str, Any] = {
        "url": query,
    }
    optional_params: dict[str, Any] = {
        "match_type": match_type,
        "limit": limit,
        "from_date": from_date,
        "to": to_date,
    }
    params.update({k: v for k, v in optional_params.items() if v is not None})

    # Build filters https://wayback.readthedocs.io/en/stable/usage.html#api-documentation
    # There are more fields that might be useful in some scenarios:
    # urlkey, timestamp, original, mimetype, statuscode, digest, length
    filters: list[str] = []
    if mime:
        filters.append(f"mimetype:{mime}")
    if status:
        filters.append(f"statuscode:{status}")
    if len(filters):
        params["filter_field"] = filters

    results: Generator[CdxRecord, Any, int] = client.search(**params)
    # Results is a GENERATOR, not a list, page through all results
    with open(
        output or f"{sanitize_filename(query)}.csv", "w", newline="", encoding="utf-8"
    ) as output_file:
        writer = csv.writer(output_file)
        writer.writerow(
            [
                "sorting key",
                "original",
                "timestamp",
                "status code",
                "mime type",
                "archived url",
                "wayback url",
            ]
        )
        for capture in results:
            writer.writerow(
                [
                    capture.urlkey,
                    capture.original,
                    capture.timestamp,
                    capture.statuscode,
                    capture.mimetype,
                    capture.raw_url,
                    capture.view_url,
                ]
            )
            # TODO progress bar


@cli.command("compact")
@click.argument(
    "input_csv",
    type=click.Path(
        exists=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
)
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, writable=True, resolve_path=True, path_type=Path),
    help="Output CSV path (defaults to '<input>-compact.csv')",
)
def compact(input_csv: Path, output: Path | None) -> None:
    """Trim coverage CSV to the latest capture row per SURT (sorting key)."""
    default_output: Path = input_csv.with_name(
        f"{input_csv.stem}-compact{input_csv.suffix}"
    )
    output_csv: Path = output or default_output
    in_count, out_count = compact_coverage_csv(input_csv, output_csv)
    click.echo(
        f"Compacted {in_count} rows in {input_csv} to {out_count} rows in {output_csv}"
    )


if __name__ == "__main__":
    cli()
