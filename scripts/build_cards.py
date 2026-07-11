"""Generate the profile's stats, language, and project pin cards as static SVGs.

Self-hosted replacement for github-readme-stats, which serves 503s whenever
its public Vercel instance is paused. Runs locally or in the daily Action.
"""
import base64
import json
import os
import urllib.request

USER = "Luwalekeah"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RUST, RUST_HI, RUST_LO = "#B45A2B", "#E09B6A", "#6E3416"
LAKE, LAKE_HI = "#4D7EA8", "#7FA8C9"
INK, BORDER, TXT, MUTED = "#0F1B24", "#2C4557", "#A9BFCF", "#5E7183"

PIN_REPOS = ["luwah-site", "watchsync", "Market-Research",
             "Digital-Resume", "Qwixx-ScoreSheet", "Quiddler-ScoreSheet"]

# Shown when the repo has no description on GitHub yet
FALLBACK_DESC = {
    "watchsync": "WatchSync, a synced watch-together app",
    "Market-Research": "Python market research tooling",
    "Digital-Resume": "Interactive resume built with Streamlit",
    "Qwixx-ScoreSheet": "Digital score sheet for the Qwixx dice game",
    "Quiddler-ScoreSheet": "Digital score sheet for the Quiddler card game",
    "luwah-site": "Luwah Technologies site, Next.js and Sanity",
}

LANG_COLORS = {
    "Python": "#3572A5", "TypeScript": "#3178C6", "JavaScript": "#F1E05A",
    "Jupyter Notebook": "#DA5B0B", "HTML": "#E34C26", "CSS": "#563D7C",
    "Shell": "#89E051", "SCSS": "#C6538C", "Dockerfile": "#384D54",
    "PLpgSQL": "#336790", "SAS": "#B34936",
}

with open(f"{ROOT}/assets/fonts/montserrat-subset.woff2", "rb") as fh:
    FONT64 = base64.b64encode(fh.read()).decode()

FONT_CSS = ("@font-face { font-family:'Montserrat'; "
            f"src:url(data:font/woff2;base64,{FONT64}) format('woff2'); "
            "font-weight:100 900; }")

TOKEN = os.environ.get("GITHUB_TOKEN", "")


def gh(url, accept="application/vnd.github+json"):
    req = urllib.request.Request(url, headers={
        "Accept": accept, "User-Agent": USER,
        **({"Authorization": f"token {TOKEN}"} if TOKEN else {}),
    })
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def wrap(text, width=52, lines=2):
    words, out, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            out.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    out.append(cur)
    if len(out) > lines:
        out = out[:lines]
        out[-1] = out[-1][:width - 1] + "…"
    return out


def card(w, h, body, label):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">
  <style>{FONT_CSS}
    .t {{ font: 700 18px 'Montserrat', sans-serif; }}
    .d {{ font: 500 13px 'Montserrat', sans-serif; }}
    .s {{ font: 700 14px 'Montserrat', sans-serif; }}
    .l {{ font: 500 12px 'Montserrat', sans-serif; }}</style>
  <defs><clipPath id="r"><rect width="{w}" height="{h}" rx="12"/></clipPath></defs>
  <g clip-path="url(#r)">
    <rect width="{w}" height="{h}" fill="{INK}"/>
    <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="11" fill="none" stroke="{BORDER}" stroke-width="2"/>
    {body}
  </g>
