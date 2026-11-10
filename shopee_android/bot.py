"""Core execution engine for Android Shopee Flash Sale Bot."""

import logging
import time
from typing import Optional

from shopee_android.config import AndroidBotConfig
from shopee_android.adb_controller import ADBController
from shopee_bot.scheduler import PreciseScheduler

logger = logging.getLogger("ShopeeAndroidBot")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class ShopeeAndroidBot:
    """Coordinates the flash sale execution sequence on an Android device."""

    def __init__(self, config: AndroidBotConfig, controller: Optional[ADBController] = None):
        self.config = config
        self.adb = controller or ADBController(device_id=config.device_id)

    def execute_sequence(self) -> bool:
        """Executes the flash sale tapping sequence."""
        coords = self.config.coordinates
        interval = self.config.tap_interval_ms / 1000.0

        # Step 1: Open product in Shopee App
        logger.info("Opening Shopee product page...")
        self.adb.open_shopee_product(self.config.product_url)
        time.sleep(1.2)  # Short wait for activity transition

        # Step 2: Tap 'Beli Sekarang' (Buy Now)
        buy_now_x, buy_now_y = coords.get("buy_now_product_page", (850, 2300))
        logger.info("Burst clicking 'Beli Sekarang' at (%d, %d)...", buy_now_x, buy_now_y)
        self.adb.tap_burst(buy_now_x, buy_now_y, count=self.config.buy_now_burst_count, interval_sec=interval)

        # Step 3: Tap Variation option if defined
        if "variation_option" in coords:
            var_x, var_y = coords["variation_option"]
            logger.info("Selecting variation at (%d, %d)...", var_x, var_y)
            self.adb.tap(var_x, var_y)
            time.sleep(interval)

        # Step 4: Confirm purchase in variation popup
        if "buy_now_popup_confirm" in coords:
            conf_x, conf_y = coords["buy_now_popup_confirm"]
            logger.info("Confirming purchase popup at (%d, %d)...", conf_x, conf_y)
            self.adb.tap(conf_x, conf_y)
            time.sleep(0.8)  # Wait for checkout screen to load

        # Step 5: Final 'Buat Pesanan' (Place Order)
        if self.config.dry_run:
            logger.info("[DRY RUN] Finished checkout flow. Final 'Buat Pesanan' tap skipped.")
            return True

        if "checkout_place_order" in coords:
            order_x, order_y = coords["checkout_place_order"]
            logger.info("Placing order at (%d, %d)...", order_x, order_y)
            self.adb.tap(order_x, order_y)
            logger.info("Order placed successfully on Android Shopee app!")

        return True

    def run(self) -> bool:
        """Runs the scheduled flash sale sequence."""
        self.config.validate()

        if self.config.scheduled_time:
            target_ts = PreciseScheduler.parse_target_time(self.config.scheduled_time)
            logger.info("Waiting for scheduled flash sale: %s (epoch %s)", self.config.scheduled_time, target_ts)
            PreciseScheduler.wait_until(
                target_ts,
                pre_offset_ms=self.config.open_app_offset_ms,
                progress_callback=lambda rem: logger.info("Android countdown: %.1f seconds remaining", rem),
            )

        return self.execute_sequence()
