#!/usr/bin/env python3
"""Rebuilds index.toml and pack.toml hashes. Run after any change, then commit + push."""
import hashlib, os, json, re
ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP = {"pack.toml", "index.toml", "README.md", "build_index.py", ".packwizignore", ".gitattributes"}
PRESERVE = {"options.txt", "config/iris.properties", "config/sodium-options.json", "config/DistantHorizons.toml"}
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def q(s): return json.dumps(s, ensure_ascii=False)
entries = []
for dp, dns, fns in os.walk(ROOT):
    dns[:] = [d for d in dns if not d.startswith(".git")]
    for fn in fns:
        rel = os.path.relpath(os.path.join(dp, fn), ROOT).replace(os.sep, "/")
        if rel in SKIP: continue
        e = f'[[files]]\nfile = {q(rel)}\nhash = "{sha(os.path.join(ROOT, rel))}"\n'
        if rel.endswith(".pw.toml"): e += "metafile = true\n"
        if rel in PRESERVE or (rel.startswith("shaderpacks/") and rel.endswith(".txt")): e += "preserve = true\n"
        entries.append((rel, e))
entries.sort()
open(os.path.join(ROOT, "index.toml"), "w", encoding="utf-8", newline="\n").write(
    'hash-format = "sha256"\n\n' + "\n".join(e for _, e in entries))
pack_path = os.path.join(ROOT, "pack.toml")
pack = open(pack_path, encoding="utf-8").read()
pack = re.sub(r'(\[index\][^\[]*?hash = ")[0-9a-f]*(")', lambda m: m.group(1) + sha(os.path.join(ROOT, "index.toml")) + m.group(2), pack, flags=re.S)
open(pack_path, "w", encoding="utf-8", newline="\n").write(pack)
print(f"Indexed {len(entries)} files.")
