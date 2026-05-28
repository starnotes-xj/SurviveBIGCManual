"""Read a Zhihu article after manual login and export it as Markdown.

Usage:
    python tools/read_zhihu_article.py "https://zhuanlan.zhihu.com/p/..."

The script opens a visible Chromium window with a persistent local profile.
Log in manually if Zhihu asks, open the article, then press Enter in the
terminal. The script reads only content visible to your logged-in browser.
"""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


ARTICLE_SELECTORS = [
    "article",
    ".Post-RichTextContainer",
    ".RichContent-inner",
    ".RichText",
    ".Post-content",
]


def clean_filename(value: str) -> str:
    value = re.sub(r"[\\/:*?\"<>|]+", "-", value).strip()
    value = re.sub(r"\s+", " ", value)
    return value[:80] or "zhihu-article"


def normalize_text(text: str) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
    compact: list[str] = []
    blank = False
    for line in lines:
        if not line.strip():
            if not blank:
                compact.append("")
            blank = True
            continue
        compact.append(line)
        blank = False
    return "\n".join(compact).strip()


def extract_text(page) -> tuple[str, str]:
    title = page.title().strip()
    try:
        h1 = page.locator("h1").first.inner_text(timeout=2000).strip()
        if h1:
            title = h1
    except PlaywrightTimeoutError:
        pass

    for selector in ARTICLE_SELECTORS:
        locator = page.locator(selector).first
        try:
            text = locator.inner_text(timeout=3000)
        except PlaywrightTimeoutError:
            continue
        text = normalize_text(text)
        if len(text) >= 200:
            return title, text

    return title, normalize_text(page.locator("body").inner_text(timeout=5000))


def write_markdown(url: str, title: str, body: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{stamp}-{clean_filename(title)}.md"
    path = output_dir / filename
    content = "\n".join(
        [
            f"# {title or '知乎文章'}",
            "",
            f"原文链接：[{url}]({url})",
            "",
            "> 本文由脚本从你已登录并有权访问的浏览器页面中提取，请自行确认转载、引用和使用范围。",
            "",
            "---",
            "",
            body,
            "",
        ]
    )
    path.write_text(content, encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Read a Zhihu article after manual login.")
    parser.add_argument("url", help="Zhihu article URL")
    parser.add_argument(
        "--profile",
        default="tmp_zhihu_profile",
        help="Persistent browser profile directory, default: tmp_zhihu_profile",
    )
    parser.add_argument(
        "--output",
        default="tmp_zhihu_read",
        help="Output directory for exported Markdown, default: tmp_zhihu_read",
    )
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=60000,
        help="Navigation timeout in milliseconds, default: 60000",
    )
    args = parser.parse_args()

    profile_dir = Path(args.profile).resolve()
    output_dir = Path(args.output).resolve()

    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=False,
            viewport={"width": 1365, "height": 900},
            locale="zh-CN",
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(args.url, wait_until="domcontentloaded", timeout=args.timeout_ms)

        print("")
        print("A browser window is open.")
        print("1. Log in to Zhihu manually if needed.")
        print("2. Make sure the target article body is visible.")
        print("3. Return here and press Enter to extract the article.")
        input("")

        page.wait_for_load_state("domcontentloaded", timeout=args.timeout_ms)
        title, body = extract_text(page)
        path = write_markdown(page.url, title, body, output_dir)

        print(f"Title: {title}")
        print(f"Characters: {len(body)}")
        print(f"Saved: {path}")
        context.close()


if __name__ == "__main__":
    main()
