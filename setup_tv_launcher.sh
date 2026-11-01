#!/usr/bin/env bash
#
# setup_tv_launcher.sh - Configure Panasonic Android TV Launcher via Termux
#
# Enables connecting to Panasonic Android TV over Wireless ADB, installing
# an alternative launcher (such as an iOS style launcher / ATV launcher),
# setting it as default, and restoring the stock launcher if needed.
#

set -euo pipefail

TV_IP=""
TV_PORT="5555"

print_header() {
    echo "========================================================"
    echo " Panasonic Android TV Launcher Manager (Termux / ADB)  "
    echo "========================================================"
}

check_dependencies() {
    echo "[*] Checking Termux dependencies..."
    if ! command -v adb >/dev/null 2>&1; then
        echo "[!] 'adb' not found in PATH."
        echo "    Installing android-tools..."
        pkg install -y android-tools || { apt update && apt install -y android-tools; }
    else
        echo "[+] 'adb' is ready."
    fi
}

connect_tv() {
    echo ""
    echo "=== Step 1: Connect to Panasonic Android TV ==="
    read -r -p "Enter TV IP address (e.g. 192.168.1.150): " TV_IP
    read -r -p "Enter Port [default: 5555]: " input_port
    TV_PORT="${input_port:-5555}"

    echo "[*] Connecting to ${TV_IP}:${TV_PORT}..."
    adb disconnect >/dev/null 2>&1 || true
    adb connect "${TV_IP}:${TV_PORT}"

    echo "[*] Checking connected ADB devices..."
    adb devices
    echo ""
    echo "[*] Note: If TV prompts 'Allow USB debugging?', select 'Always allow' on TV screen using remote."
}

list_launchers() {
    echo ""
    echo "=== Installed Launchers on TV ==="
    adb -s "${TV_IP}:${TV_PORT}" shell cmd package query-intent-activities -a android.intent.action.MAIN -c android.intent.category.HOME || true
}

install_launcher() {
    echo ""
    echo "=== Step 2: Install Launcher APK ==="
    read -r -p "Enter path to launcher APK (e.g. /sdcard/Download/ios_launcher.apk): " apk_path
    if [[ ! -f "$apk_path" ]]; then
        echo "[!] File '$apk_path' does not exist."
        return 1
    fi
    echo "[*] Installing APK to TV..."
    adb -s "${TV_IP}:${TV_PORT}" install -r "$apk_path"
    echo "[+] Launcher installed successfully."
}

set_default_launcher() {
    echo ""
    echo "=== Step 3: Set Default Launcher ==="
    echo "To set a new launcher as default on Android TV, common Panasonic / Google TV stock packages include:"
    echo " - com.google.android.tvlauncher (Android TV Launcher)"
    echo " - com.google.android.apps.tv.launcherx (Google TV Launcher)"
    echo " - com.panasonic.tv.* (Panasonic custom system launcher if present)"
    echo ""
    read -r -p "Enter package name of new launcher to launch (e.g. com.ioslauncher.clean): " new_pkg
    read -r -p "Do you want to disable stock Google/Android TV launcher? (y/n): " disable_choice

    if [[ "$disable_choice" =~ ^[Yy]$ ]]; then
        echo "[*] Disabling stock launcher packages..."
        adb -s "${TV_IP}:${TV_PORT}" shell pm disable-user --user 0 com.google.android.tvlauncher 2>/dev/null || true
        adb -s "${TV_IP}:${TV_PORT}" shell pm disable-user --user 0 com.google.android.apps.tv.launcherx 2>/dev/null || true
        echo "[+] Stock launcher disabled. The TV will now default to $new_pkg."
    fi

    if [[ -n "$new_pkg" ]]; then
        echo "[*] Launching new launcher..."
        adb -s "${TV_IP}:${TV_PORT}" shell monkey -p "$new_pkg" -c android.intent.category.LAUNCHER 1 || true
        adb -s "${TV_IP}:${TV_PORT}" shell input keyevent KEYCODE_HOME || true
    fi
}

restore_stock_launcher() {
    echo ""
    echo "=== Rollback: Restore Stock Panasonic / Google TV Launcher ==="
    echo "[*] Re-enabling stock TV launcher packages..."
    adb -s "${TV_IP}:${TV_PORT}" shell pm enable com.google.android.tvlauncher 2>/dev/null || true
    adb -s "${TV_IP}:${TV_PORT}" shell pm enable com.google.android.apps.tv.launcherx 2>/dev/null || true
    adb -s "${TV_IP}:${TV_PORT}" shell input keyevent KEYCODE_HOME || true
    echo "[+] Stock launcher restored!"
}

menu() {
    print_header
    while true; do
        echo ""
        echo "Select an option:"
        echo "1) Check / Install ADB in Termux"
        echo "2) Connect to Panasonic TV via Wireless ADB"
        echo "3) List Installed Home Launchers on TV"
        echo "4) Install New Launcher APK"
        echo "5) Activate / Set New Launcher as Default"
        echo "6) Restore Default Stock TV Launcher (Rollback)"
        echo "7) Open interactive TV shell"
        echo "8) Exit"
        read -r -p "Choice [1-8]: " opt

        case "$opt" in
            1) check_dependencies ;;
            2) connect_tv ;;
            3) list_launchers ;;
            4) install_launcher ;;
            5) set_default_launcher ;;
            6) restore_stock_launcher ;;
            7) adb -s "${TV_IP}:${TV_PORT}" shell ;;
            8) echo "Goodbye!"; exit 0 ;;
            *) echo "Invalid option. Please choose between 1-8." ;;
        esac
    done
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    menu
fi
