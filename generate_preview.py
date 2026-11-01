import os
import asyncio
from playwright.async_api import async_playwright

async def capture_tv_preview():
    html_file = os.path.abspath("ios_launcher_preview.html")
    output_png = os.path.abspath("preview_ios_tv_launcher.png")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1,
        )
        page = await context.new_page()
        await page.goto(f"file://{html_file}")
        await page.wait_for_timeout(1000)
        await page.screenshot(path=output_png, full_page=True)
        await browser.close()
        print(f"Captured screenshot to: {output_png}")

if __name__ == "__main__":
    asyncio.run(capture_tv_preview())
