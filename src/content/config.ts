import { defineCollection, z } from 'astro:content';

/**
 * Free resources - the small public sample of the member library.
 * One markdown file per piece in src/content/resources/. The body is the
 * piece itself; the front matter below is what the index cards and the
 * detail page read. `order` drives the sort everywhere (index, prev/next).
 */
const resources = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    summary: z.string(),
    format: z.enum(['Guide', 'Template', 'Read', 'Review']),
    theme: z.enum(['Self care', 'Your week', 'Leading', 'Growth']),
    source: z.string(),
    pdf: z.string().optional(),
    readingTime: z.number(),
    order: z.number(),
    // Tile + hero photo: /images/resources/<slug>.jpg (1200w max, q80). Optional - a
    // piece with no image gets the Deep Sea panel with its format glyph on the index
    // and no hero band on its page. Book covers are portrait and render as a centred cover.
    image: z.string().optional(),
    imageAlt: z.string().optional(),
    book: z
      .object({
        title: z.string(),
        author: z.string(),
      })
      .optional(),
  }),
});

export const collections = { resources };
