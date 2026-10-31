# Shopee Flash Sale Automated Checkout Bot

A Python-based high-speed automation tool designed for Shopee flash sale purchases using Playwright browser automation with millisecond-precision scheduling.

---

## ⚠️ Disclaimer & Ethical Notice

This program is provided for educational and automated testing purposes only. Automating purchases on e-commerce platforms may violate their Terms of Service (ToS) and could lead to account limitations or bans. Use responsibly and at your own risk.

---

## Features

- **Precision Countdown Scheduler**: Sub-millisecond timing loop to trigger product reload and checkout right at the start of the flash sale window.
- **Session & Cookie Persistence**: Saves cookies and browser state so you do not need to re-login every time.
- **Variation & Quantity Auto-Selection**: Automatically selects color, size, and model variations and updates product quantity.
- **Fast Checkout Execution**: Clicks through the "Beli Sekarang" / "Buy Now" flow and handles payment option selection.
- **Safe Dry-Run Mode**: By default, runs in dry-run mode (`--dry-run`), stopping before the final order placement button so you can test risk-free.

---

## Installation

Ensure you have Python 3.9+ installed.

1. Install requirements:
   ```bash
   pip install playwright
   python3 -m playwright install chromium
   ```

---

## Quick Start & Usage

### 1. Initial Login (Save Session & Cookies)
Launch the browser once to log in with your Shopee credentials or QR code:
```bash
python3 -m shopee_bot.cli --init-login
```
Complete login in the browser window, then press Enter in the terminal to save your session.

### 2. Testing with Dry-Run
Run a dry run on a product URL:
```bash
python3 -m shopee_bot.cli \
  --url "https://shopee.co.id/product/12345/67890" \
  --variation "Hitam" \
  --variation "XL" \
  --quantity 1 \
  --dry-run
```

### 3. Scheduling for a Flash Sale
Set target flash sale time (e.g., 12:00:00 PM):
```bash
python3 -m shopee_bot.cli \
  --url "https://shopee.co.id/product/12345/67890" \
  --time "2026-11-01 12:00:00" \
  --variation "Hitam" \
  --payment "ShopeePay" \
  --no-dry-run
```

### 4. Configuration File (`config.json`)
You can also store settings in `config.json`:
```json
{
  "item_url": "https://shopee.co.id/product/12345/67890",
  "scheduled_time": "2026-11-01 12:00:00",
  "variations": ["Hitam", "L"],
  "quantity": 1,
  "payment_method": "ShopeePay",
  "refresh_offset_ms": 800,
  "click_interval_ms": 50,
  "headless": false,
  "dry_run": true
}
```
Run with config:
```bash
python3 -m shopee_bot.cli --config config.json
```

---

## Running Automated Tests

Run the test suite including mocked integration tests:
```bash
python3 -m unittest discover tests
```
