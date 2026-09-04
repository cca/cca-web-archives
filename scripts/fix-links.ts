/* Walk a directory tree looking at .html files for links to other local pages that
are missing the .html extension, e.g. Squarespace summary blocks (blog/news/research
list pages) render item links like /research/2025/5/16/computational-bamboo client-side
from JSON, so wget's --convert-links never sees or rewrites them even though wget did
fetch and save the page as research/2025/5/16/computational-bamboo.html. A plain static
file server has no rewrite rule for extensionless paths, so these links 404 locally
despite the target page existing on disk.
This script finds hrefs where <href>.html exists on disk but <href> itself does not,
and appends the .html extension so the link resolves locally.
*/
import { access, readdir, readFile, writeFile } from 'node:fs/promises'
import { Dirent } from 'node:fs'
import * as path from 'node:path'
import * as cheerio from 'cheerio'

const FILE_CONCURRENCY: number = Number(process.env.FILE_CONCURRENCY) || 8

let numHtmlFiles: number = 0
let numLinksFixed: number = 0
let numHtmlFilesModified: number = 0
const root: string = process.argv[2]

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
  console.log(`Fixed ${numLinksFixed} links missing a .html extension.`)
  console.log(`Modified ${numHtmlFilesModified} HTML files.`)
}

async function pool<T>(items: T[], limit: number, worker: (item: T) => Promise<void>): Promise<void> {
  let next: number = 0
  const runners: Promise<void>[] = Array.from({ length: Math.min(limit, items.length) }, async () => {
    while (next < items.length) await worker(items[next++])
  })
  await Promise.all(runners)
}

function isHtmlFile(file: Dirent<string>): boolean {
  return file.isFile() && file.name.endsWith('.html')
}

async function fileExists(filePath: string): Promise<boolean> {
  return access(filePath).then(() => true, () => false)
}

// only rewrite same-site links to a page, not anchors, external URLs, or files that
// already have an extension (images, PDFs, etc. don't need one appended)
function isFixableHref(href: string | undefined): href is string {
  if (!href) return false
  if (!href.startsWith('/')) return false
  if (href === '/') return false
  const withoutQuery: string = href.split(/[?#]/)[0]
  if (withoutQuery.endsWith('/')) return false
  return !path.extname(withoutQuery)
}

async function processHtmlFile(file: Dirent<string>, dirRoot: string): Promise<void> {
  const filePath: string = path.join(file.parentPath, file.name)
  const htmlContent: string = await readFile(filePath, 'utf-8')
  const $ = cheerio.load(htmlContent, { scriptingEnabled: false })

  const anchors = $('a[href]').toArray().filter(element => isFixableHref($(element).attr('href')))
  if (!anchors.length) return

  const rewrites = await Promise.all(
    anchors.map(async element => {
      const href: string = $(element).attr('href')!
      const withoutQuery: string = href.split(/[?#]/)[0]
      const suffix: string = href.slice(withoutQuery.length)
      const destination: string = path.join(dirRoot, `${withoutQuery}.html`)
      const fixable: boolean = (await fileExists(destination)) && !(await fileExists(path.join(dirRoot, withoutQuery)))
      return { element, newHref: `${withoutQuery}.html${suffix}`, fixable }
    })
  )

  let modified: boolean = false
  for (const { element, newHref, fixable } of rewrites) {
    if (!fixable) continue
    $(element).attr('href', newHref)
    modified = true
    numLinksFixed++
  }
  if (!modified) return

  // don't clobber a backup from an earlier run (e.g. squarespace.ts)
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
    await processHtmlFile(file, root)
  } catch (error) {
    console.error(`Error processing ${file.name}:`, error)
  }
})

summarize()
