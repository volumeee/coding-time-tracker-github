"""Premium SVG & Code block generator — informative, clean, responsive."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import FRAMEWORK_COLORS, LANGUAGE_COLORS, THEMES


# ─── FORMATTERS ──────────────────────────────────────────────────
def _fmt(h: float) -> str:
    hrs, mins = int(h), int((h - int(h)) * 60)
    return f"{hrs} hrs {mins} mins"


def _fms(h: float) -> str:
    hrs, mins = int(h), int((h - int(h)) * 60)
    return f"{hrs}h {mins}m" if hrs > 0 else f"{mins}m"


def _lum(c: str) -> float:
    c = c.lstrip("#")
    if len(c) < 6:
        return 0.5
    r, g, b = int(c[:2], 16) / 255, int(c[2:4], 16) / 255, int(c[4:6], 16) / 255
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _tc(bg: str) -> str:
    return "#ffffff" if _lum(bg) < 0.5 else "#1a1a2e"


def _e(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _bg(p: float, w: int = 20) -> str:
    f = int(p / 100 * w)
    return "█" * f + "░" * (w - f)


def _pl(d: int) -> str:
    if d >= 365:
        n = d // 365
        return f"{n} year{'s' if n > 1 else ''}"
    if d >= 30:
        n = d // 30
        return f"{n} month{'s' if n > 1 else ''}"
    return f"{d} days"


# ═══════════════════════════════════════════════════════════════════
#  CODE BLOCK
# ═══════════════════════════════════════════════════════════════════
def generate_code_block(data: dict, langs_count: int = 10,
                        show_frameworks: bool = True) -> str:
    username = data.get("username", "user")
    total_hours = data.get("total_hours", 0)
    langs = data.get("langs", {})
    frameworks = data.get("frameworks", {})
    period = data.get("period_days", 365)
    repo_count = data.get("repo_count", 0)
    prs = data.get("prs", 0)
    issues = data.get("issues", 0)
    busiest = data.get("busiest_time", "Day Worker")

    top = dict(list(langs.items())[:langs_count])
    tl = sum(top.values()) or 1
    fw = dict(list(frameworks.items())[:langs_count]) if show_frameworks else {}

    lines = [f"Coding Time Tracker🙆‍♂️ — {username}", "",
             f"Total Time: {_fmt(total_hours)}  ({period} days)",
             f"Repos scanned: {repo_count} | 🔀 PRs: {prs} | 🐞 Issues: {issues} | 🕒 Mode: {busiest}", "", "💻 Languages:"]

    if top:
        mn = max(len(n) for n in top)
        mt = max(len(_fmt(h)) for h in top.values())
        for lang, hrs in top.items():
            p = (hrs / tl) * 100
            lines.append(f"{lang.ljust(mn)}   {_fmt(hrs).ljust(mt)}  {_bg(p)}  {p:5.2f} %")

    if show_frameworks and fw:
        lines += ["", "⚡ Frameworks & Tools:"]
        mn = max(len(n) for n in fw)
        mt = max(len(_fmt(h)) for h in fw.values())
        for f_name, hrs in fw.items():
            p = (hrs / tl) * 100
            lines.append(f"{f_name.ljust(mn)}   {_fmt(hrs).ljust(mt)}  {_bg(p)}  {p:5.2f} %")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
#  SVG - PREMIUM DESIGN
# ═══════════════════════════════════════════════════════════════════

_clip_counter = 0

def _lang_stripe(langs: dict, total: float, vw: int, y: int, pad: int) -> str:
    """Combined GitHub-style language proportion bar with proper unified rounding."""
    global _clip_counter
    _clip_counter += 1
    bar_w = vw - pad * 2
    bar_h = 10
    radius = 5
    x = pad
    parts = []
    items = list(langs.items())

    # Use clipPath for clean unified rounded bar (unique ID per invocation)
    clip_id = f"sc{_clip_counter}"
    parts.append(
        f'<defs><clipPath id="{clip_id}">'
        f'<rect x="{pad}" y="{y}" width="{bar_w}" height="{bar_h}" rx="{radius}"/>'
        f'</clipPath></defs>'
    )

    for i, (lang, hrs) in enumerate(items):
        w = max(2, hrs / total * bar_w)
        col = LANGUAGE_COLORS.get(lang, "#8b8b8b")
        parts.append(
            f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{bar_h}" '
            f'fill="{col}" clip-path="url(#{clip_id})"/>'
        )
        x += w
    return "\n  ".join(parts)


def _stat_pill(x: int, y: int, icon: str, label: str, value: str, theme: dict) -> str:
    """Rounded stat indicator pill with consistent sizing."""
    text = f"{label}: {value}"
    w = max(len(text) * 7 + 28, 90)
    return (
        f'<g class="stat-pill">'
        f'<rect x="{x}" y="{y}" width="{w:.0f}" height="26" rx="13" '
        f'fill="{theme["bar_bg"]}" opacity="0.9" class="pill-bg"/>'
        f'<text x="{x + 14}" y="{y + 17}" class="pill">'
        f'{icon} {_e(label)}: <tspan class="pv">{_e(value)}</tspan></text>'
        f'</g>'
    )


def _build_pills_row(data: dict, theme: dict, pad: int, y: int, vw: int) -> tuple:
    """Build stat pills that adapt to available width. Returns (svg_parts, new_y)."""
    total_hours = data.get("total_hours", 0)
    repo_count = data.get("repo_count", 0)
    period = data.get("period_days", 365)
    prs = data.get("prs", 0)
    issues = data.get("issues", 0)
    busiest = data.get("busiest_time", "Day Worker")

    if "Owl" in busiest:
        m_icon = "🦉"
    elif "Bird" in busiest:
        m_icon = "☀️"
    elif "Evening" in busiest:
        m_icon = "🌆"
    else:
        m_icon = "☕"

    pills = [
        ("⏱", "Time", _fms(total_hours)),
        ("📁", "Repos", str(repo_count)),
        ("📅", "Period", _pl(period)),
        ("🔀", "PRs", str(prs)),
        ("🐞", "Issues", str(issues)),
        (m_icon, "Mode", busiest),
    ]

    # Calculate pill widths
    pill_data = []
    for icon, label, value in pills:
        text = f"{label}: {value}"
        w = max(len(text) * 7 + 28, 90)
        pill_data.append((icon, label, value, w))

    available_w = vw - pad * 2
    parts = []
    cx = pad
    cy = y
    gap = 8

    for icon, label, value, w in pill_data:
        if cx + w > pad + available_w and cx > pad:
            # Wrap to next row
            cx = pad
            cy += 32
        parts.append(_stat_pill(int(cx), cy, icon, label, value, theme))
        cx += w + gap

    return parts, cy + 32


def _gradient_accent(theme: dict, pad: int, y: int, vw: int) -> str:
    """Gradient accent separator line."""
    return (
        f'<defs><linearGradient id="g1" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0%" stop-color="{theme["title"]}"/>'
        f'<stop offset="100%" stop-color="{theme["title"]}" stop-opacity="0.1"/>'
        f'</linearGradient></defs>'
        f'<rect x="{pad}" y="{y}" width="{vw - pad * 2}" height="2" rx="1" fill="url(#g1)"/>'
    )


def _build_portrait(data: dict, theme: dict, opts: dict) -> str:
    username = data.get("username", "user")
    langs = data.get("langs", {})
    frameworks = data.get("frameworks", {})

    vw = opts.get("width", 480)
    lc = opts.get("langs_count", 8)
    s_lang = opts.get("show_langs", True)
    s_fw = opts.get("show_fw", True)
    s_title = opts.get("show_title", True)
    s_footer = opts.get("show_footer", True)

    top = dict(list(langs.items())[:lc])
    tl = sum(top.values()) or 1
    fws = list(frameworks.keys()) if s_fw else []

    pad = 24
    y = pad
    parts = []

    # ── Header ──
    if s_title:
        parts.append(f'<text x="{pad}" y="{y + 18}" class="t">📊 {_e(username)}\'s Coding Stats</text>')
        y += 34

        pill_parts, y = _build_pills_row(data, theme, pad, y, vw)
        parts.extend(pill_parts)
        y += 6

        parts.append(_gradient_accent(theme, pad, y, vw))
        y += 14

    # ── Combined language bar ──
    if s_lang and top:
        parts.append(_lang_stripe(top, tl, vw, y, pad))
        y += 20

        # Language section header
        parts.append(f'<text x="{pad}" y="{y + 14}" class="sec">💻 Languages</text>')
        y += 28

        # Calculate column positions for portrait — compact layout
        name_col = pad + 14  # After color dot
        bar_x = pad + 90    # Bar start
        right_edge = vw - pad
        # Reserve space for "31.8% 57h 37m" = ~100px
        info_width = 100
        bar_w = right_edge - bar_x - info_width - 8
        if bar_w < 60:
            bar_w = 60
        pct_x = bar_x + bar_w + 8

        bar_h = 12
        row_h = 30

        for lang, hrs in top.items():
            pct = hrs / tl * 100
            bw = max(3, pct / 100 * bar_w)
            col = LANGUAGE_COLORS.get(lang, "#8b8b8b")
            parts.append(
                f'<g transform="translate(0,{y})">'
                f'<circle cx="{pad + 5}" cy="-3" r="4.5" fill="{col}"/>'
                f'<text x="{name_col}" y="0" class="l">{_e(lang)}</text>'
                f'<rect x="{bar_x}" y="-8" width="{bar_w}" height="{bar_h}" rx="{bar_h // 2}" fill="{theme["bar_bg"]}"/>'
                f'<rect x="{bar_x}" y="-8" width="{bw:.1f}" height="{bar_h}" rx="{bar_h // 2}" fill="{col}">'
                f'<animate attributeName="width" from="0" to="{bw:.1f}" dur="0.8s" fill="freeze" begin="0.15s"/></rect>'
                f'<text x="{pct_x}" y="-5" class="p">{pct:.1f}%</text>'
                f'<text x="{pct_x}" y="8" class="tm">{_fms(hrs)}</text>'
                f'</g>'
            )
            y += row_h

    # ── Frameworks ──
    if s_fw and fws:
        y += 14
        parts.append(f'<text x="{pad}" y="{y + 14}" class="sec">⚡ Frameworks &amp; Tools</text>')
        y += 30
        fx = pad
        for fw in fws:
            bc = FRAMEWORK_COLORS.get(fw, "#555555")
            tc = _tc(bc)
            tw = len(fw) * 7.5 + 22
            if fx + tw > vw - pad:
                fx = pad
                y += 30
            parts.append(
                f'<rect x="{fx}" y="{y - 16}" width="{tw:.0f}" height="26" rx="13" '
                f'fill="{bc}" opacity="0.9" class="fw-badge"/>'
                f'<text x="{fx + tw / 2:.0f}" y="{y + 1}" text-anchor="middle" '
                f'class="b" fill="{tc}">{_e(fw)}</text>'
            )
            fx += tw + 8
        y += 18

    # ── Footer ──
    if s_footer:
        y += 16
        parts.append(
            f'<text x="{vw // 2}" y="{y}" text-anchor="middle" class="f">'
            f'CodeStats · github.com/volumeee</text>'
        )
        y += 10

    return _svg(vw, y + 12, theme, "\n  ".join(parts))


def _build_landscape(data: dict, theme: dict, opts: dict) -> str:
    username = data.get("username", "user")
    langs = data.get("langs", {})
    frameworks = data.get("frameworks", {})

    vw = opts.get("width", 720)
    lc = opts.get("langs_count", 8)
    s_lang = opts.get("show_langs", True)
    s_fw = opts.get("show_fw", True)
    s_title = opts.get("show_title", True)
    s_footer = opts.get("show_footer", True)

    top = dict(list(langs.items())[:lc])
    tl = sum(top.values()) or 1
    fws = list(frameworks.keys()) if s_fw else []

    pad = 24
    row_h = 28
    header_h = 0

    # ── Layout math ──
    # Left side: languages | Right side: frameworks
    # Divider at ~62% of width
    divider_x = int(vw * 0.62)

    # Column positions for language rows (left side)
    name_col = pad + 14  # After color dot
    time_col = pad + 95  # Time column
    bar_x = pad + 155    # Bar start
    bar_w = divider_x - bar_x - 60  # Bar width (leave room for %)
    if bar_w < 60:
        bar_w = 60
    pct_x = bar_x + bar_w + 10  # Percentage text

    bar_h = 12

    parts = []

    # ── Header ──
    if s_title:
        parts.append(f'<text x="{pad}" y="24" class="t">📊 {_e(username)}\'s Coding Stats</text>')

        pill_parts, pill_end_y = _build_pills_row(data, theme, pad, 36, vw)
        parts.extend(pill_parts)

        accent_y = pill_end_y + 4
        parts.append(_gradient_accent(theme, pad, accent_y, vw))
        header_h = accent_y + 10
    else:
        header_h = 10

    # ── Combined language stripe ──
    if s_lang and top:
        parts.append(_lang_stripe(top, tl, vw, header_h + 4, pad))
        header_h += 20

    # ── Languages (left) ──
    y = header_h + 16
    if s_lang and top:
        parts.append(f'<text x="{pad}" y="{y}" class="sec">💻 Languages</text>')
        y += 20
        for lang, hrs in top.items():
            pct = hrs / tl * 100
            bw = max(3, pct / 100 * bar_w)
            col = LANGUAGE_COLORS.get(lang, "#8b8b8b")
            parts.append(
                f'<g transform="translate(0,{y})">'
                f'<circle cx="{pad + 5}" cy="-3" r="4" fill="{col}"/>'
                f'<text x="{name_col}" y="0" class="l">{_e(lang)}</text>'
                f'<text x="{time_col}" y="0" class="tm">{_fms(hrs)}</text>'
                f'<rect x="{bar_x}" y="-8" width="{bar_w}" height="{bar_h}" rx="{bar_h // 2}" fill="{theme["bar_bg"]}"/>'
                f'<rect x="{bar_x}" y="-8" width="{bw:.1f}" height="{bar_h}" rx="{bar_h // 2}" fill="{col}">'
                f'<animate attributeName="width" from="0" to="{bw:.1f}" dur="0.8s" fill="freeze" begin="0.15s"/></rect>'
                f'<text x="{pct_x}" y="0" class="p">{pct:.1f}%</text>'
                f'</g>'
            )
            y += row_h
    max_y = y

    # ── Divider ──
    parts.append(
        f'<line x1="{divider_x}" y1="{header_h + 6}" x2="{divider_x}" y2="{max_y - 8}" '
        f'stroke="{theme["border"]}" stroke-width="1" opacity="0.3"/>'
    )

    # ── Frameworks (right) ──
    rx = divider_x + 18
    if s_fw and fws:
        fy = header_h + 16
        parts.append(f'<text x="{rx}" y="{fy}" class="sec">⚡ Frameworks &amp; Tools</text>')
        fy += 24
        fx = rx
        max_fw_x = vw - pad
        for fw in fws:
            bc = FRAMEWORK_COLORS.get(fw, "#555555")
            tc = _tc(bc)
            tw = len(fw) * 7.5 + 20
            if fx + tw > max_fw_x:
                fx = rx
                fy += 30
            parts.append(
                f'<rect x="{fx}" y="{fy - 15}" width="{tw:.0f}" height="26" rx="13" '
                f'fill="{bc}" opacity="0.9" class="fw-badge"/>'
                f'<text x="{fx + tw / 2:.0f}" y="{fy + 2}" text-anchor="middle" '
                f'class="b" fill="{tc}">{_e(fw)}</text>'
            )
            fx += tw + 8
        max_y = max(max_y, fy + 22)

    # ── Footer ──
    fy = max_y + 10
    if s_footer:
        fy += 4
        parts.append(
            f'<text x="{vw // 2}" y="{fy}" text-anchor="middle" class="f">'
            f'CodeStats · github.com/volumeee</text>'
        )
        fy += 12

    return _svg(vw, fy + 6, theme, "\n  ".join(parts))


# ─── SVG WRAPPER ─────────────────────────────────────────────────
def _svg(vw: int, vh: int, theme: dict, body: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 {vw} {vh}"
     preserveAspectRatio="xMidYMin meet">
  <defs><style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;display=swap');
    
    @keyframes pulseGlow {{
      0% {{ filter: drop-shadow(0 0 2px {theme['title']}); opacity: 0.9; }}
      50% {{ filter: drop-shadow(0 0 8px {theme['title']}); opacity: 1; }}
      100% {{ filter: drop-shadow(0 0 2px {theme['title']}); opacity: 0.9; }}
    }}
    
    @keyframes slideUp {{
      from {{ transform: translateY(12px); opacity: 0; }}
      to {{ transform: translateY(0); opacity: 1; }}
    }}
    
    .card-bg {{
      fill: {theme['bg']};
      stroke: {theme['border']};
      stroke-width: 1.5;
    }}
    
    .t {{ font: 700 16px 'Inter', 'Segoe UI', Ubuntu, sans-serif; fill: {theme['title']}; animation: pulseGlow 3s infinite; }}
    .s {{ font: 400 11px 'Inter', 'Segoe UI', Ubuntu, sans-serif; fill: {theme['muted']}; }}
    .sec {{ font: 600 11.5px 'Inter', 'Segoe UI', Ubuntu, sans-serif; fill: {theme['title']}; letter-spacing: 0.3px; }}
    .l {{ font: 500 11px 'Inter', 'Segoe UI', Ubuntu, sans-serif; fill: {theme['text']}; }}
    .tm {{ font: 400 10.5px 'Inter', 'Segoe UI', monospace; fill: {theme['muted']}; }}
    .p {{ font: 600 10px 'Inter', 'Segoe UI', sans-serif; fill: {theme['muted']}; }}
    .b {{ font: 600 10px 'Inter', 'Segoe UI', sans-serif; }}
    .f {{ font: 400 9.5px 'Inter', 'Segoe UI', sans-serif; fill: {theme['muted']}; opacity: 0.5; }}
    .pill {{ font: 500 9.5px 'Inter', 'Segoe UI', sans-serif; fill: {theme['muted']}; cursor: pointer; }}
    .pv {{ fill: {theme['text']}; font-weight: 700; }}
    
    .stat-pill {{ transition: all 0.3s ease; transform-origin: center; }}
    .stat-pill:hover {{ transform: translateY(-2px); filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3)); }}
    .pill-bg {{ transition: fill 0.3s ease; }}
    .stat-pill:hover .pill-bg {{ filter: brightness(1.2); }}
    
    g {{ animation: slideUp 0.8s cubic-bezier(0.25, 1, 0.5, 1) both; }}
    g:nth-child(1) {{ animation-delay: 0.05s; }}
    g:nth-child(2) {{ animation-delay: 0.1s; }}
    g:nth-child(3) {{ animation-delay: 0.15s; }}
    g:nth-child(4) {{ animation-delay: 0.2s; }}
    g:nth-child(5) {{ animation-delay: 0.25s; }}
    g:nth-child(6) {{ animation-delay: 0.3s; }}
    g:nth-child(7) {{ animation-delay: 0.35s; }}
    g:nth-child(8) {{ animation-delay: 0.4s; }}
    g:nth-child(n+9) {{ animation-delay: 0.45s; }}
    
    rect.fw-badge {{
       transition: all 0.3s ease;
    }}
    rect.fw-badge:hover {{
       filter: brightness(1.2);
       transform: scale(1.05);
    }}
  </style></defs>
  <rect width="{vw}" height="{vh}" rx="12" class="card-bg"/>
  {body}
</svg>"""


