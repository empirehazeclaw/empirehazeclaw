#!/usr/bin/env python3
"""Playwright Browser Automation"""
from playwright.sync_api import sync_playwright
import sys

def screenshot(url, filename="screenshot.png"):
    """Take screenshot of URL"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        page.screenshot(path=filename)
        browser.close()
    return f"✅ Saved: {filename}"

def scrape(url):
    """Scrape page content"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        title = page.title()
        content = page.content()[:500]
        browser.close()
    return f"Title: {title}\n\n{content[:200]}..."

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    print(f"=== 🌐 PLAYWRIGHT TEST ===")
    print(scrape(url))
