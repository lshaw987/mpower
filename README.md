# MPower website

The marketing + pre-launch waitlist site for MPower. Live domain: **mpowerhq.nz**
(`mpowerhq.com` + `mpowerhq.co.nz` registered and 301 to it). Built in
[Astro](https://astro.build) - static output, no JS framework, ships as plain
HTML/CSS with a sprinkle of vanilla JS (mobile nav) plus the Klaviyo onsite
script.

> Source of truth for all brand/content decisions:
> `layer-4-brains/mpower/context/brand-architecture.md` (absorbs the 18 May
> 2026 Brand & Content Spec + Lisa's reconciliation calls). `mpower.nz` is an
> aspirational future domain only - the site stays on `mpowerhq.nz`.

---

## Getting started

```bash
npm install
npm run dev                # http://localhost:4321
npm run build              # outputs to ./dist
npm run preview            # serve the build locally
```

No environment variables are required to build or run the site.

## Project structure

```
├── astro.config.mjs       # site URL (https://mpowerhq.nz), sitemap, build
├── vercel.json            # Vercel build + redirects + cache headers
├── public/                # favicon.svg, og-default.png, robots.txt
└── src/
    ├── layouts/Base.astro     # <head>, Nav, Footer, Klaviyo onsite script
    ├── components/            # Nav, Footer, Wordmark, GreenBlock, VerticalCard
    ├── pages/                 # one .astro = one URL
    └── styles/tokens.css      # brand tokens (colours, type, spacing)
        styles/global.css      # reset + type primitives + utilities
```

## Brand

All brand decisions are CSS variables in `src/styles/tokens.css`. Never
hard-code a colour or font-size in a component - pull from a token.

- Parent base: Deep Sea `#0F1922`, Steel `#18222D`, Spring green `#4ADE80`
- Each vertical owns four colour roles - Accent · Ink · Deep · Light:
  Agri (Clay), Ed (Indigo), Teams (Bronze), Leaders (Violet), Rising (Cyan)
- Type: Plus Jakarta Sans (display + body) + JetBrains Mono (mono labels)
- Voice rule: no em-dashes anywhere - use the spaced short dash ` - `

## The waitlist (Klaviyo - embedded form)

The `/waitlist` page mounts an **embedded Klaviyo form**: a single
`<div class="klaviyo-form-W2JdnP"></div>`. It is powered by the Klaviyo
onsite script (company `SKABCW`) loaded before `</body>` in
`src/layouts/Base.astro`.

- The form fields, validation, success state, double opt-in and list
  assignment are all configured **in Klaviyo**, not in this repo.
- No `PUBLIC_KLAVIYO_*` env vars, no custom Client-API submit script, no
  Vercel environment variables needed. (This replaces the old approach.)
- To change the form, edit it in Klaviyo. To change where it appears, move
  the div. To change the account, change `company_id=SKABCW` in `Base.astro`.

## Deploy - Vercel

Static output, no serverless functions, no adapter. Repo
`github.com/lshaw987/mpower`, `main` = live. Deploy process:
`layer-4-brains/mpower/skills/deploy-website.md`. Never push without Lisa's
explicit go.

### Custom domains (Vercel → Project → Settings → Domains)

- `mpowerhq.nz` (primary)
- `www.mpowerhq.nz` → redirect to apex
- `mpowerhq.com` → redirect to `mpowerhq.nz`
- `mpowerhq.co.nz` → redirect to `mpowerhq.nz`

DNS: `A @ 76.76.21.21`, `CNAME www cname.vercel-dns.com`. NZ domains via an
InternetNZ reseller.

## Sub-domain verticals

Phase 1: `agri.mpowerhq.nz` and `ed.mpowerhq.nz`. The homepage and Verticals
page link to those directly. MPower Teams routes to `askme@mpowerhq.nz`
(by arrangement, no subdomain). Leaders + Rising are coming soon (no
subdomain yet - open decision). Recommendation: spin the live subdomains up
as separate Astro projects sharing this `tokens.css` and components.

## Stories

`src/pages/stories.astro` is an **honest holding page** - we are pre-launch
and do not invent member stories. Real member stories land there after
launch, with permission. No Storyblok wiring is needed until there is real
content to manage.

## Accessibility + performance

Skip link; focus-visible rings; `prefers-reduced-motion` honoured; reading
order matches visual order; type scales are clamps; fonts load with
`display=swap`; no client-side framework. Modern evergreen browsers; Mobile
Safari 14+ / Android Chrome 90+.
