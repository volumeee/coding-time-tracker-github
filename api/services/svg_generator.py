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

    top = dict(list(langs.items())[:langs_count])
    tl = sum(top.values()) or 1
    fw = dict(list(frameworks.items())[:langs_count]) if show_frameworks else {}

    lines = [f"Coding Time Tracker🙆\u200d♂️ — {username}", "",
             f"Total Time: {_fmt(total_hours)}  ({period} days)",
             f"Repos scanned: {repo_count}", "", "💻 Languages:"]

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

def _lang_stripe(langs: dict, total: float, vw: int, y: int, pad: int) -> str:
    """Combined GitHub-style language proportion bar."""
    bar_w = vw - pad * 2
    x = pad
    parts = []
    items = list(langs.items())
    for i, (lang, hrs) in enumerate(items):
        w = max(2, hrs / total * bar_w)
        col = LANGUAGE_COLORS.get(lang, "#8b8b8b")
        rx_l = "6" if i == 0 else "0"
        rx_r = "6" if i == len(items) - 1 else "0"
        parts.append(
            f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="10" fill="{col}"'
            f' rx="{rx_l}" ry="{rx_r}"/>'
        )
        x += w
    return "\n  ".join(parts)


def _stat_pill(x: int, y: int, icon: str, label: str, value: str, theme: dict) -> str:
    """Rounded stat indicator pill."""
    w = max(len(f"{label}: {value}") * 6.5 + 30, 80)
    return (
        f'<rect x="{x}" y="{y}" width="{w:.0f}" height="26" rx="13" '
        f'fill="{theme["bar_bg"]}" opacity="0.8"/>'
        f'<text x="{x + 14}" y="{y + 17}" class="pill">'
        f'{icon} {_e(label)}: <tspan class="pv">{_e(value)}</tspan></text>'
    )


def _build_portrait(data: dict, theme: dict, opts: dict) -> str:
    username = data.get("username", "user")
    total_hours = data.get("total_hours", 0)
    langs = data.get("langs", {})
    frameworks = data.get("frameworks", {})
    period = data.get("period_days", 365)
    repo_count = data.get("repo_count", 0)

    vw = opts.get("width", 480)
    lc = opts.get("langs_count", 8)
    s_lang = opts.get("show_langs", True)
    s_fw = opts.get("show_fw", True)
    s_title = opts.get("show_title", True)
    s_footer = opts.get("show_footer", True)

    top = dict(list(langs.items())[:lc])
    tl = sum(top.values()) or 1
    fws = list(frameworks.keys()) if s_fw else []

    pad = 22
    y = pad
    parts = []

    # ── Header with accent ──
    if s_title:
        parts.append(f'<text x="{pad}" y="{y + 18}" class="t">📊 {_e(username)}\'s Coding Stats</text>')
        y += 32
        # Stats pills row
        parts.append(_stat_pill(pad, y, "⏱", "Total", _fms(total_hours), theme))
        parts.append(_stat_pill(pad + 140, y, "📁", "Repos", str(repo_count), theme))
        parts.append(_stat_pill(pad + 250, y, "📅", "Period", _pl(period), theme))
        y += 38
        # Gradient accent line
        parts.append(
            f'<defs><linearGradient id="g1" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0%" stop-color="{theme["title"]}"/>'
            f'<stop offset="100%" stop-color="{theme["title"]}" stop-opacity="0.1"/>'
            f'</linearGradient></defs>'
            f'<rect x="{pad}" y="{y}" width="{vw - pad * 2}" height="2" rx="1" fill="url(#g1)"/>'
        )
        y += 12

    # ── Combined language bar ──
    if s_lang and top:
        parts.append(_lang_stripe(top, tl, vw, y, pad))
        y += 20

        # Language list with colored dots
        parts.append(f'<text x="{pad}" y="{y + 14}" class="sec">💻 Languages</text>')
        y += 26
        bar_w = vw - pad * 2 - 180
        if bar_w < 50:
            bar_w = 50
        for lang, hrs in top.items():
            pct = hrs / tl * 100
            bw = max(2, pct / 100 * bar_w)
            col = LANGUAGE_COLORS.get(lang, "#8b8b8b")
            bx = pad + 95
            parts.append(
                f'<g transform="translate(0,{y})">'
                f'<circle cx="{pad + 5}" cy="-3" r="4" fill="{col}"/>'
                f'<text x="{pad + 14}" y="0" class="l">{_e(lang)}</text>'
                f'<rect x="{bx}" y="-8" width="{bar_w}" height="8" rx="4" fill="{theme["bar_bg"]}"/>'
                f'<rect x="{bx}" y="-8" width="{bw:.1f}" height="8" rx="4" fill="{col}">'
                f'<animate attributeName="width" from="0" to="{bw:.1f}" dur="0.6s" fill="freeze" begin="0.2s"/></rect>'
                f'<text x="{bx + bar_w + 8}" y="0" class="p">{pct:.1f}%</text>'
                f'<text x="{vw - pad}" y="0" class="tm" text-anchor="end">{_fms(hrs)}</text>'
                f'</g>'
            )
            y += 26

    # ── Frameworks ──
    if s_fw and fws:
        y += 10
        parts.append(f'<text x="{pad}" y="{y + 14}" class="sec">⚡ Frameworks &amp; Tools</text>')
        y += 28
        fx = pad
        for fw in fws:
            bc = FRAMEWORK_COLORS.get(fw, "#555555")
            tc = _tc(bc)
            tw = len(fw) * 7.2 + 20
            if fx + tw > vw - pad:
                fx = pad
                y += 28
            parts.append(
                f'<rect x="{fx}" y="{y - 15}" width="{tw:.0f}" height="24" rx="12" '
                f'fill="{bc}" opacity="0.85"/>'
                f'<text x="{fx + tw / 2:.0f}" y="{y + 1}" text-anchor="middle" '
                f'class="b" fill="{tc}">{_e(fw)}</text>'
            )
            fx += tw + 8
        y += 18

    # ── Footer ──
    if s_footer:
        y += 14
        parts.append(
            f'<text x="{vw // 2}" y="{y}" text-anchor="middle" class="f">'
            f'CodeStats · github.com/volumeee</text>'
        )
        y += 8

    return _svg(vw, y + 10, theme, "\n  ".join(parts))


