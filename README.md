# MPower website

The marketing + pre-launch waitlist site for MPower (mpowerhq.co.nz, .nz, .com).
Built in [Astro](https://astro.build) — static output, no JS framework, ships
as plain HTML/CSS with a sprinkle of vanilla JS where needed (mobile nav,
waitlist form submit).

---

## Getting started

```bash
cd site
npm install
cp .env.example .env       # then fill in your Klaviyo keys
npm run dev                # http://localhost:4321
```

To produce a production build:

```bash
npm run build              # outputs to ./dist
npm run preview            # serve the build locally
```

## Project structure

```
site/
├── astro.config.mjs       # Astro config — site URL, sitemap, build options
├── vercel.json            # Vercel build + redirects + cache headers
├── public/                # Static assets served as-is
│   ├── favicon.svg
│   ├── og-default.png     # 1200×630 social card
│   └── robots.txt
└── src/
    ├── layouts/
    │   └── Base.astro     # <head>, Nav, Footer wrapper
    ├── components/
    │   ├── Nav.astro
    │   ├── Footer.astro
    │   ├── Wordmark.astro
    │   ├── GreenBlock.astro
    │   └── VerticalCard.astro
    ├── pages/             # File-system routing — one .astro file = one URL
    │   ├── index.astro
    │   ├── about.astro
    │   ├── verticals.astro
    │   ├── how-it-works.astro
    │   ├── stories.astro
    │   └── waitlist.astro
    └── styles/
        ├── tokens.css     # CSS custom properties — colors, type, spacing
        └── global.css     # Reset + type primitives + utilities
```

## Brand

All brand decisions are encoded as CSS variables in `src/styles/tokens.css`.
Never hard-code a colour or font-size in a component — pull from a token.

- Parent base: Deep Sea `#0B1620` with Spring green `#4ADE80` as the only accent
- Sub-brand accents (Agri = Clay, Ed = Indigo) come from the same file
- Type: Plus Jakarta Sans (display + body) + JetBrains Mono (mono labels)

## The waitlist (Klaviyo)

The form on `/waitlist` submits client-side to Klaviyo's Client API. No
server, no serverless function. Two values needed (both public, safe to
ship to the browser):

1. **Public Company ID** — Account → Settings → API Keys → "Public API Key"
2. **List ID** — Lists & Segments → create "MPower Waitlist" → copy from URL

Drop them in `.env` (and into your host's environment variables). The form
captures: name, email, audience type, which vertical(s) they're interested
in, optional note, and the source. All become Klaviyo profile properties so
you can segment campaigns by Agri-only / Ed-only / both.

### What the form sends

```json
{
  "audience": "Individual" | "Organisation" | "Community" | "Funder / Partner",
  "verticals": ["Agri", "Ed"],
  "name": "...",
  "email": "...",
  "note": "...",
  "source": "mpowerhq.co.nz/waitlist"
}
```

If keys are not configured the script logs the payload and shows the
success state — useful for design review without hitting Klaviyo.

## Deploy — Vercel

The site is configured for **Vercel** out of the box (`vercel.json` at the
repo root sets the build command, output directory, security headers, and a
few redirects). Static output — no serverless functions, no adapter.

### One-time setup

1. Push `site/` to a GitHub repo (e.g. `mpower/website`). If you keep the
   repo wider than just `site/`, set the **Root Directory** in Vercel to
   `site` so it builds from the right place.
2. [vercel.com/new](https://vercel.com/new) → import the repo. Vercel
   auto-detects Astro:
   - Framework preset: **Astro**
   - Build command: `npm run build`
   - Output directory: `dist`
   - Install command: `npm install`
3. Add environment variables (Project → Settings → Environment Variables).
   Apply each to **Production**, **Preview**, **Development**:
   - `PUBLIC_KLAVIYO_COMPANY_ID` — six-character public API key
   - `PUBLIC_KLAVIYO_LIST_ID` — six-character list ID
4. Click **Deploy**. First build takes ~30 seconds. Every push to `main`
   re-deploys automatically; PRs get preview URLs.

### Custom domains

Vercel → Project → Settings → Domains. Add all three and let Vercel
manage SSL:

- `mpowerhq.co.nz` (primary)
- `www.mpowerhq.co.nz` → redirect to apex
- `mpowerhq.nz` → redirect to `mpowerhq.co.nz`
- `mpowerhq.com` → redirect to `mpowerhq.co.nz`

DNS records Vercel will ask for:

| Type  | Name | Value                  |
|-------|------|------------------------|
| A     | `@`  | `76.76.21.21`          |
| CNAME | `www`| `cname.vercel-dns.com` |

NZ domains are registered through [Internet NZ
resellers](https://internetnz.nz/) — point each domain's nameservers (or
A/CNAME records) at the values above.

### Local development

```bash
cd site
npm install
cp .env.example .env       # then fill in your Klaviyo keys
npm run dev                # http://localhost:4321
npm run build && npm run preview   # production build, served locally
```

### Other hosts (if you ever switch)

The build also works as-is on **Cloudflare Pages** and **Netlify** —
framework preset Astro, build `npm run build`, publish `dist`. Same env
vars. The `vercel.json` is ignored by both.

## Storyblok (later, for Stories)

The Stories page (`src/pages/stories.astro`) currently uses a hand-coded
array at the top of the file. To swap in Storyblok:

1. `npm install @storyblok/astro`
2. Add the integration to `astro.config.mjs` with your space token
3. Replace the `stories` const with a `useStoryblokApi()` fetch of the
   `stories` content type — keep the same field names (slug, vertical,
   accent, location, title, lede, readMinutes, featured) and the page
   keeps rendering unchanged.

Individual story pages aren't built yet — when Storyblok is wired in,
add `src/pages/stories/[slug].astro` as the dynamic detail route.

## Sub-domain verticals

Phase 1 has two: `agri.mpowerhq.co.nz` and `ed.mpowerhq.co.nz`. The
homepage and Verticals page link to those directly. Recommendation:
spin them up as separate Astro projects sharing the same `tokens.css`
and components, so each vertical's team can iterate without touching
the parent site.

## Accessibility + performance notes

- Skip link wired up
- Focus-visible rings on brand
- `prefers-reduced-motion` honoured
- Reading order matches visual order on every page
- Type scales are clamps — no media queries needed for typography
- All fonts loaded with `display=swap`
- No client-side framework — pages ship as static HTML

## Browser support

Modern evergreen — last 2 versions of Chrome/Edge/Firefox/Safari. IE not
supported. Mobile Safari 14+ and Android Chrome 90+ cover effectively
100% of NZ traffic.
