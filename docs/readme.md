# Web Archives

How to create web archives of CCA sites. Different tools are suitable for particular sites. Currently, my thinking is:

- `wget` script for small (<100 MB) static sites without much media, e.g. grad thesis site
- Webrecorder for small dynamic sites, e.g. Build Lab
- Submit URLs to IA for our largest static sites, e.g. Comics

The biggest outstanding question is archiving sites that are both large and dynamic, such as Portal. Webrecorder takes time and IA may not be a faithful reproduction. I am considering using Webrecorder's Browsertrix locally with custom behaviors. Some sites are hard to crawl because their index is dynamic but their content is static, e.g. Portal's courses and policies, and for those we may be able to compile a list of URLs (e.g. from analytics) to feed to `wget`.

## Simple CLI Tools

Command-line archiving of smaller sites without much interactivity. These tools simply download the HTML you see in the browser and do not capture dynamic content (e.g. infinite scroll, search results, facet filtering).

- [`httrack`](https://www.httrack.com/page/2/en/index.html) - no update since 2017, `brew install httrack`
- [`wget`](https://man7.org/linux/man-pages/man1/wget.1.html) - common web utility, `brew install wget`
- [`wayback`](https://github.com/wabarc/wayback) - CLI to archive to IA & other archives, confusingly _not_ the same as the IA's Wayback Machine

```bash
httrack "https://gradthesis2007.cca.edu" -O "gradthesis2007.cca.edu" "gradthesis2007.cca.edu/*" -v
wget --mirror --convert-links --adjust-extension --page-requisites --no-parent --domains=example.com http://example.com
wayback https://gradthesis2007.cca.edu # only does one page, submits to several archives, not just IA
wayback urls.txt # archive all URLs in a file, see note below about skipping some digital archives
```

Try [the `wgetmirror` script](./wgetmirror) which accepts a domain and runs the wget command above, saving output to a log file.

## Mirroring a Site on GitHub Pages

This approach is suitable to small sites without a lot of media, since GitHub has a 100 MB limit on repository size. We can host the site for free, even once the CCA GitHub org is no longer a paid account, and it can be easily forked to other accounts. The [push-to-gh-pages.sh](./push-to-gh-pages.sh) script automates these steps.

1. Use the `wget` command to mirror the site
1. (Optional) Add a readme describing the site & archiving method
1. Push the local repo to GitHub `gh repo create` under the CCA org
1. GH Repo > Settings > Pages > Source: deploy from a branch & Branch: main "/ (root)"
1. Once the site deploys & you can confirm it works, add the URL to the [CCA Web Archives](https://github.com/cca/cca-web-archives/) site

Once a site has been mirrored to Github, `node domainstub.js` (in project root) creates a stub JSON file with the domain for the CCA Web Archives Gallery.

### GitHub 100mb File Size Limit

GitHub's file size limit is 100 MB, which some WACZ files may exceed, but we can work around this using `git lfs` and a GitHub Action for deployment.

We can follow the instructions for configuring [Git Large File Storage](https://git-lfs.com/) to work around this. However, then GitHub Pages will not fetch the WACZ, only the text pointer that LFS uses. I tried creating a GitHub Release with the WACZ as an asset, but WebRecorder refused to load it from the github.com URL due to CORS. Finally, I deployed to GitHub Pages using a workflow with `lfs: true` in its checkout action. The [Build Lab](https://github.com/cca/build.cca.edu) archive is an example of this approach; see its [deploy](https://github.com/cca/build.cca.edu/blob/main/.github/workflows/deploy.yml) workflow.

```sh
git lfs install
git lfs track "*.wacz"
git add .gitattributes
# now you can git add, commit, & push as usual
# if you already have a commit with an existing large file in it, migrate it to LFS like so:
git lfs migrate import --include="*.wacz" --everything
```

## Mirroring a Site on GCP

**TBD** do a complete trial run with this method and fill out the steps below

Eric created a `digital-archiving` GCP project to be the parent for all archives storage buckets.

1. Use the `wget` command to mirror the site
1. Create a storage bucket underneath the project
1. `gcloud storage cp --recursive example.cca.edu gs://my-bucket/example.cca.edu`
1. Make the storage bucket public
1. Add the URL to the CCA Web Archives

## Webrecorder

Dynamic sites which do not load all their content in the initial HTML (e.g. infinite scroll, search filters, etc.) will not work when copied with `wget` or other naïve web archiving tools. [Webrecorder](https://webrecorder.net/) lets you record interactions with a dynamic site and then "replay" them later. To use Webrecorder:

- Install the recorder Chrome extension or desktop app
- Open the site and start recording
  - Webrecorder has an "autopilot" mode which will scroll infinitely but it does not interact in other ways such as clicking links or opening modal dialogs
- Interact with the site _exhaustively_ to load all content: click all links, scroll to the edges, open modal dialogs, etc.
- Stop recording (click **Cancel** for Chrome extension)
- Download the WACZ from within Webrecorder
- Create a static site for hosting the WACZ which uses the embedded replayer
  - If the WACZ is too large for GitHub Pages, it could be hosted elsewhere like GCP
  - [Studio Forward](https://github.com/cca/studioforward) is a minimal example. It can be copied for other sites.

For large sites that need dynamic crawls (e.g. Portal), we could look into [running Webrecorder's Browsertrix locally](https://docs.browsertrix.com/deploy/local/) and writing custom [browser behaviors](https://crawler.docs.browsertrix.com/user-guide/behaviors/) to navigate the site.

## Internet Archive

We can use [their Google Sheets service](https://archive.org/services/wayback-gsheets/) to archive 5k URLs at a time and 30k per day, see [this blog post](https://ws-dl.blogspot.com/2026/02/2026-02-12-how-to-archive-web-pages-in.html).

- [ia cli tool](https://archive.org/developers/internetarchive/cli.html)
- [ia python library](https://archive.org/developers/internetarchive/index.html)

## Archiving a Site with `wayback`

`wayback` is not made by the Internet Archive and its primary utility is submitting to _multiple web archives at once_. The archive-specific flags for `wayback` like `--ia` still submit to _all_ five services the tool uses. **Update**: this should be fixed in version 0.21.1. To skip some archives, you can also create a wayback.conf file like the one below. I couldn't figure out how to disable Ghost Archive.

```env
WAYBACK_ENABLE_IS=false
WAYBACK_ENABLE_IP=false
WAYBACK_ENABLE_PH=false
```

## Scraping Only Portal Courses/Policies/etc

Many sections of Portal are difficult to scrape because while their content pages are static with interesting data, the index is dynamic and cannot be scraped with `wget`. This true of both /policies/ and /courses/. I've not found success with feeding an `--input-file` of all /courses/subjects/ANIMA URLs nor with flags like `--include-directories=/courses/` or `--accept-regex=/courses/.*` which in combination with the input file only download the subject pages but none of the courses linked on them. We may need to a giant list of all course, subject, and policy URLs. I compiled the original subjects list by looking at Portal's analytics.

Another alternative; build a simple view in Portal to show the data in a scrapable format, as Eric and Tanza discussed about Showcase. Nick made a good point that we have structured course data in Workday, and anyone could build a frontend, so it is a less high priority project than one saving content not duplicated anywhere else (which is true for policies and showcase).