</svg>'''


def star_icon(x, y, fill):
    return (f'<path transform="translate({x},{y}) scale(0.875)" fill="{fill}" d="M8 .25l2.03 4.11 '
            '4.54.66-3.28 3.2.77 4.52L8 10.6l-4.06 2.14.77-4.52L1.43 5.02l4.54-.66z"/>')


def fork_icon(x, y, fill):
    return (f'<path transform="translate({x},{y}) scale(0.875)" fill="{fill}" d="M5 3.25a.75.75 0 11-1.5 0 '
            '.75.75 0 011.5 0zm0 2.122a2.25 2.25 0 10-1.5 0v.878A2.25 2.25 0 005.75 8.5h1.5v2.128a2.251 '
            '2.251 0 101.5 0V8.5h1.5a2.25 2.25 0 002.25-2.25v-.878a2.25 2.25 0 10-1.5 0v.878a.75.75 0 '
            '01-.75.75h-4.5A.75.75 0 015 6.25v-.878zm3.75 7.378a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm3-8.75'
            'a.75.75 0 100-1.5.75.75 0 000 1.5z"/>')


def build_pin(repo):
    name = esc(repo["name"])
    desc = repo.get("description") or FALLBACK_DESC.get(repo["name"], "")
    lang = repo.get("language") or ""
    stars, forks = repo["stargazers_count"], repo["forks_count"]
    lang_dot = LANG_COLORS.get(lang, LAKE)
    lines = wrap(esc(desc))
    desc_svg = "".join(f'<text class="d" x="24" y="{62 + i * 20}" fill="{TXT}">{ln}</text>'
                       for i, ln in enumerate(lines))
    meta = []
    x = 24
    if lang:
        meta.append(f'<circle cx="{x + 5}" cy="118" r="5" fill="{lang_dot}"/>'
                    f'<text class="l" x="{x + 16}" y="122" fill="{LAKE_HI}">{esc(lang)}</text>')
        x += 16 + int(len(lang) * 7.2) + 24
    meta.append(star_icon(x, 111, MUTED) +
                f'<text class="l" x="{x + 19}" y="122" fill="{MUTED}">{stars}</text>')
    x += 46
    meta.append(fork_icon(x, 111, MUTED) +
                f'<text class="l" x="{x + 19}" y="122" fill="{MUTED}">{forks}</text>')
    body = f'''
    <rect x="0" y="0" width="5" height="140" fill="{RUST}"/>
    <text class="t" x="24" y="36" fill="{RUST_HI}">{name}</text>
    {desc_svg}
    {"".join(meta)}'''
    return card(495, 140, body, f"{name}: {desc}")


def build_stats(user, repos, commits, prs, issues):
    stars = sum(r["stargazers_count"] for r in repos)
    rows = [("Total Stars Earned", stars), ("Commits This Year", commits),
            ("Total PRs", prs), ("Total Issues", issues),
            ("Public Repos", user["public_repos"]), ("Followers", user["followers"])]
    body_rows = "".join(
        f'<rect x="24" y="{58 + i * 26}" width="9" height="9" transform="rotate(45 28.5 {62.5 + i * 26})" fill="{LAKE}"/>'
        f'<text class="d" x="44" y="{69 + i * 26}" fill="{TXT}">{label}</text>'
        f'<text class="s" x="300" y="{69 + i * 26}" fill="{RUST_HI}">{val}</text>'
        for i, (label, val) in enumerate(rows))
    initials = f'''
    <circle cx="415" cy="120" r="52" fill="none" stroke="{BORDER}" stroke-width="6"/>
    <circle cx="415" cy="120" r="52" fill="none" stroke="{RUST}" stroke-width="6"
      stroke-dasharray="245 327" stroke-linecap="round" transform="rotate(-90 415 120)"/>
    <text class="t" x="415" y="128" text-anchor="middle" fill="{LAKE_HI}">DC</text>'''
    body = f'''
    <text class="t" x="24" y="34" fill="{RUST_HI}">Daniel&#8217;s GitHub Stats</text>
    {body_rows}{initials}'''
    return card(495, 230, body, "Daniel's GitHub stats")


def build_langs(lang_bytes):
    total = sum(lang_bytes.values()) or 1
    top = sorted(lang_bytes.items(), key=lambda kv: -kv[1])[:8]
    body = [f'<text class="t" x="24" y="34" fill="{RUST_HI}">Most Used Languages</text>']
    x = 24.0
    for lang, n in top:
        seg = max((n / total) * 447, 4)
        body.append(f'<rect x="{x:.1f}" y="52" width="{seg:.1f}" height="10" '
                    f'fill="{LANG_COLORS.get(lang, LAKE)}"/>')
        x += seg
    for i, (lang, n) in enumerate(top):
        cx, cy = 24 + (i % 2) * 236, 92 + (i // 2) * 32
        pct = 100 * n / total
        body.append(f'<circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{LANG_COLORS.get(lang, LAKE)}"/>'
                    f'<text class="l" x="{cx + 18}" y="{cy}" fill="{TXT}">{esc(lang)}</text>'
                    f'<text class="l" x="{cx + 158}" y="{cy}" fill="{MUTED}">{pct:.1f}%</text>')
    return card(495, 230, "".join(body), "Most used languages")


def main():
    user = gh(f"https://api.github.com/users/{USER}")
    repos = [r for r in gh(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
             if not r["fork"]]
    year = user["updated_at"][:4]
    commits = gh(f"https://api.github.com/search/commits?q=author:{USER}+author-date:>={year}-01-01&per_page=1",
                 accept="application/vnd.github.cloak-preview+json")["total_count"]
    prs = gh(f"https://api.github.com/search/issues?q=author:{USER}+type:pr&per_page=1")["total_count"]
    issues = gh(f"https://api.github.com/search/issues?q=author:{USER}+type:issue&per_page=1")["total_count"]

    lang_bytes = {}
    for r in repos:
        for lang, n in gh(r["languages_url"]).items():
            lang_bytes[lang] = lang_bytes.get(lang, 0) + n

    with open(f"{ROOT}/assets/stats.svg", "w") as fh:
        fh.write(build_stats(user, repos, commits, prs, issues))
    with open(f"{ROOT}/assets/langs.svg", "w") as fh:
        fh.write(build_langs(lang_bytes))

    by_name = {r["name"]: r for r in repos}
    for name in PIN_REPOS:
        if name in by_name:
            with open(f"{ROOT}/assets/pin-{name}.svg", "w") as fh:
                fh.write(build_pin(by_name[name]))
        else:
            print(f"warning: repo {name} not found, card skipped")
    print("cards written")


if __name__ == "__main__":
    main()
