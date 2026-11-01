# Panasonic Android TV Launcher Customization via Samsung Phone (Termux)

This guide walks you through modifying the default launcher on your Panasonic Android TV and setting up a clean iOS-style launcher (or any custom launcher) using Termux from your Samsung Android phone.

---

## Prerequisites

1. **Panasonic Android TV** and **Samsung Phone** must be connected to the **same Wi-Fi network**.
2. **Termux** app installed on your Samsung phone (from F-Droid or GitHub release).
3. The APK file for the iOS-style launcher downloaded on your phone (e.g., in `/sdcard/Download/`).
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

## Step 2: Install ADB Tools in Termux on Samsung Phone

Open Termux on your phone and run:

```bash
pkg update && pkg install -y android-tools
```

---

## Step 3: Connect to Panasonic TV via Wireless ADB

In Termux:

```bash
adb connect <TV_IP_ADDRESS>:5555
```

Example:
```bash
adb connect 192.168.1.150:5555
```

> **Important:** Look at your Panasonic TV screen! A prompt will appear saying: **"Allow USB debugging?"**.
> Check **"Always allow from this computer"** and select **OK** using your TV remote.

Verify the connection:
```bash
adb devices
```
You should see:
```
192.168.1.150:5555    device
```

---

## Step 4: Install the iOS Launcher APK

Grant Termux storage access (if not already granted):
```bash
termux-setup-storage
```

Push and install the launcher APK directly from your phone to the TV:
```bash
adb install -r /sdcard/Download/your_ios_launcher.apk
```

---

## Step 5: Set the New Launcher as Default

Find the package name of your newly installed launcher:
```bash
adb shell pm list packages -3
```

Launch the new launcher to test it:
```bash
adb shell monkey -p <package.name> -c android.intent.category.LAUNCHER 1
```

### Disable the Stock Android / Google TV Launcher
To make the TV stay on your new launcher when pressing the Home button:

For standard Android TV:
```bash
adb shell pm disable-user --user 0 com.google.android.tvlauncher
```

For Google TV:
```bash
adb shell pm disable-user --user 0 com.google.android.apps.tv.launcherx
```

Now press the **Home** button on your remote. Your new iOS-style launcher will open directly!

---

## Step 6: Easy Automated Script

You can also run our automated script directly inside Termux:

```bash
chmod +x setup_tv_launcher.sh
./setup_tv_launcher.sh
```
This interactive script will guide you through connecting, installing, enabling, and rolling back when needed.

---

## Rollback / Recovery (Restore Original Launcher)

If you ever want to revert back to Panasonic's stock launcher:

```bash
adb shell pm enable com.google.android.tvlauncher
adb shell pm enable com.google.android.apps.tv.launcherx
adb shell input keyevent KEYCODE_HOME
```