def _build_landscape(data: dict, theme: dict, opts: dict) -> str:
    username = data.get("username", "user")
    total_hours = data.get("total_hours", 0)
    langs = data.get("langs", {})
    frameworks = data.get("frameworks", {})
    period = data.get("period_days", 365)
    repo_count = data.get("repo_count", 0)

    vw = opts.get("width", 720)
    lc = opts.get("langs_count", 8)
    s_lang = opts.get("show_langs", True)
    s_fw = opts.get("show_fw", True)
    s_title = opts.get("show_title", True)
    s_footer = opts.get("show_footer", True)

    top = dict(list(langs.items())[:lc])
    tl = sum(top.values()) or 1
    fws = list(frameworks.keys()) if s_fw else []

    pad = 22
    row_h = 26
    header_h = 0

    # Column math: name(80) + time(85) + bar(130) + pct(45) + gaps
    name_w, time_w, bar_w, pct_w = 80, 85, 130, 45
    left_block = name_w + time_w + bar_w + pct_w + 30
    divider_x = pad + left_block
    if divider_x > vw * 0.62:
        divider_x = int(vw * 0.62)
        bar_w = divider_x - pad - name_w - time_w - pct_w - 30
        if bar_w < 60:
            bar_w = 60

    parts = []

    # ── Header ──
    if s_title:
        parts.append(f'<text x="{pad}" y="24" class="t">📊 {_e(username)}\'s Coding Stats</text>')
        # Stats pills
        y_pill = 36
        parts.append(_stat_pill(pad, y_pill, "⏱", "Total", _fms(total_hours), theme))
        parts.append(_stat_pill(pad + 135, y_pill, "📁", "Repos", str(repo_count), theme))
        parts.append(_stat_pill(pad + 240, y_pill, "📅", "Period", _pl(period), theme))
        # Gradient accent
        parts.append(
            f'<defs><linearGradient id="g1" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0%" stop-color="{theme["title"]}"/>'
            f'<stop offset="100%" stop-color="{theme["title"]}" stop-opacity="0.1"/>'
            f'</linearGradient></defs>'
            f'<rect x="{pad}" y="68" width="{vw - pad * 2}" height="2" rx="1" fill="url(#g1)"/>'
        )
        header_h = 78
    else:
        header_h = 10

    # ── Combined language stripe ──
    if s_lang and top:
        parts.append(_lang_stripe(top, tl, vw, header_h + 4, pad))
        header_h += 18

    # ── Languages (left) ──
    y = header_h + 16
    if s_lang and top:
        parts.append(f'<text x="{pad}" y="{y}" class="sec">💻 Languages</text>')
        y += 18
        for lang, hrs in top.items():
            pct = hrs / tl * 100
            bw = max(2, pct / 100 * bar_w)
            col = LANGUAGE_COLORS.get(lang, "#8b8b8b")
            xn = pad
            xt = pad + name_w
            xb = pad + name_w + time_w
            xp = pad + name_w + time_w + bar_w + 8
            parts.append(
                f'<g transform="translate(0,{y})">'
                f'<circle cx="{xn + 4}" cy="-3" r="3.5" fill="{col}"/>'
                f'<text x="{xn + 13}" y="0" class="l">{_e(lang)}</text>'
                f'<text x="{xt}" y="0" class="tm">{_fms(hrs)}</text>'
                f'<rect x="{xb}" y="-7" width="{bar_w}" height="7" rx="3.5" fill="{theme["bar_bg"]}"/>'
                f'<rect x="{xb}" y="-7" width="{bw:.1f}" height="7" rx="3.5" fill="{col}">'
                f'<animate attributeName="width" from="0" to="{bw:.1f}" dur="0.6s" fill="freeze" begin="0.2s"/></rect>'
                f'<text x="{xp}" y="0" class="p">{pct:.1f}%</text>'
                f'</g>'
            )
            y += row_h
    max_y = y

    # ── Divider ──
    parts.append(
        f'<line x1="{divider_x}" y1="{header_h + 8}" x2="{divider_x}" y2="{max_y - 6}" '
        f'stroke="{theme["border"]}" stroke-width="0.5" opacity="0.2"/>'
    )

    # ── Frameworks (right) ──
    rx = divider_x + pad
    if s_fw and fws:
        fy = header_h + 16
        parts.append(f'<text x="{rx}" y="{fy}" class="sec">⚡ Frameworks</text>')
        fy += 22
        fx = rx
        for fw in fws:
            bc = FRAMEWORK_COLORS.get(fw, "#555555")
            tc = _tc(bc)
            tw = len(fw) * 7.2 + 18
            if fx + tw > vw - pad:
                fx = rx
                fy += 28
            parts.append(
                f'<rect x="{fx}" y="{fy - 14}" width="{tw:.0f}" height="23" rx="11.5" '
                f'fill="{bc}" opacity="0.85"/>'
                f'<text x="{fx + tw / 2:.0f}" y="{fy + 2}" text-anchor="middle" '
                f'class="b" fill="{tc}">{_e(fw)}</text>'
            )
            fx += tw + 7
        max_y = max(max_y, fy + 20)

    # ── Footer ──
    fy = max_y + 8
    if s_footer:
        fy += 6
        parts.append(
            f'<text x="{vw // 2}" y="{fy}" text-anchor="middle" class="f">'
            f'CodeStats · github.com/volumeee</text>'
        )
        fy += 10

    return _svg(vw, fy + 6, theme, "\n  ".join(parts))