# ─── PUBLIC API ──────────────────────────────────────────────────
def generate_svg(data: dict, theme_name: str = "dark",
                 langs_count: int = 8, show_frameworks: bool = True,
                 layout: str = "landscape", width: int = 0,
                 show_title: bool = True, show_footer: bool = True,
                 show_languages: bool = True) -> str:
    theme = THEMES.get(theme_name, THEMES["dark"])
    opts = {"langs_count": langs_count, "show_fw": show_frameworks,
            "show_title": show_title, "show_footer": show_footer,
            "show_langs": show_languages}
    if layout == "portrait":
        opts["width"] = width if width > 0 else 480
        return _build_portrait(data, theme, opts)
    else:
        opts["width"] = width if width > 0 else 720
        return _build_landscape(data, theme, opts)


def generate_error_svg(message: str, theme_name: str = "dark") -> str:
    theme = THEMES.get(theme_name, THEMES["dark"])
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 495 80"
     preserveAspectRatio="xMidYMin meet">
  <rect width="495" height="80" rx="12" fill="{theme['bg']}" stroke="{theme['border']}" stroke-width="1"/>
  <text x="247" y="35" text-anchor="middle" style="font:600 14px 'Inter','Segoe UI',sans-serif;fill:{theme['title']}">⚠️ CodeStats Error</text>
  <text x="247" y="58" text-anchor="middle" style="font:400 11px 'Inter','Segoe UI',sans-serif;fill:{theme['muted']}">{_e(message)}</text>
</svg>"""
