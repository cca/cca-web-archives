import { defineCollection } from 'astro:content'
import { z } from 'astro/zod'
import { glob } from 'astro/loaders'

const archives = defineCollection({
  loader: glob({ pattern: '**/[^_]*.json', base: './src/content/archives' }),
  schema: z.object({
    title: z.string(),
    domain: z.string(),
    fullUrl: z.string().url(),
    dateArchived: z.string().transform((str) => new Date(str)),
    archiveFormat: z.enum(['static-html', 'warc', 'other', 'internet-archive']),
    description: z.string(),
    // We can't use .url() because some are relative paths to local thumbnails
    thumbnailUrl: z.string().optional(),
    thumbnailAltText: z.string().optional(),
  }),
});

export const collections = {
  archives,
}
