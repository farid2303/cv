#!/usr/bin/env bash
# ==============================================================================
# Panasonic Android TV Launcher Setup Tool (Desktop - macOS / Linux)
# ==============================================================================

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}  Panasonic Android TV - Desktop Launcher Setup Tool  ${NC}"
echo -e "${BLUE}  (Compatible with macOS and Linux laptops)           ${NC}"
echo -e "${BLUE}======================================================${NC}\n"

check_adb() {
    if ! command -v adb >/dev/null 2>&1; then
        echo -e "${RED}[!] ADB is not installed or not found in PATH.${NC}"
        echo -e "On macOS: run ${YELLOW}brew install android-platform-tools${NC}"
        echo -e "On Ubuntu/Debian: run ${YELLOW}sudo apt update && sudo apt install -y adb${NC}"
        echo -e "On Fedora: run ${YELLOW}sudo dnf install android-tools${NC}"
        exit 1
    fi
    echo -e "${GREEN}[✔] ADB found: $(adb version | head -n 1)${NC}"
}

connect_tv() {
    echo -e "\n${YELLOW}--- Step 1: Connect to Panasonic TV ---${NC}"
    read -rp "Enter your Panasonic TV IP address (e.g. 192.168.1.150): " TV_IP
    if [[ -z "$TV_IP" ]]; then
        echo -e "${RED}[!] IP address cannot be empty.${NC}"
        return 1
    fi

    read -rp "Enter port [Default: 5555]: " TV_PORT
    TV_PORT=${TV_PORT:-5555}

    echo -e "Attempting wireless connection to ${TV_IP}:${TV_PORT}..."
    adb connect "${TV_IP}:${TV_PORT}"

    echo -e "\n${YELLOW}[Notice] If your TV shows 'Allow USB debugging?', select 'Always allow' and click OK.${NC}"
    echo "Checking connected devices:"
    adb devices
}

install_launcher() {
    echo -e "\n${YELLOW}--- Step 2: Install Launcher APK ---${NC}"
    read -rp "Enter path to launcher APK file (e.g. ./launcher.apk or ~/Downloads/launcher.apk): " APK_PATH
    # Expand tilde if present
    APK_PATH="${APK_PATH/#\~/$HOME}"

    if [[ ! -f "$APK_PATH" ]]; then
        echo -e "${RED}[!] File not found at: $APK_PATH${NC}"
        return 1
    fi

    echo -e "Sideloading APK to TV..."
    adb install -r "$APK_PATH"
    echo -e "${GREEN}[✔] APK installed successfully!${NC}"
}

list_third_party() {
    echo -e "\n${YELLOW}Third-party installed packages on TV:${NC}"
    adb shell pm list packages -3
}

disable_stock() {
    echo -e "\n${YELLOW}--- Step 3: Disable Stock TV Launcher ---${NC}"
    echo "Choose stock launcher type on your Panasonic TV:"
    echo "1) Standard Android TV Home (com.google.android.tvlauncher)"
    echo "2) Google TV Home (com.google.android.apps.tv.launcherx)"
    echo "3) Disable both (Safest to ensure custom launcher stays default)"
    read -rp "Select option [1-3]: " DISABLE_OPT

    case "$DISABLE_OPT" in
        1)
            adb shell pm disable-user --user 0 com.google.android.tvlauncher || true
            ;;
        2)
            adb shell pm disable-user --user 0 com.google.android.apps.tv.launcherx || true
            ;;
        3)
            adb shell pm disable-user --user 0 com.google.android.tvlauncher || true
            adb shell pm disable-user --user 0 com.google.android.apps.tv.launcherx || true
            ;;
        *)
            echo -e "${RED}Invalid option.${NC}"
            return 1
            ;;
    esac

    echo -e "${GREEN}[✔] Stock launcher disabled!${NC}"
    echo -e "Simulating Home button press on TV..."
    adb shell input keyevent KEYCODE_HOME || true
}

restore_stock() {
    echo -e "\n${YELLOW}--- Restore Stock Panasonic Launcher ---${NC}"
    echo "Re-enabling official Android TV & Google TV launchers..."
    adb shell pm enable com.google.android.tvlauncher || true
    adb shell pm enable com.google.android.apps.tv.launcherx || true
    adb shell input keyevent KEYCODE_HOME || true
    echo -e "${GREEN}[✔] Stock launchers restored!${NC}"
}

main_menu() {
    check_adb
    while true; do
        echo -e "\n${BLUE}================ Main Menu ================${NC}"
        echo "1) Connect to Panasonic TV via Wireless ADB"
        echo "2) Install Launcher APK"
        echo "3) List Installed Third-Party Packages"
        echo "4) Disable Stock Launcher (Enable iOS Launcher default)"
        echo "5) Restore Stock Panasonic Launcher (Rollback)"
        echo "6) Test Home Button (KEYCODE_HOME)"
        echo "0) Exit"
        read -rp "Enter choice [0-6]: " CHOICE

        case "$CHOICE" in
            1) connect_tv ;;
            2) install_launcher ;;
            3) list_third_party ;;
            4) disable_stock ;;
            5) restore_stock ;;
            6) adb shell input keyevent KEYCODE_HOME ;;
            0) echo "Goodbye!"; exit 0 ;;
            *) echo -e "${RED}Invalid option, try again.${NC}" ;;
        esac
    done
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main_menu
fi
