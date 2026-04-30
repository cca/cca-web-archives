# Web Archives

## Simple CLI Tools

Simple command-line archiving of smaller sites without much interactivity. These tools simply download the HTML you see in the browser and do not capture dynamic content (e.g. infinite scroll, search results).

- [`httrack`](https://www.httrack.com/page/2/en/index.html) - no update since 2017, `brew install httrack`
- [`wget`](https://man7.org/linux/man-pages/man1/wget.1.html) - common web utility, `brew install wget`
- [`wayback`](https://github.com/wabarc/wayback) - CLI to archive to IA & other archives, confusingly not the same as the IA's Wayback Machine

```bash
httrack "https://gradthesis2007.cca.edu" -O "gradthesis2007.cca.edu" "gradthesis2007.cca.edu/*" -v
wget --mirror --convert-links --adjust-extension --page-requisites --no-parent --domains=example.com http://example.com
wayback https://gradthesis2007.cca.edu # only does one page, submits to several archives, not just IA
wayback urls.txt # archive all URLs in a file, TODO need to find a way to limit archives submitted to
```

Try the `wgetmirror` script which just accepts a domain and runs the wget command above, saving output to a log file.

The archive-specific flags for `wayback` like `--ia` still submit to _all_ five services the tool uses. To skip some, create a wayback.conf file like the one below. I couldn't figure out how to disable Ghost Archive.

```env
WAYBACK_ENABLE_IS=false
WAYBACK_ENABLE_IP=false
WAYBACK_ENABLE_PH=false
```

## Mirroring a Site on GitHub Pages

This approach is suitable to small sites without a lot of media, since GitHub has a 1 GB limit on repository size. We can host the site for free, even once the CCA GitHub org is no longer a paid account, and it can be easily forked to other accounts.

1. Use the `wget` command to mirror the site
1. (Optional) Add a readme describing the site & archiving method
1. Push the local repo to GitHub `gh repo create` under the CCA org
1. GH Repo > Settings > Pages > Source: deploy from a branch & Branch: main "/ (root)"
1. Once the site deploys & you can confirm it works, add the URL to the [CCA Web Archives](https://github.com/cca/cca-web-archives/) site

## Mirroring a Site on GCP

**TBD** do a complete trial run with this method and fill out the steps below

Question: one parent project for all web archives? I think this makes the most sense.

1. Use the `wget` command to mirror the site
1. Create a storage bucket underneath the project
1. `gcloud storage cp --recursive website.cca.edu gs://my-bucket/ocl.cca.edu`
1. Make the storage bucket public
1. Add the URL to the CCA Web Archives

## Scraping Only Portal Courses

The Portal course catalog is hard to scrape with `wget` because the root /courses/ page is dynamic so it cannot be used as a starting point but we do not want to crawl the entirety of Portal, either. I've not found success with feeding an `--input-file` of all /courses/subjects/ANIMA URLs nor with flags like `--include-directories=/courses/` or `--accept-regex=/courses/.*` which in combination with the input file only download the subject pages but none of the courses linked on them. We may need to great a giant URL list of all courses and subjects. I compiled the original subjects list by looking at Portal's analytics.

Another alternative; build a simple view in Portal to show the data in a scrapable format, as Eric and Tanza discussed about Showcase.

## Web Recorder

Scripts for archiving Instagram accounts.

## Internet Archive

We can use [their Google Sheets service](https://archive.org/services/wayback-gsheets/) to archive 5k URLs at a time and 30k per day, see [this blog post](https://ws-dl.blogspot.com/2026/02/2026-02-12-how-to-archive-web-pages-in.html).

[ia cli tool](https://archive.org/developers/internetarchive/cli.html)

[ia python library](https://archive.org/developers/internetarchive/index.html)
