#!/usr/bin/env python3
"""Pull the Blockrophage course repository into the website build.

The course lives in its own repository (github.com/TizzuLab/blockrophage); the
website only showcases it. This script:

1. makes sure `_blockrophage/` holds a checkout of that repository (CI checks it
   out beforehand; locally it is cloned on first run and pulled afterwards),
2. copies the lecture decks and the schedule drawings into `assets/teaching/`,
3. writes the Markdown fragments that `teaching.qmd` includes:
   `_blockrophage/_site_readme.md`   the course script (README) with relative
                                     links rewritten to GitHub and headings
                                     demoted one level,
   `_blockrophage/_site_slides.md`   one embedded viewer per lecture deck,
   `_blockrophage/_site_schedule.md` the four week drawings,
   `_blockrophage/_site_meta.md`     the sync line (commit, date).

`_blockrophage/` and `assets/teaching/` are git-ignored; Quarto ignores folders
that start with an underscore, so nothing in the checkout is rendered on its own.
The publish workflow runs this nightly, so the website follows the course repo
with at most a day of delay.
"""
from __future__ import annotations

import datetime as dt
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "_blockrophage"
REPO = "https://github.com/TizzuLab/blockrophage"
ASSETS = ROOT / "assets" / "teaching"


def run(*cmd, cwd=None):
    return subprocess.check_output(cmd, cwd=cwd, text=True).strip()


def ensure_checkout():
    if (SRC / ".git").exists() or (SRC / ".git").is_file():
        return
    if SRC.exists() and any(SRC.iterdir()):
        return  # CI checkout without .git metadata is fine too
    run("git", "clone", "--depth", "1", REPO + ".git", str(SRC))


def commit_info():
    try:
        sha = run("git", "rev-parse", "--short", "HEAD", cwd=SRC)
        date = run("git", "log", "-1", "--format=%cs", cwd=SRC)
        return sha, date
    except Exception:
        return "unknown", dt.date.today().isoformat()


LINK = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)(\s+\"[^\"]*\")?\)")


def rewrite_links(md: str) -> str:
    def sub(m):
        bang, text, target, title = m.group(1), m.group(2), m.group(3), m.group(4) or ""
        if re.match(r"^(https?:|mailto:|#)", target):
            return m.group(0)
        clean = target.lstrip("./")
        kind = "tree" if clean.endswith("/") or "." not in clean.rsplit("/", 1)[-1] else "blob"
        url = f"{REPO}/{kind}/main/{clean}"
        return f"{bang}[{text}]({url}{title})"
    return LINK.sub(sub, md)


def demote(md: str) -> str:
    return re.sub(r"^(#{1,5})(\s)", lambda m: "#" * (len(m.group(1)) + 1) + m.group(2), md, flags=re.M)


def strip_head(md: str) -> str:
    """Drop the H1, the bold subtitle line and the under-construction quote; the page has its own."""
    lines = md.split("\n")
    out, i = [], 0
    # H1
    if lines and lines[0].startswith("# "):
        i = 1
    # blank lines + subtitle paragraph (ends at first blank line)
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and lines[i].startswith("**"):
        while i < len(lines) and lines[i].strip():
            i += 1
    # blockquote
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and lines[i].startswith(">"):
        while i < len(lines) and lines[i].startswith(">"):
            i += 1
    out = lines[i:]
    return "\n".join(out).strip() + "\n"


def slides_table():
    """[(filename, title)] from slides/README.md, falling back to file names."""
    readme = SRC / "slides" / "README.md"
    items = []
    if readme.exists():
        for line in readme.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^\|\s*\[([^\]]+\.pdf)\]\([^)]+\)\s*\|\s*(.+?)\s*\|$", line)
            if m:
                items.append((m.group(1), m.group(2)))
    found = sorted(p.name for p in (SRC / "slides").glob("*.pdf"))
    known = {f for f, _ in items}
    items += [(f, f) for f in found if f not in known]
    return [(f, t) for f, t in items if f in found]


def main():
    ensure_checkout()
    sha, date = commit_info()

    # assets
    if ASSETS.exists():
        shutil.rmtree(ASSETS)
    (ASSETS / "slides").mkdir(parents=True)
    (ASSETS / "schedule").mkdir(parents=True)
    for p in (SRC / "slides").glob("*.pdf"):
        shutil.copyfile(p, ASSETS / "slides" / p.name)
    for p in (SRC / "schedule").glob("week-*.svg"):
        shutil.copyfile(p, ASSETS / "schedule" / p.name)

    # fragments
    readme = (SRC / "README.md").read_text(encoding="utf-8")
    body = demote(rewrite_links(strip_head(readme)))
    (SRC / "_site_readme.md").write_text(body, encoding="utf-8")

    slides = []
    for f, title in slides_table():
        url = f"/assets/teaching/slides/{f}"
        slides.append(
            f"**{title}**\n\n"
            f"```{{=html}}\n"
            f"<iframe src=\"{url}#view=FitH\" title=\"{title}\" loading=\"lazy\" "
            f"style=\"border:1px solid #1f1f1f;width:100%;aspect-ratio:16/10;background:#111\"></iframe>\n"
            f"```\n\n"
            f"[Open the PDF]({url}){{target=\"_blank\"}}\n"
        )
    (SRC / "_site_slides.md").write_text("\n".join(slides) if slides else "_No decks yet._\n", encoding="utf-8")

    weeks = sorted((ASSETS / "schedule").glob("week-*.svg"), key=lambda p: int(p.stem.split("-")[1]))
    sched = []
    for p in weeks:
        n = p.stem.split("-")[1]
        url = f"/assets/teaching/schedule/{p.name}"
        sched.append(f"[![Week {n}]({url}){{.schedule-week}}]({url}){{target=\"_blank\"}}\n")
    sched.append(f"\nClick a week to open it at full size. Source and text version: "
                 f"[schedule folder on GitHub]({REPO}/tree/main/schedule).\n")
    (SRC / "_site_schedule.md").write_text("\n".join(sched), encoding="utf-8")

    (SRC / "_site_meta.md").write_text(
        f"*Synced nightly from [TizzuLab/blockrophage]({REPO}), commit `{sha}` of {date}; "
        f"this page rebuilt {dt.date.today().isoformat()}.*\n", encoding="utf-8")
    print(f"synced blockrophage {sha} ({date}): {len(slides)} decks, {len(weeks)} week drawings")


if __name__ == "__main__":
    main()
