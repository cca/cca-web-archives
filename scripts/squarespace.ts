/* Walk a directory tree looking at .html files for Squarespace CDN images like the below:
<img data-src="https://images.squarespace-cdn.com/content/v1/5a14a0cff9a61e9beda498ad/1567790492156-G2995PQDAJ8LMN2Y6BK9/buoyant+ecologies+float+lab31.png" data-image="https://images.squarespace-cdn.com/content/v1/5a14a0cff9a61e9beda498ad/1567790492156-G2995PQDAJ8LMN2Y6BK9/buoyant+ecologies+float+lab31.png" data-image-dimensions="2400x1350" data-image-focal-point="0.364,0.6085992907801419" alt="Buoyant Ecologies Float Lab"  data-load="false" class="summary-thumbnail-image" elementtiming="summary-thumbnail-image-autogrid" />
Then a tripartite operation:
- Download the image to a local directory
- Backup the original HTML file
- Replace the Squarespace CDN image URL with the local image path in the HTML file
*/
import { access, mkdir, readdir, readFile, writeFile } from 'node:fs/promises'
import { Dirent } from 'node:fs'
import * as path from 'node:path'
import * as cheerio from 'cheerio'

// how many files/images we work on at the same time
const FILE_CONCURRENCY: number = Number(process.env.FILE_CONCURRENCY) || 8
const IMAGE_CONCURRENCY: number = Number(process.env.IMAGE_CONCURRENCY) || 8

let numImages: number = 0
let numImagesDownloaded: number = 0
let numImageDownloadErrors: number = 0
let numHtmlFiles: number = 0
let numHtmlFilesModified: number = 0
const root: string = process.argv[2]
// images are mirrored under <root>/squarespacecdn/
const imageDir: string = 'squarespacecdn'
const cdnHost: string = 'images.squarespace-cdn.com'
// for sanity check that all image path prefixes are the same across a site
// like /content/v1/5a14a0cff9a61e9beda498ad/ in the example above
const imagePathPrefix: RegExp = /\/content\/v1\/([0-9a-f]{24})\//
let imagePathUuid: string

if (!root) {
  console.error('Please provide a root directory path as an argument.')
  process.exit(1)
}

function debug(...args: unknown[]): void {
  if (process.env.DEBUG === 'true') console.log(...args)
}

function summarize(): void {
  console.log('========= Summary =========')
  console.log(`Processed ${numHtmlFiles} HTML files.`)
  console.log(`Found ${numImages} images referencing the Squarespace CDN.`)
  console.log(`Downloaded ${numImagesDownloaded} images.`)
  console.log(`Encountered ${numImageDownloadErrors} image download errors.`)
  console.log(`Modified ${numHtmlFilesModified} HTML files.`)
}

// run worker over items with at most `limit` in flight, resolves when all are done
async function pool<T>(items: T[], limit: number, worker: (item: T) => Promise<void>): Promise<void> {
  let next: number = 0
  const runners: Promise<void>[] = Array.from({ length: Math.min(limit, items.length) }, async () => {
    while (next < items.length) await worker(items[next++])
  })
  await Promise.all(runners)
}

// global cap on in-flight downloads, independent of how many files are open
class Semaphore {
  private available: number
  private waiting: (() => void)[] = []

  constructor(limit: number) {
    this.available = limit
  }

  async run<T>(fn: () => Promise<T>): Promise<T> {
    if (this.available === 0) {
      await new Promise<void>(resolve => {
        this.waiting.push(resolve)
      })
    } else {
      this.available--
    }

    try {
      return await fn()
    } finally {
      const next = this.waiting.shift()
      if (next) next()
      else this.available++
    }
  }
}

const imageSemaphore: Semaphore = new Semaphore(IMAGE_CONCURRENCY)
// the same image often appears across many pages, only fetch it once
const downloads = new Map<string, Promise<boolean>>()

debug(`Starting at ${root}, processing ${FILE_CONCURRENCY} files at a time and downloading ${IMAGE_CONCURRENCY} images concurrently.`)

// absolute destination for a CDN url, with the /content/v1/<uuid>/ prefix stripped
function localPath(url: URL): string {
  const relative = decodeURIComponent(url.pathname).replace(imagePathPrefix, '').replace(/^\/+/, '')
  return path.join(root, imageDir, ...relative.split('/'))
}

// resolves true when the image is available locally
function downloadImage(url: URL, destination: string): Promise<boolean> {
  const existing: Promise<boolean> | undefined = downloads.get(destination)
  if (existing) return existing
  const download: Promise<boolean> = (async () => {
    // already mirrored by an earlier run, no network request needed
    const onDisk: boolean = await access(destination).then(() => true, () => false)
    if (onDisk) {
      debug(`Already on disk: ${destination}`)
      return true
    }
    return imageSemaphore.run(async () => {
      try {
        const response = await fetch(url)
        if (!response.ok) throw new Error(`Failed to download image: ${response.statusText}`)
        const body = Buffer.from(await response.arrayBuffer())
        await mkdir(path.dirname(destination), { recursive: true })
        await writeFile(destination, body)
        numImagesDownloaded++
        return true
      } catch (error) {
        console.error(`Error downloading image from ${url}:`, error)
        numImageDownloadErrors++
        return false
      }
    })
  })()
  downloads.set(destination, download)
  return download
}

