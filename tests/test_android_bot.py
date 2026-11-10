"""Tests for Shopee Android Bot and ADB Controller."""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, call

from shopee_android.config import AndroidBotConfig
from shopee_android.adb_controller import ADBController
from shopee_android.bot import ShopeeAndroidBot


class TestAndroidBotConfig(unittest.TestCase):
    def test_default_config(self):
        config = AndroidBotConfig()
        self.assertTrue(config.dry_run)
        self.assertEqual(config.screen_resolution, (1080, 2400))
        self.assertIn("buy_now_product_page", config.coordinates)

    def test_validation(self):
        config = AndroidBotConfig(product_url="")
        with self.assertRaises(ValueError):
            config.validate()

        config = AndroidBotConfig(product_url="https://shopee.co.id/item", tap_interval_ms=5)
        with self.assertRaises(ValueError):
            config.validate()

    def test_json_serialization(self):
        config = AndroidBotConfig(
            product_url="https://shopee.co.id/test-product",
            screen_resolution=(720, 1600),
            dry_run=False,
        )
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            config.to_json_file(tmp_path)
            loaded = AndroidBotConfig.from_json_file(tmp_path)
            self.assertEqual(loaded.product_url, config.product_url)
            self.assertEqual(loaded.screen_resolution, [720, 1600])
            self.assertFalse(loaded.dry_run)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class TestShopeeAndroidBot(unittest.TestCase):
    def test_execute_sequence_dry_run(self):
        mock_adb = MagicMock(spec=ADBController)
        config = AndroidBotConfig(
            product_url="https://shopee.co.id/item123",
            dry_run=True,
            buy_now_burst_count=2,
            tap_interval_ms=10,
        )

        bot = ShopeeAndroidBot(config, controller=mock_adb)
        success = bot.execute_sequence()

        self.assertTrue(success)
        mock_adb.open_shopee_product.assert_called_once_with("https://shopee.co.id/item123")
        mock_adb.tap_burst.assert_called_once()
        # In dry run mode, checkout_place_order tap must not be called
        all_calls = [c[0] for c in mock_adb.tap.call_args_list]
        place_order_coord = config.coordinates["checkout_place_order"]
        self.assertNotIn(place_order_coord, all_calls)

    def test_execute_sequence_live(self):
        mock_adb = MagicMock(spec=ADBController)
        config = AndroidBotConfig(
            product_url="https://shopee.co.id/item123",
            dry_run=False,
            buy_now_burst_count=2,
            tap_interval_ms=10,
        )

        bot = ShopeeAndroidBot(config, controller=mock_adb)
        success = bot.execute_sequence()

        self.assertTrue(success)
        mock_adb.open_shopee_product.assert_called_once_with("https://shopee.co.id/item123")
        # In live mode, place order coordinate must be tapped
        place_order_coord = config.coordinates["checkout_place_order"]
        all_calls = [c[0] for c in mock_adb.tap.call_args_list]
        self.assertIn(place_order_coord, all_calls)


if __name__ == "__main__":
    unittest.main()