# ─── SVG WRAPPER ─────────────────────────────────────────────────
def _svg(vw: int, vh: int, theme: dict, body: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 {vw} {vh}"
     preserveAspectRatio="xMidYMin meet">
  <defs><style>
    .t {{ font: 700 16px 'Segoe UI', Ubuntu, sans-serif; fill: {theme['title']}; }}
    .s {{ font: 400 11px 'Segoe UI', Ubuntu, sans-serif; fill: {theme['muted']}; }}
    .sec {{ font: 600 11px 'Segoe UI', Ubuntu, sans-serif; fill: {theme['title']}; }}
    .l {{ font: 500 11px 'Segoe UI', Ubuntu, sans-serif; fill: {theme['text']}; }}
    .tm {{ font: 400 10px 'Segoe UI', monospace; fill: {theme['muted']}; }}
    .p {{ font: 500 10px 'Segoe UI', sans-serif; fill: {theme['muted']}; }}
    .b {{ font: 600 9.5px 'Segoe UI', sans-serif; }}
    .f {{ font: 400 9px 'Segoe UI', sans-serif; fill: {theme['muted']}; opacity: 0.4; }}
    .pill {{ font: 500 9.5px 'Segoe UI', sans-serif; fill: {theme['muted']}; }}
    .pv {{ fill: {theme['text']}; font-weight: 700; }}
  </style></defs>
  <rect width="{vw}" height="{vh}" rx="12" fill="{theme['bg']}" stroke="{theme['border']}" stroke-width="1"/>
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
  <text x="247" y="35" text-anchor="middle" style="font:600 14px 'Segoe UI',sans-serif;fill:{theme['title']}">⚠️ CodeStats Error</text>
  <text x="247" y="58" text-anchor="middle" style="font:400 11px 'Segoe UI',sans-serif;fill:{theme['muted']}">{_e(message)}</text>
</svg>"""
