"""Core Shopee Flash Sale Bot automation implementation."""

import json
import logging
import os
import time
from typing import Optional
from playwright.sync_api import BrowserContext, Page, sync_playwright

from shopee_bot.config import BotConfig
from shopee_bot.scheduler import PreciseScheduler

logger = logging.getLogger("ShopeeBot")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class ShopeeFlashSaleBot:
    """Automates Shopee product purchase during flash sales using Playwright."""

    def __init__(self, config: BotConfig):
        self.config = config
        self._playwright = None
        self._browser_context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    def setup_browser(self, playwright_instance=None) -> Page:
        """Initializes the browser context with user data and persistent cookies."""
        if playwright_instance is None:
            self._playwright = sync_playwright().start()
            p = self._playwright
        else:
            p = playwright_instance

        # Use persistent context to retain login session, local storage, and cookies
        user_data_path = os.path.abspath(self.config.user_data_dir)
        os.makedirs(user_data_path, exist_ok=True)

        self._browser_context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_path,
            headless=self.config.headless,
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            args=["--disable-blink-features=AutomationControlled"],
        )

        # Load cookies if available
        if self.config.cookies_file and os.path.exists(self.config.cookies_file):
            try:
                with open(self.config.cookies_file, "r", encoding="utf-8") as f:
                    cookies = json.load(f)
                    self._browser_context.add_cookies(cookies)
                logger.info("Loaded cookies from %s", self.config.cookies_file)
            except Exception as e:
                logger.warning("Failed to load cookies: %s", e)

        if self._browser_context.pages:
            self._page = self._browser_context.pages[0]
        else:
            self._page = self._browser_context.new_page()

        return self._page

    def save_cookies(self) -> None:
        """Saves current browser cookies to file for future sessions."""
        if not self._browser_context or not self.config.cookies_file:
            return
        cookies = self._browser_context.cookies()
        with open(self.config.cookies_file, "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2)
        logger.info("Saved cookies to %s", self.config.cookies_file)

    def select_variations(self, page: Page) -> None:
        """Clicks variation buttons specified in config."""
        for variation in self.config.variations:
            logger.info("Attempting to select variation: %s", variation)
            # Find button containing variation text
            btn_selector = f"button:has-text('{variation}'), [aria-label='{variation}']"
            try:
                btn = page.locator(btn_selector).first
                if btn.is_visible(timeout=2000):
                    btn.click()
                    logger.info("Selected variation: %s", variation)
            except Exception as e:
                logger.warning("Variation %s could not be clicked: %s", variation, e)

    def set_quantity(self, page: Page) -> None:
        """Sets the quantity if greater than 1."""
        if self.config.quantity <= 1:
            return
        logger.info("Setting quantity to %s", self.config.quantity)
        try:
            qty_input = page.locator("input.shopee-input-quantity, input[type='number']").first
            if qty_input.is_visible(timeout=1000):
                qty_input.fill(str(self.config.quantity))
        except Exception as e:
            logger.warning("Failed to set quantity input: %s", e)

    def wait_and_click_buy_now(self, page: Page, max_retries: int = 50) -> bool:
        """
        Polls and clicks the 'Buy Now' / 'Beli Sekarang' button.
        Shopee button texts typically include 'beli sekarang', 'buy now', or 'beli dengan voucher'.
        """
        selectors = [
            "button:has-text('Beli Sekarang')",
            "button:has-text('Buy Now')",
            "button:has-text('beli sekarang')",
            "button.btn-solid-primary:has-text('Beli')",
            "button.btn-solid-primary:has-text('Buy')",
            "[aria-label='Beli Sekarang']",
            "[aria-label='Buy Now']",
            "button.btn-buy-now",
        ]

        logger.info("Waiting for Buy Now button to be clickable...")
        start_time = time.time()
        for attempt in range(max_retries):
            for sel in selectors:
                loc = page.locator(sel).first
                try:
                    if loc.is_visible() and loc.is_enabled():
                        loc.click()
                        logger.info("Clicked Buy Now using selector '%s' (attempt %d)", sel, attempt + 1)
                        return True
                except Exception:
                    pass

            time.sleep(self.config.click_interval_ms / 1000.0)

        elapsed = time.time() - start_time
        logger.error("Timed out waiting to click Buy Now after %.2fs", elapsed)
        return False

    def handle_checkout(self, page: Page) -> bool:
        """
        Navigates checkout screen, selects preferred payment method, and places order.
        """
        logger.info("Handling checkout flow...")

        # Wait for checkout page indicator
        try:
            page.wait_for_url("**/checkout**", timeout=self.config.max_checkout_wait_sec * 1000)
            logger.info("Arrived at checkout page: %s", page.url)
        except Exception:
            logger.warning("Did not navigate to URL containing 'checkout', continuing with current page.")

        # Payment method selection if configured
        if self.config.payment_method:
            logger.info("Looking for payment method: %s", self.config.payment_method)
            try:
                payment_btn = page.locator(f"text='{self.config.payment_method}'").first
                if payment_btn.is_visible(timeout=3000):
                    payment_btn.click()
                    logger.info("Selected payment method: %s", self.config.payment_method)
            except Exception as e:
                logger.warning("Could not select payment method: %s", e)

        # Place Order button
        place_order_selectors = [
            "button:has-text('Buat Pesanan')",
            "button:has-text('Place Order')",
            "button:has-text('Bayar')",
            "button.stardust-button--primary:has-text('Buat Pesanan')",
            "button.place-order-btn",
        ]

        if self.config.dry_run:
            logger.info("[DRY RUN] Final 'Place Order' / 'Buat Pesanan' button NOT clicked.")
            return True

        for sel in place_order_selectors:
            btn = page.locator(sel).first
            try:
                if btn.is_visible(timeout=5000) and btn.is_enabled():
                    btn.click()
                    logger.info("Clicked 'Place Order' button successfully!")
                    return True
            except Exception:
                continue

        logger.error("Could not find or click the 'Place Order' button.")
        return False

    def run(self) -> bool:
        """Executes the full automated flash sale process."""
        self.config.validate()
        page = self.setup_browser()

        try:
            logger.info("Opening product page: %s", self.config.item_url)
            page.goto(self.config.item_url, wait_until="domcontentloaded")

            # Pre-select variations early if available
            self.select_variations(page)
            self.set_quantity(page)

            # Wait for scheduled flash sale time if set
            if self.config.scheduled_time:
                target_ts = PreciseScheduler.parse_target_time(self.config.scheduled_time)
                logger.info("Scheduled target: %s (epoch %s)", self.config.scheduled_time, target_ts)
                PreciseScheduler.wait_until(
                    target_ts,
                    pre_offset_ms=self.config.refresh_offset_ms,
                    progress_callback=lambda rem: logger.info("Countdown: %.1f seconds remaining", rem),
                )
                logger.info("Target time reached! Reloading page for flash sale update...")
                page.reload(wait_until="domcontentloaded")
                # Re-select variation after refresh
                self.select_variations(page)
                self.set_quantity(page)

            # Click Buy Now
            bought = self.wait_and_click_buy_now(page)
            if not bought:
                logger.error("Failed to click Buy Now.")
                return False

            # Checkout
            success = self.handle_checkout(page)
            if success:
                logger.info("Auto-checkout sequence completed successfully!")
            return success

        finally:
            self.save_cookies()
            self.close()

    def close(self) -> None:
        """Closes browser context and playwright session."""
        try:
            if self._browser_context:
                self._browser_context.close()
            if self._playwright:
                self._playwright.stop()
        except Exception as e:
            logger.warning("Error during browser teardown: %s", e)
