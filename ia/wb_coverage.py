"""Check IA Web Archive coverage for a site"""

import csv
import re
from typing import Any, Generator

import click
from wayback import CdxRecord, WaybackClient


def sanitize_filename(name: str) -> str:
    """Sanitize a string to be safe for use as a filename."""
    safe_name: str = name.lower().strip()
    safe_name = re.sub(r"[^\w]+", "-", safe_name)
    # macOS has 255 char limit & we leave space for .csv extension
    return safe_name[0:250]


@click.command()
@click.help_option("-h", "--help")
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
# TODO can we filter to only the _latest_ captures?
# TODO debug print parameters before request, can we print number of results?
def search_wayback(
    query: str,
    match_type: str,
    limit: int,
    from_date,
    to_date,
    mime: str,
    status: str,
    output: str,
):
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


if __name__ == "__main__":
    search_wayback()
