# Internet Archive

See IA's documentation on [its python library](https://archive.org/developers/internetarchive/index.html) and [metadata schema](https://archive.org/developers/metadata-schema/index.html) for reference.

## Setup

Enter Internet Archive credentials into the .env file. Look up the CCA/C Archives account in Dashlane.

```sh
uv sync # install python project
cp example.env .env
vim .env # edit in IA S3 credentials
```

## Test

```sh
uv run pytest # run tests
uv run ruff check . --fix # lint files and auto-fix
```

## Checking Wayback Holdings Manually

We can use `*` wildcards on domains to retrieve data about what content is already in IA. For instance, [here is the whole cca.edu domain](https://web.archive.org/web/*/cca.edu/*). The tabs show:

- **URLs**: total list of URLs, max 10,000, filterable my URL or MIME type
- **Site Map**: a radial tree graph of capture paths for a given year
- **Summary**: captures in a time range by MIME type

The top-level cca.edu domain has so much data that it is not very useful, but we might be able to investigate smaller subsites this way. For instance, [here is the 2007 grad thesis site](https://web.archive.org/web/*/gradthesis2007.cca.edu*) where the URLs and site map offer a more legible picture of how much of the site has been archived.
f

## Checking Wayback Holdings Programmatically

The Wayback Machine has an additional [CDX API mentioned here](https://archive.org/help/wayback_api.php) and [documented here on GitHub](https://github.com/internetarchive/wayback/tree/master/wayback-cdx-server). It is likely better to use the `wayback` python library when interacting with this API. [Here is `wayback`'s documentation](https://wayback.readthedocs.io/en/stable/usage.html#api-documentation). We have a [`wb_coverage.py`](wb_coverage.py) script to check IA Web Archive coverage for our sites. Example usage:

```sh
# check grad thesis site HTML pages with 2XX status codes
uv run python wb_coverage.py --match-type host --mime 'text/html' --status '^2' gradthesis2007.cca.edu
# cca.edu captures for 2019-present
uv run python wb_coverage.py --mt prefix --from 2019-01-01 cca.edu
```

The script creates a CSV named after the query, e.g. "gradthesis2007-cca-edu.csv" or "cca-edu.csv".

Complete usage information is below. Note the mime type and status filters are regexes. There are other capture fields which could be filtered on as well if they're useful, but we will often want only `2XX` status responses and sometimes `text/html` MIME types.

```sh
Usage: wb_coverage.py [OPTIONS] QUERY

  Check Internet Archive Web Archive coverage for a site/domain.

Options:
  -h, --help                      Show this message and exit.
  --match-type, --mt [exact|prefix|host|domain]
                                  Type of match to perform
  -l, --limit INTEGER             Maximum results per API request (NOT per
                                  query)
  --from [%Y-%m-%d]               Captures after this date (YYYY-MM-DD)
  --to [%Y-%m-%d]                 Captures before this date (YYYY-MM-DD)
  --mime TEXT                     Filter to captures with MIME type (regex,
                                  ex. 'text/.*' for all text types)
  --status TEXT                   Filter to captures with HTTP status (regex,
                                  ex. '2..' for 200 status codes)
  -o, --output FILE               Output CSV file path (defaults to sanitized
                                  query with .csv extension)
```

Match types (`--mt`):

- `host`: match same domain, `--mt host cca.edu` matches `cca.edu` but not `libraries.cca.edu`
- `domain`: match domain _and subdomains_, `--mt domain cca.edu` matches `libraries.cca.edu` and `cca.edu`
- `prefix`: URLs with a common prefix which is good for a path-separated subsite, e.g. `libraries.cca.edu/exhibitions` or `portal.cca.edu/courses`
- `exact` (default): one specific page, `libraries.cca.edu/about-us/about-us/staff`

There are [some nuances](https://wayback.readthedocs.io/en/stable/usage.html#wayback.WaybackClient) for convenience. All URL patterns match both http/https, are case insensitive, and www. and www\*. subdomains are treated as no subdomain at all (e.g. `cca.edu` = `www.cca.edu`). Wildcards can be used and they convert the match type as appropriate; so `*.cca.edu` is the same as `--mt domain cca.edu` while `cca.edu/*` is the same as `--mt prefix cca.edu`.

## Two Wayback Repos

To avoid confusion, keep in mind the difference between the `wayback` python library and the `wayback` CLI.

[edgi-govdata-archiving/wayback](https://github.com/edgi-govdata-archiving/wayback) is a python library for Internet Archive's Wayback CDX API, used here in the `wb_coverage.py` script.

[wabarc/wayback](https://github.com/webarc/wayback) is a command-line utility for submitting to multiple archives at once, mentioned in [the docs readme](../docs/readme.md).
