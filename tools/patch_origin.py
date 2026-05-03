"""One-shot: inject `<SelectManifestation point="0 0 0 0 0 0"/><Delete/>` into
any .vZome file that does NOT have a vertex at the origin and does NOT already
have the auto-delete-origin edit. This removes the spurious origin ball that
vZome auto-creates on document load.
"""
import re, os, sys

ROOT = os.path.join(os.path.dirname(__file__), '..', 'output')

origin_re = re.compile(r'<connector>\s*<point[^>]*>0 0 0 0 0 0|ShowPoint[^/]*point="0 0 0 0 0 0"')
delete_re = re.compile(r'SelectManifestation\s+point="0 0 0 0 0 0"\s*/>\s*<Delete')
edit_re   = re.compile(r'<EditHistory editNumber="(\d+)"')

modified = []
skipped_has_vert = []
skipped_already_deletes = []

for dp, _, fs in os.walk(ROOT):
    for f in fs:
        if not f.endswith('.vZome'):
            continue
        path = os.path.join(dp, f)
        with open(path, 'r', encoding='utf-8') as fh:
            content = fh.read()
        if origin_re.search(content):
            skipped_has_vert.append(path)
            continue
        if delete_re.search(content):
            skipped_already_deletes.append(path)
            continue
        insert = '    <SelectManifestation point="0 0 0 0 0 0"/>\n    <Delete/>\n  '
        new = content.replace('  </EditHistory>', insert + '</EditHistory>', 1)
        m = edit_re.search(new)
        if m:
            n = int(m.group(1))
            new = new[:m.start(1)] + str(n + 2) + new[m.end(1):]
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(new)
        modified.append(path)

print(f"Patched {len(modified)} files (added auto-delete-origin):")
for p in modified:
    print(f"  {os.path.relpath(p, ROOT)}")
print()
print(f"Skipped (origin already a vertex): {len(skipped_has_vert)}")
print(f"Skipped (already has auto-delete): {len(skipped_already_deletes)}")
