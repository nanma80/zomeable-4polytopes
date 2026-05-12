"""Update all `output/<slug>/` references to `output/<category>/<slug>/`.

Operates on a curated list of tracked text files.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "output"

REGULARS = {"5cell", "8cell", "16cell", "24cell", "120cell", "600cell"}
CATEGORY_FOLDERS = ["regular", "uniform", "polyhedral_prisms", "duoprisms", "antiprismatic_prisms"]


def categorize(slug: str) -> str:
    if slug in REGULARS:
        return "regular"
    if slug.startswith("duoprism_"):
        return "duoprisms"
    if slug.endswith("_antiprismatic_prism"):
        return "antiprismatic_prisms"
    if slug.endswith("_prism"):
        return "polyhedral_prisms"
    return "uniform"


# Build mapping from physically existing slugs
SLUG_TO_CAT = {}
for cat in CATEGORY_FOLDERS:
    cat_dir = OUT / cat
    if cat_dir.is_dir():
        for sub in cat_dir.iterdir():
            if sub.is_dir():
                SLUG_TO_CAT[sub.name] = cat


def update_text(text: str) -> tuple[str, int]:
    """Replace `output/<slug>/` with `output/<cat>/<slug>/`, in any form."""
    n = 0
    # Sort slugs by length desc so longer slugs match first (avoid "8cell" matching inside "rectified_8cell")
    for slug in sorted(SLUG_TO_CAT.keys(), key=len, reverse=True):
        cat = SLUG_TO_CAT[slug]
        # Use callable replacements to avoid re backreference issues with literal backslashes
        pattern = re.compile(r"(\boutput/)" + re.escape(slug) + r"(?=[/\"'\s\):,)`\\]|$)")
        repl = lambda m, c=cat, s=slug: m.group(1) + c + "/" + s
        text, count = pattern.subn(repl, text)
        n += count
        pattern_win = re.compile(r"(\boutput\\)" + re.escape(slug) + r"(?=[\\\"'\s\):,)`/]|$)")
        repl_win = lambda m, c=cat, s=slug: m.group(1) + c + "\\" + s
        text, count = pattern_win.subn(repl_win, text)
        n += count
    return text, n


def files_to_update():
    """Curated list of tracked files that may contain output/<slug>/ refs."""
    files = []
    # Docs and READMEs
    files.append(REPO / "README.md")
    files.append(REPO / "output" / "README.md")
    files.extend(sorted((REPO / "docs").glob("*.md")))
    # Manifests + logs
    files.append(REPO / "output" / "prismatic_manifest.json")
    files.append(REPO / "output" / "wythoff_sweep_manifest.json")
    files.append(REPO / "ongoing_work" / "prismatic_sweep_log.jsonl")
    # All RESULTS.md and CLASSIFICATION.md etc in the new subfolder hierarchy
    files.extend(sorted(OUT.rglob("RESULTS.md")))
    files.extend(sorted(OUT.rglob("CLASSIFICATION.md")))
    files.extend(sorted(OUT.rglob("ZOMEABLE_PROJECTIONS.md")))
    # Tools
    tools = REPO / "tools"
    for name in [
        "run_prismatic_sweep.py", "build_prismatic_doc.py", "build_prismatic_results.py",
        "emit_novel.py", "audit_kernel_dups.py", "dedup_corpus_by_direction.py",
        "dedup_corpus_by_shape.py", "rename_corpus.py", "rescale_corpus.py",
        "measure_strut_size.py", "run_wythoff_sweep.py", "add_vzome_viewers.py",
    ]:
        p = tools / name
        if p.exists():
            files.append(p)
    # de-dup, keep only existing
    seen = set()
    out = []
    for f in files:
        if f.exists() and f not in seen:
            out.append(f)
            seen.add(f)
    return out


def main():
    print(f"Found {len(SLUG_TO_CAT)} categorized slugs")
    cats = {}
    for slug, cat in SLUG_TO_CAT.items():
        cats[cat] = cats.get(cat, 0) + 1
    print(f"  by category: {cats}")
    files = files_to_update()
    print(f"Scanning {len(files)} files...")
    total = 0
    for f in files:
        try:
            original = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            original = f.read_text(encoding="latin-1")
        updated, n = update_text(original)
        if n:
            f.write_text(updated, encoding="utf-8")
            print(f"  {f.relative_to(REPO)}: {n} replacements")
            total += n
    print(f"\nTotal replacements: {total}")


if __name__ == "__main__":
    main()
