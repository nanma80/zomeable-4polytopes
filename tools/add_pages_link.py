"""Insert a 'View on GitHub Pages' link directly under each '## 3D Viewers'
heading in every output/<polytope>/*.md file.

The link target is an absolute URL on the upstream GitHub Pages site so it
also works when the markdown is rendered on github.com.  This means the
owner ('nanma80') is hardcoded; forks of this repo need to either:

  - edit PAGES_BASE below and re-run this script, or
  - rely on relative '<name>.html' (set HARDCODE_OWNER = False).

Idempotent — re-running on a file that already has the link makes no change.
To refresh links after toggling HARDCODE_OWNER or changing PAGES_BASE, run
with --force to strip the existing link block and re-insert.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"

VIEWERS_HEADING = "## 3D Viewers"
LINK_MARKER = "_3d-viewer-html-link_"  # comment marker for idempotence
HARDCODE_OWNER = True
PAGES_BASE = "https://nanma80.github.io/zomeable-4polytopes"

def link_html(md: Path) -> str:
    rel_html = md.relative_to(ROOT).with_suffix(".html").as_posix()
    if HARDCODE_OWNER:
        target = f"{PAGES_BASE}/{rel_html}"
    else:
        target = md.with_suffix(".html").name
    return (
        f"<!-- {LINK_MARKER} -->\n"
        f"➡️ **[Open this page on GitHub Pages]({target})** to interact with "
        f"the 3D models below (the embeds only render when this file is "
        f"served via GitHub Pages, not in github.com's markdown preview).\n"
    )

def strip_existing(text: str) -> str:
    """Remove an existing link block (marker comment + following link line +
    one trailing blank line if present)."""
    marker = f"<!-- {LINK_MARKER} -->"
    if marker not in text:
        return text
    lines = text.splitlines(keepends=True)
    out, skip = [], 0
    for i, line in enumerate(lines):
        if skip > 0:
            skip -= 1
            continue
        if marker in line:
            # Skip marker line + next non-empty line (the link itself).
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            # j now points at the link line; skip it too if it's a link line.
            if j < len(lines) and lines[j].lstrip().startswith("➡️"):
                skip = (j - i) + 1 - 1   # we already 'continue' for i
                # also drop a trailing blank
                if j + 1 < len(lines) and lines[j + 1].strip() == "":
                    skip += 1
            else:
                skip = (j - i) - 1
            continue
        out.append(line)
    return "".join(out)

def process(md: Path, force: bool = False) -> str:
    text = md.read_text(encoding="utf-8")
    if LINK_MARKER in text:
        if not force:
            return "already-has-link"
        text = strip_existing(text)
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
            out.append(link_html(md))
            out.append("\n")
            inserted = True
    md.write_text("".join(out), encoding="utf-8")
    return "added"

if __name__ == "__main__":
    force = "--force" in sys.argv
    for sub in sorted(p for p in OUTPUT.iterdir() if p.is_dir()):
        mds = sorted(sub.glob("*.md"))
        for md in mds:
            status = process(md, force=force)
            print(f"{sub.name:<32} {md.name:<28} -> {status}")
