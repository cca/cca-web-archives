#!/usr/bin/env node
// Create a stub entry for a domain
import * as fs from 'node:fs/promises'
import * as path from 'node:path'
import * as readline from 'node:readline/promises'
import chalk from 'chalk'

const domain = process.argv[2]
if (!domain) {
  console.error(chalk.red('Provide a domain name, e.g. libraries.cca.edu'))
  process.exit(1)
}

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
})

let template = {
  title: `${domain}`,
  domain: `${domain}`,
  fullUrl: `https://${domain}/index.html`,
  dateArchived: new Date().toISOString().substring(0, 10),
  archiveFormat: 'static-html',
  description: '',
  thumbnailUrl: `thumbnails/${domain}.png`,
  thumbnailAltText: ''
}

// Check for screenshot in Downloads, prompt to move it to thumbnails
async function moveScreenshot() {
  const downloadsDir = path.join(process.env.HOME || process.env.USERPROFILE, 'Downloads',)
  try {
    const files = await fs.readdir(downloadsDir)
    // reverse() should prioritize more recent timestamped screenshots on macOS
    const screenshot = files.reverse().find(
      (file) =>
        file.toLowerCase().includes('screenshot') &&
        file.toLowerCase().endsWith('.png'),
    )
    if (screenshot) {
      console.log(chalk.magenta(`Found a screenshot in your Downloads folder: ${screenshot}`))
      const answer = await rl.question('Would you like to move it to the thumbnails folder? (y/n) ')
      if (answer.toLowerCase() === 'y') {
        const sourcePath = path.join(downloadsDir, screenshot)
        const destPath = path.join('public', 'thumbnails', `${domain}.png`)
        await fs.rename(sourcePath, destPath)
        return console.log(chalk.cyan(`Moved ${sourcePath} to ${destPath}`))
      } else {
        return console.log(chalk.yellow('Ok.'))
      }
    }
  } catch (err) { return console.error(err) }
}

// Write JSON entry
const contentDirPath = path.join('src', 'content', 'archives')
const contentDirStats = await fs.stat(contentDirPath)

if (!contentDirStats.isDirectory()) {
  console.error(chalk.red('Error: src/content/archives is not a directory.'))
  process.exit(1)
}

const jsonPath = path.join(contentDirPath, `${domain}.json`)
fs.stat(jsonPath)
  .then(jsonStats => {
    if (jsonStats.isFile()) {
      console.error(chalk.yellow(`File already exists at ${jsonPath}`))
      return rl.question('Would you like to overwrite it? (y/n) ')
    }
    return 'y'
  })
  .then(answer => {
    if (answer?.toLowerCase() !== 'y') {
      console.log(chalk.yellow('Aborting. No changes were made.'))
      process.exit(0)
    }
    return fs.writeFile(jsonPath, JSON.stringify(template, null, 2))
  })
  .catch(() => {
    // File doesn't exist, proceed with writing
    return fs.writeFile(jsonPath, JSON.stringify(template, null, 2))
  })
  .finally(async () => {
    console.log(chalk.cyan(`Wrote ${jsonPath}`))
    await moveScreenshot()
    rl.close()
  })
