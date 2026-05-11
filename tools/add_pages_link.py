"""Insert a 'View on GitHub Pages' link directly under each '## 3D Viewers'
heading in every output/<polytope>/*.md file.

The link target is a relative .html with the same name as the markdown file
(GitHub Pages auto-converts foo.md -> foo.html via Jekyll). No owner /
account name is hardcoded: forks of this repo work without edits.

Idempotent — re-running on a file that already has the link makes no change.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"

VIEWERS_HEADING = "## 3D Viewers"
LINK_MARKER = "_3d-viewer-html-link_"  # comment marker for idempotence

def link_html(md_name: str) -> str:
    target = md_name[:-3] + ".html"   # foo.md -> foo.html
    return (
        f"<!-- {LINK_MARKER} -->\n"
        f"➡️ **[Open this page on GitHub Pages]({target})** to interact with "
        f"the 3D models below (the embeds only render when this file is "
        f"served via GitHub Pages, not in github.com's markdown preview).\n"
    )

def process(md: Path) -> str:
    text = md.read_text(encoding="utf-8")
    if LINK_MARKER in text:
        return "already-has-link"
    if VIEWERS_HEADING not in text:
        return "no-viewers-section"
    # Insert link right after the heading line.
    lines = text.splitlines(keepends=True)
    out = []
    inserted = False
    for line in lines:
        out.append(line)
        if not inserted and line.rstrip("\r\n") == VIEWERS_HEADING:
            # ensure exactly one blank line then the link block then one blank line
            if not (out and out[-1].endswith("\n")):
                out.append("\n")
            out.append("\n")
            out.append(link_html(md.name))
            out.append("\n")
            inserted = True
    md.write_text("".join(out), encoding="utf-8")
    return "added"

if __name__ == "__main__":
    for sub in sorted(p for p in OUTPUT.iterdir() if p.is_dir()):
        mds = sorted(sub.glob("*.md"))
        for md in mds:
            status = process(md)
            print(f"{sub.name:<32} {md.name:<28} -> {status}")
