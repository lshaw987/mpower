"""Build the MPower free-resource PDFs.

    python tools/pdf/build.py                 # build all, write into public/resources/pdf/
    python tools/pdf/build.py self-care-menu  # build one (or several) by slug
    python tools/pdf/build.py --no-copy       # build into the temp folder only, touch nothing in public/

How it works: pdfs.json lists each PDF. pages/<slug>.html holds the words and layout for
that PDF (pages split by a line containing <!-- pagebreak -->). This script wraps each page
in the shared header and footer, writes one HTML file per PDF into a temp folder beside a
copy of pdf.css and fonts/, prints it with headless Microsoft Edge, checks the result
(page count, page size, fonts, footer email), then copies it into public/resources/pdf/.

Rendering happens in %TEMP% on purpose: Edge print-to-pdf fails silently when it writes into
the workspace path (spaces and "!"), and headless profiles must never sit in a synced folder.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE.parent.parent / "public" / "resources" / "pdf"
WORK = Path(tempfile.gettempdir()) / "mpower-pdf-build"

FOOTER_TEXT = "mpowerhq.nz · hello@mpowerhq.nz · free resource"
EMAIL = "hello@mpowerhq.nz"

EDGE_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

SHELL = """<!doctype html>
<html lang="en-NZ">
<head>
<meta charset="utf-8">
<title>{title}</title>
<link rel="stylesheet" href="pdf.css">
</head>
<body>
{body}
</body>
</html>
"""

BRAND = '<div class="brand"><b>M</b>Power</div>'


def find_edge():
    for c in EDGE_CANDIDATES:
        if os.path.exists(c):
            return c
    sys.exit("Microsoft Edge not found - edit EDGE_CANDIDATES in build.py")


def compose(item):
    """Turn pages/<slug>.html into a full HTML document."""
    src = (HERE / "pages" / f"{item['slug']}.html").read_text(encoding="utf-8")
    chunks = [c.strip() for c in src.split("<!-- pagebreak -->")]
    total = len(chunks)
    pages = []
    for n, chunk in enumerate(chunks, 1):
        chunk = chunk.replace("{{footer}}", FOOTER_TEXT).replace("{{brand}}", BRAND)
        if item.get("layout") == "bare":
            # the page draws its own header and footer (self-care menu, landscape)
            pages.append(f'<section class="page {item.get("page_class", "")}">\n{chunk}\n</section>')
            continue
        pages.append(
            f'<section class="page">\n'
            f'<div class="hdr">{BRAND}<div class="tag">{item["tag"]}</div></div>\n'
            f'<div class="content {item.get("content_class", "")}">\n{chunk}\n</div>\n'
            f'<div class="ftr"><span>{FOOTER_TEXT}</span><span>page {n}/{total}</span></div>\n'
            f'</section>'
        )
    return SHELL.format(title=item["title"], body="\n".join(pages)), total


def print_pdf(edge, html_path, pdf_path):
    """Headless Edge print-to-pdf, with retries - the CLI sometimes exits 0 and writes nothing."""
    uri = html_path.resolve().as_uri()  # proper file:///C:/... form; plain paths fail silently
    for attempt in range(1, 5):
        profile = Path(tempfile.mkdtemp(prefix="mpower-pdf-edge-"))
        if pdf_path.exists():
            pdf_path.unlink()
        cmd = [
            edge, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
            f"--user-data-dir={profile}", "--virtual-time-budget=8000",
            "--no-pdf-header-footer", f"--print-to-pdf={pdf_path}", uri,
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        except subprocess.TimeoutExpired:
            pass
        for _ in range(20):  # the file can land a moment after the process returns
            if pdf_path.exists() and pdf_path.stat().st_size > 5000:
                break
            time.sleep(0.25)
        shutil.rmtree(profile, ignore_errors=True)
        if pdf_path.exists() and pdf_path.stat().st_size > 5000:
            return
        print(f"    attempt {attempt}: Edge wrote nothing, trying again")
        time.sleep(2)
    sys.exit(f"Edge did not produce {pdf_path.name} after 4 tries")


def check(item, pdf_path, expected_pages):
    """Cheap checks that catch the known traps. Not a substitute for looking at the pages."""
    try:
        import pymupdf
    except ImportError:
        print("    (pymupdf not installed - skipped checks; pip install pymupdf)")
        return []
    problems = []
    doc = pymupdf.open(pdf_path)
    if len(doc) != expected_pages:
        problems.append(f"{len(doc)} pages, expected {expected_pages}")
    landscape = item.get("page_class") == "land"
    for i, page in enumerate(doc, 1):
        w, h = round(page.rect.width), round(page.rect.height)
        want = (842, 595) if landscape else (595, 842)
        if (w, h) != want:
            problems.append(f"page {i} is {w}x{h}pt, expected {want[0]}x{want[1]} (A4)")
        text = page.get_text()
        if EMAIL not in text:
            problems.append(f"page {i} has no {EMAIL}")
        if "ERR_" in text or "file:///" in text:
            problems.append(f"page {i} looks like a browser error page")
        fonts = {f[3] for f in page.get_fonts()}
        if not fonts or not all("PlusJakartaSans" in f for f in fonts):
            problems.append(f"page {i} fonts are {sorted(fonts)} - Plus Jakarta Sans did not load")
    return problems


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    no_copy = "--no-copy" in sys.argv
    items = json.loads((HERE / "pdfs.json").read_text(encoding="utf-8"))
    if args:
        unknown = set(args) - {i["slug"] for i in items}
        if unknown:
            sys.exit(f"unknown slug(s): {', '.join(sorted(unknown))}")
        items = [i for i in items if i["slug"] in args]

    edge = find_edge()
    WORK.mkdir(parents=True, exist_ok=True)
    shutil.copy2(HERE / "pdf.css", WORK / "pdf.css")
    shutil.copytree(HERE / "fonts", WORK / "fonts", dirs_exist_ok=True)

    failed = False
    for item in items:
        slug = item["slug"]
        html, total = compose(item)
        html_path = WORK / f"{slug}.html"
        pdf_path = WORK / f"{slug}.pdf"
        html_path.write_text(html, encoding="utf-8")
        print(f"{slug}: printing {total} page(s)")
        print_pdf(edge, html_path, pdf_path)
        problems = check(item, pdf_path, item.get("pages", total))
        for p in problems:
            print(f"    PROBLEM: {p}")
        if problems:
            failed = True
            continue
        if not no_copy:
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(pdf_path, OUT_DIR / f"{slug}.pdf")
            print(f"    ok -> public/resources/pdf/{slug}.pdf")
        else:
            print(f"    ok -> {pdf_path}")
    if failed:
        sys.exit("Some PDFs failed their checks and were NOT copied. Fix and re-run.")
    print("Done. Now look at the pages - see README.md.")


if __name__ == "__main__":
    main()
