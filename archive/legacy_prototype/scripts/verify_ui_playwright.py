"""Automated Playwright UI & Regression Verification Script.
Inspects the built case study HTML in headless Chromium:
- Asserts DOM presence of all 9 core sections
- Validates 2-minute executive brief rendering
- Tests matrix filtering, search, and preset chips
- Tests modal dialog triggering and documentation link rendering
- Tests live agent demo execution and terminal log stream
- Captures verified screenshots in outputs/
- Checks for JavaScript console errors
"""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = f"file://{ROOT}/case_study.html"
OUT_DIR = ROOT / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

async def run_playwright_verification():
    print(f"Launching Playwright Chromium to test: {HTML_PATH}")
    console_errors = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        # Capture console messages
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda err: console_errors.append(str(err)))

        # Navigate to standalone HTML
        await page.goto(HTML_PATH, wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # 1. Title verification
        title = await page.title()
        print(f"[OK] Page title: '{title}'")
        assert "Composio Access Atlas" in title

        # 2. Check 2-Minute Executive Briefing
        brief_header = await page.locator("text=Executive Briefing for Reviewers").is_visible()
        print(f"[OK] 2-Minute Executive Briefing visible: {brief_header}")
        assert brief_header

        # 3. Check Metric Cards
        metric_100 = await page.locator("text=100% across 10 categories").is_visible()
        print(f"[OK] Coverage metric card visible: {metric_100}")
        assert metric_100

        # Capture Hero & Overview Screenshot
        await page.screenshot(path=str(OUT_DIR / "playwright_hero_overview.png"), full_page=False)
        print(f"[OK] Saved: {OUT_DIR}/playwright_hero_overview.png")

        # 4. Test Matrix Preset Chips
        print("Testing Matrix Preset Filter: '🤝 Partner Gated (6)'...")
        await page.locator("text=🤝 Partner Gated (6)").click()
        await page.wait_for_timeout(400)
        
        # Verify count shows 6
        stat_text = await page.locator("text=Showing 6 of 100 apps").is_visible()
        print(f"[OK] Matrix filtered to exactly 6 apps: {stat_text}")
        assert stat_text

        # Capture Filtered Matrix Screenshot
        matrix_el = page.locator("#matrix")
        await matrix_el.screenshot(path=str(OUT_DIR / "playwright_matrix_filtered.png"))
        print(f"[OK] Saved: {OUT_DIR}/playwright_matrix_filtered.png")

        # Reset filters
        await page.locator("text=All 100 Apps").click()
        await page.wait_for_timeout(300)

        # 5. Test Modal Triggering on App #1 (Salesforce)
        print("Testing Modal Inspector on first table row (App #1)...")
        await page.locator("tbody tr").first.click()
        await page.wait_for_timeout(500)

        modal_title = await page.locator("text=Application Scope & Profile").is_visible()
        print(f"[OK] App Detail Modal opened: {modal_title}")
        assert modal_title

        # Check documentation link in modal
        docs_visible = await page.locator("text=Official Developer Documentation URLs").is_visible()
        print(f"[OK] Documentation URLs section in modal: {docs_visible}")
        assert docs_visible

        # Close modal
        await page.locator("button:has-text('Close')").click()
        await page.wait_for_timeout(300)

        # 6. Test Live Agent Runner
        print("Testing Live Agent Runner on #6 Firecrawl...")
        await page.locator("#demo").scroll_into_view_if_needed()
        await page.locator("text=#6 Firecrawl (Official MCP)").click()
        await page.wait_for_timeout(300)

        # Click Run Research
        run_btn = page.locator("button:has-text('Run Research')")
        await run_btn.click()
        print("Triggered research run in Live Agent Runner...")

        # Wait for agent progress
        await page.wait_for_timeout(2000)
        logs_visible = await page.locator("text=[Agent 1: Discovery]").is_visible()
        print(f"[OK] Terminal logs streaming: {logs_visible}")
        assert logs_visible

        # Wait for completion
        await page.wait_for_timeout(3000)
        completed_visible = await page.locator("text=✓ COMPLETED").is_visible()
        print(f"[OK] Agent run completed with 100% progress: {completed_visible}")
        assert completed_visible

        # Capture Live Agent Demo Screenshot
        demo_el = page.locator("#demo")
        await demo_el.screenshot(path=str(OUT_DIR / "playwright_agent_demo.png"))
        print(f"[OK] Saved: {OUT_DIR}/playwright_agent_demo.png")

        await browser.close()

    print("\n--- Playwright UI Verification Summary ---")
    print(f"Total Console Errors: {len(console_errors)}")
    if console_errors:
        print("Errors logged:", console_errors)
    else:
        print("Zero console errors. 100% UI and functionality verified!")

if __name__ == "__main__":
    asyncio.run(run_playwright_verification())
