import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  // Live domain is mpowerhq.nz (held - mpower.nz is aspirational only,
  // per the 18 May 2026 spec reconciliation). Must match the real deploy
  // domain or sitemap/canonical/OG URLs point at a dead host.
  site: 'https://mpowerhq.nz',
  // Static output by default — Vercel auto-detects Astro and serves
  // `dist/` from its global edge CDN. No adapter needed.
  integrations: [
    sitemap({
      // Drop the waitlist confirmation noise; everything else is fair game.
      filter: (page) => !page.includes('/waitlist?'),
    }),
  ],
  build: {
    // Inline tiny stylesheets to save HTTP round-trips on patchy data.
    inlineStylesheets: 'auto',
  },
});
