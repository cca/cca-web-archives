# Web Archives

## Simple CLI Tools

Simple command-line archiving of smaller sites without much interactivity. These tools simply download the HTML you see in the browser and do not capture dynamic content (e.g. infinite scroll, search results).

- [`httrack`](https://www.httrack.com/page/2/en/index.html) - no update since 2017, `brew install httrack`
- [`wget`](https://man7.org/linux/man-pages/man1/wget.1.html) - common web utility, `brew install wget`

```bash
httrack "https://gradthesis2007.cca.edu" -O "gradthesis2007.cca.edu" "gradthesis2007.cca.edu/*" -v
wget --mirror --convert-links --adjust-extension --page-requisites --no-parent --domains=example.com http://example.com
```

Try the `wgetmirror` script which just accepts a domain and runs the wget command above, saving output to a log file.

## Web Recorder

Scripts for archiving Instagram accounts.

## Internet Archive

We can use [their Google Sheets service](https://archive.org/services/wayback-gsheets/) to archive 5k URLs at a time and 30k per day, see [this blog post](https://ws-dl.blogspot.com/2026/02/2026-02-12-how-to-archive-web-pages-in.html).

[ia cli tool](https://archive.org/developers/internetarchive/cli.html)

[ia python library](https://archive.org/developers/internetarchive/index.html)
