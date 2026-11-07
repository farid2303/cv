@echo off
:: ==============================================================================
:: Panasonic Android TV Launcher Setup Tool (Windows Batch)
:: ==============================================================================
title Panasonic Android TV - Launcher Setup Tool
color 0B

echo ======================================================
echo   Panasonic Android TV - Windows Setup Tool
echo ======================================================
echo.

:: Check ADB
where adb >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] ADB command not found in PATH.
    echo Please make sure Android Platform-Tools is installed and added to PATH,
    echo or place this script inside the platform-tools folder.
    echo.
    echo Quick install via PowerShell:
    echo winget install Google.PlatformTools
    echo.
    pause
    exit /b 1
)

:MENU
echo.
echo ==================== Main Menu ====================
echo 1) Connect to Panasonic TV via Wireless ADB
echo 2) Install Launcher APK
echo 3) List Installed Third-Party Packages
echo 4) Disable Stock Launcher (Set Custom Launcher Default)
echo 5) Restore Stock Panasonic Launcher (Rollback)
echo 6) Test Home Button
echo 0) Exit
echo ===================================================
set /p CHOICE="Enter choice [0-6]: "

if "%CHOICE%"=="1" goto CONNECT
if "%CHOICE%"=="2" goto INSTALL
if "%CHOICE%"=="3" goto LIST_PKGS
if "%CHOICE%"=="4" goto DISABLE_STOCK
if "%CHOICE%"=="5" goto RESTORE
if "%CHOICE%"=="6" goto TEST_HOME
if "%CHOICE%"=="0" goto EXIT
echo Invalid choice. Please try again.
goto MENU

:CONNECT
echo.
echo --- Connect to Panasonic TV ---
set /p TV_IP="Enter your Panasonic TV IP address (e.g. 192.168.1.150): "
if "%TV_IP%"=="" (
    echo [!] IP address cannot be empty.
    goto MENU
)
set /p TV_PORT="Enter port [Press Enter for 5555]: "
if "%TV_PORT%"=="" set TV_PORT=5555

echo Connecting to %TV_IP%:%TV_PORT%...
adb connect %TV_IP%:%TV_PORT%
echo.
echo [Notice] Check your TV screen and accept "Allow USB debugging".
adb devices
pause
goto MENU

:INSTALL
echo.
echo --- Install Launcher APK ---
set /p APK_PATH="Enter full path or drag-and-drop the APK file here: "
if "%APK_PATH%"=="" (
    echo [!] Path cannot be empty.
    goto MENU
)
echo Sideloading APK to TV...
adb install -r %APK_PATH%
if %errorlevel% equ 0 (
    echo [✔] APK installed successfully!
) else (
    echo [!] Installation encountered an issue. Check TV connection.
)
pause
goto MENU

:LIST_PKGS
echo.
echo Third-party installed packages on TV:
adb shell pm list packages -3
pause
goto MENU

:DISABLE_STOCK
echo.
echo --- Disable Stock TV Launcher ---
echo 1) Standard Android TV Home (com.google.android.tvlauncher)
echo 2) Google TV Home (com.google.android.apps.tv.launcherx)
echo 3) Disable both (Safest to ensure custom launcher stays default)
set /p D_OPT="Select option [1-3]: "

if "%D_OPT%"=="1" (
    adb shell pm disable-user --user 0 com.google.android.tvlauncher
)
if "%D_OPT%"=="2" (
    adb shell pm disable-user --user 0 com.google.android.apps.tv.launcherx
)
if "%D_OPT%"=="3" (
    adb shell pm disable-user --user 0 com.google.android.tvlauncher
    adb shell pm disable-user --user 0 com.google.android.apps.tv.launcherx
)
echo [✔] Stock launcher disabled!
adb shell input keyevent KEYCODE_HOME
pause
goto MENU

:RESTORE
echo.
echo --- Restore Stock Panasonic Launcher ---
adb shell pm enable com.google.android.tvlauncher
adb shell pm enable com.google.android.apps.tv.launcherx
adb shell input keyevent KEYCODE_HOME
echo [✔] Stock launchers re-enabled!
pause
goto MENU

:TEST_HOME
echo Simulating Home keyevent...
adb shell input keyevent KEYCODE_HOME
goto MENU

:EXIT
echo Goodbye!
exit /b 0
