"""Integration tests for ShopeeFlashSaleBot using local HTTP mock server."""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import shutil
import tempfile
import threading
import unittest
from playwright.sync_api import sync_playwright

from shopee_bot.bot import ShopeeFlashSaleBot
from shopee_bot.config import BotConfig

MOCK_DIR = os.path.join(os.path.dirname(__file__), "mock_pages")


class CustomMockHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=MOCK_DIR, **kwargs)

    def do_GET(self):
        if self.path == "/checkout":
            self.path = "/checkout.html"
        elif self.path == "/" or self.path == "/product":
            self.path = "/product.html"
        return super().do_GET()


class TestShopeeBotAutomation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start mock HTTP server on random free port
        cls.server = HTTPServer(("127.0.0.1", 0), CustomMockHandler)
        cls.port = cls.server.server_port
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def test_full_bot_flow_dry_run(self):
        url = f"http://127.0.0.1:{self.port}/product"
        config = BotConfig(
            item_url=url,
            variations=["Hitam"],
            quantity=2,
            payment_method="ShopeePay",
            headless=True,
            dry_run=True,
            user_data_dir=os.path.join(self.tmp_dir, "userdata"),
            cookies_file=os.path.join(self.tmp_dir, "cookies.json"),
        )
        bot = ShopeeFlashSaleBot(config)
        success = bot.run()
        self.assertTrue(success)

    def test_full_bot_flow_live_order(self):
        url = f"http://127.0.0.1:{self.port}/product"
        config = BotConfig(
            item_url=url,
            variations=["Putih", "M"],
            quantity=1,
            payment_method="COD",
            headless=True,
            dry_run=False,
            user_data_dir=os.path.join(self.tmp_dir, "userdata"),
            cookies_file=os.path.join(self.tmp_dir, "cookies.json"),
        )
        bot = ShopeeFlashSaleBot(config)
        success = bot.run()
        self.assertTrue(success)


if __name__ == "__main__":
    unittest.main()