function isHtmlFile(file: Dirent<string>): boolean {
  return file.isFile() && file.name.endsWith('.html')
}

function checkImagePathPrefix(src: string): void {
  const match = src.match(imagePathPrefix)
  if (match) {
    const uuid = match[1]
    if (!imagePathUuid) {
      imagePathUuid = uuid
    } else if (imagePathUuid !== uuid) {
      console.warn(`Warning: Found different UUIDs in image paths: ${imagePathUuid} and ${uuid}`)
    }
  } else {
    console.warn(`Warning: image src does not match expected pattern: ${src}`)
  }
}

const imageAttributes: string[] = ['src', 'data-src', 'data-image', 'srcset', 'data-srcset', 'href']

// Squarespace hides images until its loader adds .loaded and hides blocks with
// data-animation-role until its animation observer runs, so force both visible
const visibilityFix: string = 'img,[data-animation-role]{opacity:1!important;visibility:visible!important}'

function cdnUrl(value: string | undefined): URL | undefined {
  if (!value) return undefined
  try {
    const url = new URL(value, `https://${cdnHost}`)
    return url.hostname === cdnHost ? url : undefined
  } catch {
    return undefined
  }
}

// srcset candidates are "url 750w", we only want the url
function firstCdnUrl(values: (string | undefined)[]): URL | undefined {
  for (const value of values) {
    for (const candidate of (value ?? '').split(',')) {
      const url = cdnUrl(candidate.trim().split(/\s+/)[0])
      if (url) return url
    }
  }
  return undefined
}

async function processHtmlFile(file: Dirent<string>): Promise<void> {
  const filePath: string = path.join(file.parentPath, file.name)
  const htmlContent: string = await readFile(filePath, 'utf-8')
  // scriptingEnabled: false parses <noscript> fallbacks as elements instead of text
  const $ = cheerio.load(htmlContent, { scriptingEnabled: false })
  // anchors are gallery lightbox links to the full size original
  const images = $('img, source, a')
    .toArray()
    .map(element => ({ element, url: firstCdnUrl(imageAttributes.map(attr => $(element).attr(attr))) }))
    .filter((entry): entry is { element: typeof entry.element; url: URL } => Boolean(entry.url))
  if (!images.length) return
  numImages += images.length

  // images in a file download in parallel, throttled by the shared semaphore
  const rewrites = await Promise.all(
    images.map(async ({ element, url }) => {
      // sanity check that all image path prefixes are the same across a site
      checkImagePathPrefix(url.pathname)
      const destination: string = localPath(url)
      const ok: boolean = await downloadImage(url, destination)
      const href: string = path.relative(file.parentPath, destination).split(path.sep).join('/')
      return { element, href, ok }
    })
  )

  const targetAttribute: Record<string, string> = { a: 'href', source: 'srcset', img: 'src' }
  let modified: boolean = false
  for (const { element, href, ok } of rewrites) {
    if (!ok) continue
    // Squarespace's image loader resolves a relative data-src against the CDN, so
    // strip everything that lets the JS rewrite the element and mark it already loaded
    $(element)
      .attr(targetAttribute[element.tagName], href)
      .removeAttr('data-src')
      .removeAttr('data-image')
      .removeAttr('data-image-id')
      .removeAttr('data-load')
      .removeAttr('data-srcset')
      .removeAttr('sizes')
      .removeAttr('elementtiming')
    if (element.tagName === 'img') {
      $(element)
        .removeAttr('srcset')
        .addClass('loaded')
        .data('loaded', true)
    }
    modified = true
  }
  if (!modified) return

  if (!$('#squarespace-mirror-fix').length) $('head').append(`<style id="squarespace-mirror-fix">${visibilityFix}</style>`)

  // don't clobber a backup from an earlier run
  try {
    await writeFile(`${filePath}.bak`, htmlContent, { flag: 'wx' })
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code !== 'EEXIST') throw error
  }
  await writeFile(filePath, $.html(), 'utf-8')
  numHtmlFilesModified++
}

const entries: Dirent<string>[] = await readdir(root, { withFileTypes: true, recursive: true })
const htmlFiles: Dirent<string>[] = entries.filter(isHtmlFile)
numHtmlFiles = htmlFiles.length

await pool(htmlFiles, FILE_CONCURRENCY, async file => {
  debug(`Processing HTML file: ${file.name}`)
  try {
    await processHtmlFile(file)
  } catch (error) {
    console.error(`Error processing ${file.name}:`, error)
  }
})

summarize()
