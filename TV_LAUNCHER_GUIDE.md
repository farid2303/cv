# Panasonic Android TV Launcher Customization Guide

This guide walks you through modifying the default launcher on your Panasonic Android TV and setting up a clean iOS-style launcher (or any custom launcher) using:
- **Option A:** Your **Laptop** (Windows, macOS, or Linux).
- **Option B:** Your **Samsung Android Phone** (via Termux).

---

## Prerequisites

1. **Panasonic Android TV** and your **Laptop / Samsung Phone** must be connected to the **same local Wi-Fi network**.
2. For Laptop: Windows (PowerShell/CMD), macOS (Terminal), or Linux.
3. For Samsung Phone: **Termux** app installed (from F-Droid or GitHub release).
4. The APK file for the iOS-style launcher downloaded on your laptop or phone.
   - *Recommendation:* Choose an Android TV-compatible launcher (e.g., Projectivy Launcher, FLauncher, or a lean ATV iOS theme) for smooth remote control (D-pad) navigation. Standard mobile phone iOS launchers may require a mouse pointer / air mouse.

---

## Step 1: Enable Developer Options & USB / Wireless Debugging on TV

1. On your Panasonic TV, go to **Settings** > **Device Preferences** > **About**.
2. Scroll down to **Build** (or Android TV OS build) and click it **7 times** until you see the message: `"You are now a developer!"`.
3. Return to **Device Preferences** and open **Developer options**.
4. Enable **USB debugging** (and **Wireless debugging** if shown on Android 11+).
5. Check your TV's IP address:
   - Go to **Settings** > **Network & Internet** > select your connected Wi-Fi network to view the **IP address** (e.g. `192.168.1.150`).

---

## Option A: Installing via Laptop (Windows, macOS, Linux)

### 1. Install ADB (Android Debug Bridge) on your Laptop

- **Windows:**
  - Option 1 (Winget): Open PowerShell and run:
    ```powershell
    winget install Google.PlatformTools
    ```
  - Option 2 (Manual): Download the official [SDK Platform-Tools for Windows](https://developer.android.com/tools/releases/platform-tools), extract the zip folder (e.g. to `C:\platform-tools`), and open PowerShell or Command Prompt inside that folder.

- **macOS:**
  - Open Terminal and install via Homebrew:
    ```bash
    brew install android-platform-tools
    ```

- **Linux (Ubuntu / Debian / Mint):**
  - Open Terminal and run:
    ```bash
    sudo apt update && sudo apt install -y adb
    ```

---

### 2. Connect your Laptop to the TV Wirelessly

In your Laptop terminal (PowerShell, Command Prompt, or Terminal):

```bash
adb connect <TV_IP_ADDRESS>:5555
```

Example:
```bash
adb connect 192.168.1.150:5555
```

> **Note for Android TV 11+ (Wireless Debugging with Pairing):**
> If your TV requires pairing code, look at Developer Options > Wireless Debugging:
> ```bash
> adb pair <TV_IP_ADDRESS>:<PAIRING_PORT> <PAIRING_CODE>
> adb connect <TV_IP_ADDRESS>:<CONNECT_PORT>
> ```

Look at your Panasonic TV screen:
A popup will appear asking **"Allow USB debugging?"**.
Check **"Always allow from this computer"** and select **OK** using your TV remote.

Verify the connection:
```bash
adb devices
```
You should see:
```
192.168.1.150:5555    device
```

---

### 3. Install the iOS Launcher APK from Laptop

Download the launcher APK to your laptop (for example, save as `ios_launcher.apk` in your current folder or Downloads folder).

Run:
```bash
adb install -r ios_launcher.apk
```
*(If on Windows with full path: `adb install -r "C:\Users\YourUser\Downloads\ios_launcher.apk"`)*

---

### 4. Set the New Launcher as Default

1. **Test-launch the newly installed app:**
   ```bash
   adb shell monkey -p <package.name> -c android.intent.category.LAUNCHER 1
   ```
   *(To find third-party package names: `adb shell pm list packages -3`)*

2. **Disable the stock Panasonic / Google TV home launcher:**
   - For standard Android TV:
     ```bash
     adb shell pm disable-user --user 0 com.google.android.tvlauncher
     ```
   - For Google TV:
     ```bash
     adb shell pm disable-user --user 0 com.google.android.apps.tv.launcherx
     ```

3. Press the **Home** button on your Panasonic TV remote. The TV will now default directly to your iOS Clean Edition launcher!

---

### 5. Automated Laptop Helper Scripts

To make this effortless, you can use the included desktop scripts:

- **Windows Laptop:**
  Double-click `setup_tv_launcher_windows.bat` or run in Command Prompt:
  ```cmd
  setup_tv_launcher_windows.bat
  ```

- **macOS / Linux Laptop:**
  Run in Terminal:
  ```bash
  chmod +x setup_tv_launcher_desktop.sh
  ./setup_tv_launcher_desktop.sh
  ```

---

## Option B: Installing via Samsung Phone (Termux)

### 1. Install ADB Tools in Termux
Open Termux on your Samsung phone and run:
```bash
pkg update && pkg install -y android-tools
```

### 2. Connect to Panasonic TV
```bash
adb connect <TV_IP_ADDRESS>:5555
```
Accept the USB debugging prompt on your TV screen.

### 3. Install the iOS Launcher APK
Grant storage permission:
```bash
termux-setup-storage
adb install -r /sdcard/Download/your_ios_launcher.apk
```

### 4. Disable Stock Launcher
```bash
adb shell pm disable-user --user 0 com.google.android.tvlauncher
adb shell pm disable-user --user 0 com.google.android.apps.tv.launcherx
```

### 5. Automated Phone Script
Inside Termux:
```bash
chmod +x setup_tv_launcher.sh
./setup_tv_launcher.sh
```

---

## Rollback / Recovery (Restore Original Launcher)

If you ever want to revert back to Panasonic's stock launcher:

```bash
adb shell pm enable com.google.android.tvlauncher
adb shell pm enable com.google.android.apps.tv.launcherx
adb shell input keyevent KEYCODE_HOME
```
