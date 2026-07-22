# Rewind Review Respond

Scrape the article URLs for the twelve RRR issues from the main website for submission to the Internet Archive.

- Start here: https://www.cca.edu/exhibitions/rewind-review-respond/
- `a.program-card` -> href -> issue
- `a.program-card` -> href -> article

Confirm there are something like >7 articles in each issue, otherwise markup may have changed.

## Setup

`uv sync` _inside the RRR folder_. Note that the IA folder has its own python venv. For that reason, ignore the VS code import warnings in main.py; it assumes the other venv.

## Usage

Simply run `uv run python main.py` to write the article URLs to [`rrr-article-urls.txt`](./rrr-article-urls.txt) by default.

```sh
usage: main.py [-h] [--start-url START_URL] [--output OUTPUT] [--timeout TIMEOUT]
               [--min-articles-per-issue MIN_ARTICLES_PER_ISSUE] [--expected-issue-count EXPECTED_ISSUE_COUNT]

Scrape RRR issue pages and collect unique article URLs from a.program-card href values.

options:
  -h, --help            show this help message and exit
  --start-url START_URL
                        RRR landing page URL
  --output OUTPUT       Output plain-text file for one URL per line
  --timeout TIMEOUT     HTTP request timeout in seconds
  --min-articles-per-issue MIN_ARTICLES_PER_ISSUE
                        Warn if an issue has <= this many article URLs
  --expected-issue-count EXPECTED_ISSUE_COUNT
                        Warn if discovered issue count differs
```
