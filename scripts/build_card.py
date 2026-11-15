import json
import os
import urllib.request
from datetime import datetime, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
USER = "TyrealQ"

PROFILE = [
    ("Name", "Yizhou (Tyreal) Qian 钱亦舟"),
    ("Alias", "Dr. Q"),
    ("Approach", "Computational social science"),
    ("Building", "Open datasets and AI research tools"),
]

CONTACT = [
    ("Email", "tyqian@iu.edu"),
    ("Hugging Face", "huggingface.co/tyrealqian"),
]

THEMES = {
    "dark": {
        "bg": "#0d1117", "border": "#30363d", "ascii": "#c9d1d9",
        "text": "#c9d1d9", "key": "#ff7b72", "muted": "#484f58", "title": "#f0f6fc",
    },
    "light": {
        "bg": "#ffffff", "border": "#d0d7de", "ascii": "#24292f",
        "text": "#24292f", "key": "#990000", "muted": "#afb8c1", "title": "#1f2328",
    },
}

FONT = "SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace"
SIZE = 14
CHAR_W = SIZE * 0.6
LINE_H = 20
ART_SIZE = 4.4
ART_W = ART_SIZE * 0.6
ART_LINE = 5.1
PAD = 24
KEY_W = 16
PANEL_COLS = 54


def graphql(query, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-card"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if "errors" in body:
        raise RuntimeError(body["errors"])
    return body["data"]


def fetch_stats(token):
    base = graphql(
        f"""{{ user(login: "{USER}") {{
            createdAt
            contributionsCollection {{ contributionYears }}
            repositories(ownerAffiliations: OWNER, privacy: PUBLIC, first: 100) {{
                totalCount nodes {{ stargazerCount }} }}
        }} }}""",
        token,
    )["user"]
    years = base["contributionsCollection"]["contributionYears"]
    parts = " ".join(
        f'y{y}: contributionsCollection(from: "{y}-01-01T00:00:00Z", to: "{y}-12-31T23:59:59Z")'
        " { totalCommitContributions restrictedContributionsCount }"
        for y in years
    )
    per_year = graphql(f'{{ user(login: "{USER}") {{ {parts} }} }}', token)["user"]
    commits = sum(v["totalCommitContributions"] + v["restrictedContributionsCount"] for v in per_year.values())
    return {
        "repos": base["repositories"]["totalCount"],
        "stars": sum(n["stargazerCount"] for n in base["repositories"]["nodes"]),
        "commits": commits,
        "created": base["createdAt"],
    }


def tenure(created):
    start = datetime.fromisoformat(created.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    months = (now.year - start.year) * 12 + now.month - start.month - (now.day < start.day)
    y, m = divmod(months, 12)
    return f"{y} years, {m} months" if m else f"{y} years"


def stat_lines(s):
    return [
        ("Repos", f"{s['repos']:,}"),
        ("Stars", f"{s['stars']:,}"),
        ("Commits", f"{s['commits']:,}"),
        ("On GitHub", tenure(s["created"])),
    ]


def kv(key, value, c):
    dots = " " + "." * (KEY_W - len(key) - 1) + " "
    return (
        f'<tspan fill="{c["key"]}">{escape(key)}</tspan>'
        f'<tspan fill="{c["muted"]}">{dots}</tspan>'
        f'<tspan fill="{c["text"]}">{escape(value)}</tspan>'
    )


def rule(label, c):
    head = f"─ {label} " if label else ""
    fill = "─" * (PANEL_COLS - len(head))
    title = f'<tspan fill="{c["title"]}">{escape(head)}</tspan>' if head else ""
    return f'{title}<tspan fill="{c["muted"]}">{fill}</tspan>'


def panel(stats, c):
    rows = [f'<tspan fill="{c["title"]}" font-weight="bold">tyrealq</tspan>'
            f'<tspan fill="{c["text"]}">@</tspan>'
            f'<tspan fill="{c["title"]}" font-weight="bold">github</tspan>',
            rule("", c)]
    rows += [kv(k, v, c) for k, v in PROFILE]
    rows += ["", rule("Contact", c)]
    rows += [kv(k, v, c) for k, v in CONTACT]
    rows += ["", rule("GitHub Stats", c)]
    rows += [kv(k, v, c) for k, v in stat_lines(stats)]
    return rows


def render(theme, stats):
    c = THEMES[theme]
    art = (ROOT / "art" / f"portrait-{theme}.txt").read_text().splitlines()
    art_cols = max(len(line) for line in art)
    right = panel(stats, c)
    art_w = art_cols * ART_W
    gap = 3 * CHAR_W
    panel_x = PAD + art_w + gap
    width = round(panel_x + PANEL_COLS * CHAR_W + PAD)
    inner = max(len(art) * ART_LINE, len(right) * LINE_H)
    height = round(PAD * 2 + inner)
    art_top = PAD + (inner - len(art) * ART_LINE) / 2
    panel_top = PAD + (inner - len(right) * LINE_H) / 2

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="{FONT}" font-size="{SIZE}px">',
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" '
        f'fill="{c["bg"]}" stroke="{c["border"]}"/>',
        f'<text fill="{c["ascii"]}" font-size="{ART_SIZE}px" xml:space="preserve">',
    ]
    for i, line in enumerate(art):
        if line.strip():
            y = art_top + (i + 0.8) * ART_LINE
            out.append(
                f'<tspan x="{PAD}" y="{y:.1f}" textLength="{len(line) * ART_W:.1f}" '
                f'lengthAdjust="spacingAndGlyphs">{escape(line)}</tspan>'
            )
    out.append("</text>")
    out.append('<text xml:space="preserve">')
    for i, row in enumerate(right):
        if row:
            y = panel_top + (i + 0.75) * LINE_H
            out.append(f'<tspan x="{panel_x:.1f}" y="{y:.1f}">{row}</tspan>')
    out.append("</text></svg>")
    return "\n".join(out) + "\n"


def main():
    stats = fetch_stats(os.environ["GITHUB_TOKEN"])
    for theme in THEMES:
        (ROOT / f"card-{theme}.svg").write_text(render(theme, stats))


if __name__ == "__main__":
    main()
