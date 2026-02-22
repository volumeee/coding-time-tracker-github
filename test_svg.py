#!/usr/bin/env python3
"""Test script for SVG generator — generates all layouts, themes, and responsive HTML."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "api"))

from services.svg_generator import generate_code_block, generate_svg

# Sample data
DATA = {
    "username": "volumeee",
    "total_hours": 181.4,
    "repo_count": 15,
    "period_days": 1454,
    "langs": {
        "TypeScript": 57.62,
        "JavaScript": 41.77,
        "C++": 34.33,
        "Python": 30.93,
        "HTML": 8.18,
        "CSS": 4.08,
        "Java": 3.58,
        "PHP": 0.57,
    },
    "frameworks": {
        "Express.js": 29.02,
        "React": 26.1,
        "Tailwind CSS": 18.57,
        "React Native": 17.03,
        "Vite": 9.05,
        "Jest": 3.4,
    },
}

OUT = "/tmp"
THEMES = ["dark", "light", "radical", "tokyonight"]

print("=" * 60)
print("  CodeStats SVG Generator — Test Suite")
print("=" * 60)

# 1. Generate SVG for each theme × layout
cards = {}
for theme in THEMES:
    for layout in ["landscape", "portrait"]:
        name = f"card_{theme}_{layout}"
        svg = generate_svg(DATA, theme, 8, True, layout)
        path = os.path.join(OUT, f"{name}.svg")
        with open(path, "w") as f:
            f.write(svg)
        cards[name] = svg
        print(f"  ✅ {name}.svg  ({len(svg)} bytes)")

# 2. Code block
print()
code = generate_code_block(DATA, 10, True)
code_path = os.path.join(OUT, "codestats_block.txt")
with open(code_path, "w") as f:
    f.write(code)
print(f"  ✅ codestats_block.txt  ({len(code)} bytes)")
print()
print("─" * 60)
print("  Code Block Preview:")
print("─" * 60)
print(code)
print("─" * 60)

# 3. Responsive HTML test page
sections = []
# Desktop/Tablet/Mobile for dark landscape
dl = cards["card_dark_landscape"]
dp = cards["card_dark_portrait"]
sections.append(('🖥️ Desktop (900px)', 'max-width:900px', dl))
sections.append(('📱 Tablet (600px)', 'max-width:600px', dl))
sections.append(('📲 Mobile (360px)', 'max-width:360px', dl))
sections.append(('📱 Portrait Mobile (360px)', 'max-width:360px', dp))

# All themes landscape
for th in THEMES:
    svg = cards[f"card_{th}_landscape"]
    sections.append((f'🎨 Theme: {th.title()}', 'max-width:900px', svg))

body = ""
for title, style, svg in sections:
    body += f"""
    <h2>{title}</h2>
    <div style="{style}">
      <div class="box">{svg}</div>
    </div>"""

html = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CodeStats SVG Test</title>
<style>
  body {{ margin:0; padding:30px; background:#0d1117; font-family:'Segoe UI',sans-serif; color:#c9d1d9 }}
  .wrap {{ max-width:960px; margin:0 auto }}
  h2 {{ color:#58a6ff; margin:30px 0 10px; font-weight:600; font-size:18px }}
  .box {{ margin:8px 0 30px; border:1px solid #30363d; border-radius:14px; padding:12px; background:#161b22 }}
</style>
</head><body>
<div class="wrap">
  <h1 style="color:#58a6ff;text-align:center;font-size:24px">📊 CodeStats SVG Test Suite</h1>
  {body}
</div>
</body></html>"""

html_path = os.path.join(OUT, "responsive_test.html")
with open(html_path, "w") as f:
    f.write(html)
print(f"\n  ✅ responsive_test.html  ({len(html)} bytes)")
print(f"\n  🌐 Open: file://{html_path}")
print()
print("=" * 60)
print(f"  All tests passed! {len(cards)} SVG cards generated.")
print("=" * 60)
