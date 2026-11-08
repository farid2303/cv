import os
import unittest
from playwright.sync_api import sync_playwright

class TestPagePerformance(unittest.TestCase):
    def test_index_image_attributes_and_load(self):
        index_path = os.path.abspath("index.html")
        file_url = f"file://{index_path}"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

            page.goto(file_url)

            # Check profile image exists and has explicit width, height, and decoding
            img = page.locator("img[alt='Gambar profile']")
            self.assertEqual(img.count(), 1, "Profile image should be present")

            width_attr = img.get_attribute("width")
            height_attr = img.get_attribute("height")
            decoding_attr = img.get_attribute("decoding")
            src_attr = img.get_attribute("src")

            self.assertEqual(width_attr, "156")
            self.assertEqual(height_attr, "209")
            self.assertEqual(decoding_attr, "async")
            self.assertIn("/", src_attr)
            self.assertNotIn("\\", src_attr)

            # Verify image loaded successfully without broken state
            is_loaded = page.evaluate("""() => {
                const img = document.querySelector("img[alt='Gambar profile']");
                return img && img.complete && img.naturalWidth > 0;
            }""")
            self.assertTrue(is_loaded, "Profile image should load completely")

            self.assertEqual(console_errors, [], "There should be no console errors")
            browser.close()

if __name__ == "__main__":
    unittest.main()
