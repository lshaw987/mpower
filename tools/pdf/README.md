# MPower free-resource PDFs - the builder

Makes every PDF in `public/resources/pdf/` from HTML. Rebuilt 14 Nov 2026 after the first generator (4 Nov 2026) was lost; the layouts were measured back off those PDFs.

## Run it

From the website folder:

```
python tools/pdf/build.py                      # all eight, written into public/resources/pdf/
python tools/pdf/build.py audit-your-calendar  # just one (any number of slugs)
python tools/pdf/build.py --no-copy            # build into %TEMP%\mpower-pdf-build only, public/ untouched
```

Use `python`, not `python3`. Needs Microsoft Edge (it does the printing) and, for the checks, `pip install pymupdf`.

## What is here

| File | What it is |
|---|---|
| `pdfs.json` | The list of PDFs: slug (= file name), browser-tab title, the top-right tag, expected page count. |
| `pages/<slug>.html` | The words and layout of one PDF. A line with `<!-- pagebreak -->` starts a new page. |
| `pdf.css` | The shared stylesheet. Colours match `src/styles/tokens.css`. |
| `fonts/` | Plus Jakarta Sans, static weights (SIL Open Font Licence, `OFL.txt`). Bundled so a build never needs the internet. |
| `build.py` | Wraps each page in the shared header and footer, prints with headless Edge, checks, copies. |
| `_originals/` | The seven PDFs as they stood on 4 Nov 2026, before this builder overwrote them. Reference only. |

The header (MPower + tag) and the footer (`mpowerhq.nz · askme@mpowerhq.nz · free resource` + page number) are added by `build.py`, so they are the same on every page. To change the footer wording, edit `FOOTER_TEXT` at the top of `build.py` - one place, all PDFs. The self-care menu is landscape and draws its own header and footer; it takes the same footer text through `{{footer}}`.

## Adding a PDF

1. Add a row to `pdfs.json`.
2. Write `pages/<slug>.html`. Copy the nearest existing page - a review, a card worksheet, a checklist.
3. Build it, then look at it (below).
4. Point the article at it with `pdf: "/resources/pdf/<slug>.pdf"` in its front matter under `src/content/resources/`.

## Always look at the pages

The build checks page count, A4 size, that Plus Jakarta Sans embedded, and that the footer email is on every page. It cannot see a clipped line or a paragraph that ran into the footer. Pages are fixed-height sheets, so text that is too long is cut off at the bottom, not pushed to a new page. After any change to the words, render and look:

```
python -c "import pymupdf,sys; d=pymupdf.open(sys.argv[1]); [p.get_pixmap(dpi=110).save(f'page{i+1}.png') for i,p in enumerate(d)]" public/resources/pdf/<slug>.pdf
```

## Known traps on this laptop (already handled in build.py)

- Edge print-to-pdf writes nothing if pointed at the workspace path (spaces and `!`), so the build renders in `%TEMP%\mpower-pdf-build` and copies the result across.
- Edge sometimes exits clean and writes no file. The build retries up to four times and stops loudly if it still has nothing.
- Each print uses its own throwaway Edge profile in `%TEMP%`, removed afterwards. Never put a headless profile in the synced workspace.
- Edge defaults to US Letter. `pdf.css` sets `@page { size: A4 }` and the build checks for it.
- Use the static font files. The variable font prints as nameless glyph shapes and the font check fails.

## Voice rules for anything written here

Plain and speech-shaped. Short dash ` - ` with spaces, never the long em-dash. "Ai", not "AI". No "it's not X, it's Y". No prices, no mention of a trial. Worksheets that go with an article use the article's own words - nothing invented, no new claims, numbers or attributions.
