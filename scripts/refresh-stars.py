#!/usr/bin/env python3
"""Refresh star counts in index.html from the GitHub REST API.

Updates: per-repo star numbers + bar widths, the four hero stats,
and the "verified <date>" notes in the header kicker and footer.

Usage:
  python scripts/refresh-stars.py --dry-run   # print the diff, change nothing
  python scripts/refresh-stars.py             # rewrite index.html in place

Needs GITHUB_TOKEN (or gh CLI auth) — ~118 API calls, one per repo.
"""
import re
import sys
import math
import json
import datetime
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "index.html"
MIN_BAR = 157  # smallest star count used to calibrate bar widths


def get_token():
    import os
    t = os.environ.get("GITHUB_TOKEN")
    if t:
        return t
    try:
        import subprocess
        return subprocess.run(["gh", "auth", "token"], capture_output=True,
                              text=True).stdout.strip() or None
    except Exception:
        return None


def api(slug, tok):
    req = urllib.request.Request(f"https://api.github.com/repos/{slug}", headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "field-guide-refresh",
        **({"Authorization": f"Bearer {tok}"} if tok else {}),
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fmt_k(stars):
    """Match the page's number style: 821, 1k, 6.2k, 112k, 433.3k."""
    if stars < 1000:
        return str(stars)
    s = f"{stars / 1000.0:.1f}"
    return f"{round(stars / 1000)}k" if s.endswith(".0") else f"{s}k"


def bar_w(stars):
    return max(17, min(44, round(17 + 8 * math.log10(stars / MIN_BAR))))


def main():
    dry = "--dry-run" in sys.argv
    html = PAGE.read_text(encoding="utf-8")
    tok = get_token()

    row_re = re.compile(
        r'<a href="https://github\.com/([^"]+)" target="_blank" rel="noopener">'
        r'<span class="owner">[^<]*</span>([^<]+)</a></td>\s*'
        r'<td class="st"><span class="num">([^<]+)</span>\s*'
        r'<span class="bar"><i style="width:(\d+)px"></i></span>'
    )
    rows = list(row_re.finditer(html))
    if not rows:
        sys.exit("No rows matched — markup changed?")

    stats, errors, out, last = {}, [], [], 0
    for m in rows:
        slug = m.group(1)
        stars = None
        try:
            stars = api(slug, tok).get("stargazers_count")
        except Exception as e:
            errors.append((slug, str(e)))
        if stars is None:
            out.append(html[last:m.end(4)])
            last = m.end(4)
            continue
        stats[slug] = stars
        seg = html[m.start(3):m.end(4)]
        seg = seg.replace(m.group(3), fmt_k(stars), 1)
        seg = seg.replace(f'width:{m.group(4)}px', f'width:{bar_w(stars)}px', 1)
        out.append(html[last:m.start(3)], )
        out.append(seg)
        last = m.end(4)
    out.append(html[last:])
    new_html = "".join(out)

    total = sum(stats.values())
    total_m = (f"{total / 1e6:.2f}".rstrip("0").rstrip(".")) + "M"
    big_k = fmt_k(max(stats.values()))
    today = datetime.date.today().strftime("%d %B %Y").lstrip("0")

    for pat, repl in [
        (r'(<div class="stat"><b>)[\d.]+[kM]?(</b><span>Combined stars</span>)', f'\\g<1>{total_m}\\g<2>'),
        (r'(<div class="stat"><b>)[\d.]+[kM]?(</b><span>Largest single repo</span>)', f'\\g<1>{big_k}\\g<2>'),
        (r'Field guide · verified [^<]+</div>', f'Field guide · verified {today}</div>'),
        (r'Star counts: GitHub REST API, [^.]+\. ', f'Star counts: GitHub REST API, {today}. '),
    ]:
        new_html, n = re.subn(pat, repl, new_html, count=1)
        if n == 0 and not dry:
            print(f"! could not update: {pat}")

    if errors:
        print(f"! {len(errors)} repo(s) failed (kept old numbers):")
        for slug, e in errors:
            print(f"   {slug}: {e}")

    if dry:
        import difflib
        for line in difflib.unified_diff(html.splitlines(), new_html.splitlines(), lineterm="", n=0):
            print(line)
        print("\nDRY RUN — nothing written.")
    else:
        PAGE.write_text(new_html, encoding="utf-8")
        print(f"Updated {len(stats)}/{len(rows)} repos · total {total_m} · largest {big_k} · verified {today}")


if __name__ == "__main__":
    main()
