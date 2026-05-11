"""Append a '3D Viewers' section to each output/<polytope>/<RESULTS|CLASSIFICATION|...>.md
that does not already have one, following the pattern Scott introduced in PR #1
for output/5cell/RESULTS.md.

For each subfolder of output/:
  - find the single markdown file
  - if it already contains 'vzome-viewer', skip (already done)
  - else find all .vZome files in the subfolder (sorted by name)
  - append a '## 3D Viewers' section with a <figure>/<vzome-viewer> block per file
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"

SCRIPT_LINE = "<script type='module' src='https://www.vzome.com/modules/vzome-viewer.js'></script>"

def figure_block(fname: str) -> str:
    return (
        '<figure style="width: 800px; margin: 5%">\n'
        f' <vzome-viewer style="width: 100%; height: 500px" src="{fname}" progress="true" >\n'
        ' </vzome-viewer>\n'
        ' <figcaption style="text-align: center; font-style: italic;">\n'
        f'    {fname}\n'
        ' </figcaption>\n'
        '</figure>\n'
    )

def build_section(vzome_files: list[str]) -> str:
    parts = ["## 3D Viewers", "", SCRIPT_LINE, ""]
    for f in vzome_files:
        parts.append(figure_block(f))
    return "\n".join(parts) + "\n"

def process_subfolder(sub: Path) -> tuple[str, int]:
    mds = sorted(sub.glob("*.md"))
    if not mds:
        return ("no-md", 0)
    if len(mds) > 1:
        return (f"multiple-md ({','.join(m.name for m in mds)})", 0)
    md = mds[0]
    text = md.read_text(encoding="utf-8")
    if "vzome-viewer" in text:
        return ("already-has-viewers", 0)
    vzome_files = sorted(p.name for p in sub.glob("*.vZome"))
    if not vzome_files:
        return ("no-vzome", 0)
    section = build_section(vzome_files)
    # ensure a blank line separator
    if not text.endswith("\n"):
        text += "\n"
    if not text.endswith("\n\n"):
        text += "\n"
    text += section
    md.write_text(text, encoding="utf-8")
    return (md.name, len(vzome_files))

if __name__ == "__main__":
    subs = sorted(p for p in OUTPUT.iterdir() if p.is_dir())
    for sub in subs:
        status, n = process_subfolder(sub)
        print(f"{sub.name:<35} -> {status:<25}  ({n} viewer{'s' if n != 1 else ''})")
