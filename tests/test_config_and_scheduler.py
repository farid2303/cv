"""Unit tests for config and scheduler modules."""

import os
import tempfile
import time
import unittest
from shopee_bot.config import BotConfig
from shopee_bot.scheduler import PreciseScheduler


class TestBotConfig(unittest.TestCase):
    def test_default_config(self):
        config = BotConfig()
        self.assertEqual(config.quantity, 1)
        self.assertTrue(config.dry_run)
        self.assertFalse(config.headless)

    def test_validate(self):
        config = BotConfig(item_url="")
        with self.assertRaises(ValueError):
            config.validate()

        config = BotConfig(item_url="https://shopee.co.id/item", quantity=0)
        with self.assertRaises(ValueError):
            config.validate()

        config = BotConfig(item_url="https://shopee.co.id/item", quantity=2)
        config.validate()  # should not raise

    def test_json_serialization(self):
        config = BotConfig(
            item_url="https://shopee.co.id/product/123",
            variations=["Hitam", "XL"],
            quantity=2,
            payment_method="ShopeePay",
        )
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            config.to_json_file(tmp_path)
            loaded = BotConfig.from_json_file(tmp_path)
            self.assertEqual(loaded.item_url, config.item_url)
            self.assertEqual(loaded.variations, ["Hitam", "XL"])
            self.assertEqual(loaded.quantity, 2)
            self.assertEqual(loaded.payment_method, "ShopeePay")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class TestPreciseScheduler(unittest.TestCase):
    def test_parse_target_time(self):
        time_str = "2025-12-31 23:59:59"
        ts = PreciseScheduler.parse_target_time(time_str)
        self.assertGreater(ts, 0)

    def test_wait_until(self):
        target = time.time() + 0.15  # 150 ms in future
        t_start = time.time()
        PreciseScheduler.wait_until(target, pre_offset_ms=0)
        t_end = time.time()
        self.assertGreaterEqual(t_end, target - 0.01)
        self.assertLess(t_end - t_start, 0.3)


if __name__ == "__main__":
    unittest.main()
