#!/usr/bin/env python3
"""Aktualisiert recipes-index.json fuer GitHub Pages aus allen Rezept-JSON-Dateien."""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# Unterstuetzt sowohl JSON-Dateien im Unterordner ./recipes als auch direkt im Root
recipes_dir = ROOT / "recipes" if (ROOT / "recipes").is_dir() else ROOT
files = sorted(
    p.name for p in recipes_dir.glob("*.json")
    if p.name != "recipes-index.json"
)
manifest = {
    "updated_at": date.today().isoformat(),
    "count": len(files),
    "recipes": files,
}
(ROOT / "recipes-index.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(f"recipes-index.json aktualisiert ({len(files)} Rezepte).")
