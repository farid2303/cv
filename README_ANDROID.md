# Shopee Android Flash Sale Auto-Checkout Bot

Automate purchases directly inside the official **Shopee Android App** using ADB (Android Debug Bridge) or directly on the phone via **Termux**.

---

## How It Works

1. **Direct Deep Link Launch**: Opens the target product directly in the native Shopee Android App (`am start -a android.intent.action.VIEW -d <url> com.shopee.id`).
2. **Sub-millisecond Precision Scheduler**: Countdown loop calculates flash sale time and triggers app opening and tap sequences with millisecond precision.
3. **Rapid Tapping Execution**: Sends automated taps to coordinates for **Beli Sekarang**, variations, and **Buat Pesanan**.
4. **Safe Dry-Run Mode**: Allows you to test the flow without placing real orders (`--dry-run`).

---

## Setup Options

You can run this program in two ways:
- **Option A (Recommended)**: Run from your PC connected to your Android phone via USB or Wi-Fi (Wireless Debugging).
- **Option B**: Run directly on your Android phone using **Termux**.

---

### Option A: From PC/Laptop to Android Phone (USB or Wireless ADB)

#### 1. Enable Developer Options & USB Debugging on your phone:
1. Open phone **Settings** > **About Phone** (Tentang Ponsel).
2. Tap **Build Number** (Nomor Versi) 7 times until you see *"You are now a developer!"*.
3. Go to **Settings** > **System** > **Developer Options** (Opsi Pengembang).
4. Turn ON:
   - **USB Debugging** (Debugging USB).
   - **USB Debugging (Security settings)** / Allow mock input if on Xiaomi/POCO/MIUI/HyperOS.

#### 2. Check Device Connection:
Connect phone to PC with USB cable, then run:
```bash
python3 -m shopee_android.cli --check-devices
```
You should see your phone listed.

#### 3. Test Tap Coordinates (Dry Run):
```bash
python3 -m shopee_android.cli \
  --url "https://shopee.co.id/product/12345/67890" \
  --dry-run
```

#### 4. Schedule for a Flash Sale:
```bash
python3 -m shopee_android.cli \
  --url "https://shopee.co.id/product/12345/67890" \
  --time "2026-11-01 12:00:00" \
  --no-dry-run
```

---

### Option B: Directly on Android Phone via Termux

1. Install **Termux** from F-Droid (or GitHub).
2. Inside Termux, install Python and ADB:
   ```bash
   pkg update
   pkg install python git android-tools
   ```
3. Enable Wireless Debugging on your Android phone (Android 11+):
   - In Developer Options, enable **Wireless Debugging**.
   - Note the IP address and port (e.g. `127.0.0.1:41234`).
   - Pair in Termux:
     ```bash
     adb pair 127.0.0.1:<pairing-port> <pairing-code>
     adb connect 127.0.0.1:<connect-port>
     ```
4. Clone and run:
   ```bash
   python3 -m shopee_android.cli \
     --url "https://shopee.co.id/product/12345/67890" \
     --time "2026-11-01 12:00:00" \
     --dry-run
   ```

---

## Finding & Customizing Tap Coordinates

Different phone screen resolutions (1080x2400, 1440x3200, 720x1600) have slight coordinate differences.

1. Enable **Pointer Location** (Lokasi Penunjuk) in Developer Options on your phone.
   - When you touch the screen, Android displays exact `X` and `Y` coordinates on the top bar!
2. Open Shopee and note the (X, Y) coordinates of:
   - *Beli Sekarang* button.
   - Variation button (e.g. size/color).
   - Final *Buat Pesanan* button.
3. Edit `config.android.example.json` and pass it to the bot:
   ```bash
   python3 -m shopee_android.cli --config config.android.example.json
   ```
