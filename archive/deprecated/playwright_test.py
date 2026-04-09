#!/usr/bin/env python3
"""Playwright Test Script"""
from playwright.sync_api import sync_playwright
import sys

def test_playwright():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto("https://empirehazeclaw.com")
        title = page.title()
        
        print(f"✅ Playwright works!")
        print(f"   Page title: {title}")
        
        browser.close()

if __name__ == "__main__":
    test_playwright()
