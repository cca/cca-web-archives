from __future__ import annotations

import argparse
import re
from collections.abc import Iterable
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup

START_URL = "https://www.cca.edu/exhibitions/rewind-review-respond/"
DEFAULT_OUTPUT_FILE = "rrr-article-urls.txt"


def normalize_url(url: str) -> str:
    """Normalize URL for stable de-duplication."""
    parts = urlsplit(url.strip())
    path: str = parts.path.rstrip("/")
    if not path:
        path = "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, "", ""))


def get_soup(url: str, timeout: int) -> BeautifulSoup:
    response: requests.Response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def hrefs_from_program_cards(soup: BeautifulSoup, base_url: str) -> list[str]:
    hrefs: list[str] = []
    for anchor in soup.select("a.program-card[href]"):
        href = anchor.get("href")
        if not href:
            continue
        absolute: str = urljoin(base_url, href)
        hrefs.append(normalize_url(absolute))
    return hrefs


def unique_in_order(urls: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    unique_urls: list[str] = []
    for url in urls:
        if url in seen:
            continue
        seen.add(url)
        unique_urls.append(url)
    return unique_urls


def issue_publication_number(issue_url: str) -> int | None:
    """Extract an issue number from a URL slug, if present."""
    path: str = urlsplit(issue_url).path.rstrip("/")
    slug: str = path.split("/")[-1] if path else ""
    match: re.Match[str] | None = re.search(r"(\d+)", slug)
    if not match:
        return None
    return int(match.group(1))


def issue_sort_key(issue_url: str) -> tuple[int, int, str]:
    number: int | None = issue_publication_number(issue_url)
    if number is None:
        return (1, 0, issue_url)
    return (0, number, issue_url)


def scrape_rrr_article_urls(
    start_url: str,
    timeout: int,
    min_articles_per_issue: int,
    expected_issue_count: int,
) -> tuple[list[str], dict[str, list[str]], dict[str, int], list[str]]:
    index_soup: BeautifulSoup = get_soup(start_url, timeout=timeout)
    issue_urls: list[str] = unique_in_order(
        hrefs_from_program_cards(index_soup, base_url=start_url)
    )
    issue_urls = sorted(issue_urls, key=issue_sort_key)

    issue_articles: dict[str, list[str]] = {}
    issue_article_counts: dict[str, int] = {}
    all_article_urls: list[str] = []
    seen_articles: set[str] = set()

    for issue_url in issue_urls:
        issue_soup: BeautifulSoup = get_soup(issue_url, timeout=timeout)
        article_urls: list[str] = sorted(
            hrefs_from_program_cards(issue_soup, base_url=issue_url)
        )
        issue_articles[issue_url] = []

        for article_url in article_urls:
            if article_url in seen_articles:
                continue
            seen_articles.add(article_url)
            issue_articles[issue_url].append(article_url)
            all_article_urls.append(article_url)

        issue_article_counts[issue_url] = len(issue_articles[issue_url])

    warnings: list[str] = []
    if len(issue_urls) != expected_issue_count:
        warnings.append(
            f"Expected about {expected_issue_count} issues, found {len(issue_urls)}. "
            "Page markup may have changed."
        )

    for issue_url, article_count in issue_article_counts.items():
        if article_count <= min_articles_per_issue:
            warnings.append(
                f"Issue {issue_url} has {article_count} articles; expected more than "
                f"{min_articles_per_issue}. Markup may have changed."
            )

    for issue_url in issue_urls:
        if issue_publication_number(issue_url) is None:
            warnings.append(
                f"Could not parse issue number from {issue_url}; placed after numbered issues."
            )

    return issue_urls, issue_articles, issue_article_counts, warnings


def write_grouped_plain_text_urls(
    file_path: Path,
    issue_urls: list[str],
    issue_articles: dict[str, list[str]],
) -> None:
    lines: list[str] = []
    for issue_url in issue_urls:
        lines.append(issue_url)
        lines.extend(issue_articles[issue_url])
        lines.append("")

    file_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Scrape RRR issue pages and collect unique article URLs from "
            "a.program-card href values."
        )
    )
    parser.add_argument("--start-url", default=START_URL, help="RRR landing page URL")
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_FILE,
        help="Output plain-text file for one URL per line",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="HTTP request timeout in seconds",
    )
    parser.add_argument(
        "--min-articles-per-issue",
        type=int,
        default=8,
        help="Warn if an issue has <= this many article URLs",
    )
    parser.add_argument(
        "--expected-issue-count",
        type=int,
        default=12,
        help="Warn if discovered issue count differs",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    issue_urls, issue_articles, issue_article_counts, warnings = (
        scrape_rrr_article_urls(
            start_url=args.start_url,
            timeout=args.timeout,
            min_articles_per_issue=args.min_articles_per_issue,
            expected_issue_count=args.expected_issue_count,
        )
    )

    output_path: Path = Path(args.output)
    write_grouped_plain_text_urls(output_path, issue_urls, issue_articles)

    print(f"Discovered {len(issue_article_counts)} issues")
    for issue_url, count in issue_article_counts.items():
        print(f"- {issue_url}: {count} article URLs")

    total_unique_articles: int = sum(issue_article_counts.values())
    print(
        f"\nWrote {total_unique_articles} unique article URLs grouped under "
        f"{len(issue_urls)} issue URLs to {output_path}"
    )
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"- {warning}")


if __name__ == "__main__":
    main()
