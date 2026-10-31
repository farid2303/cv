"""Android Debug Bridge (ADB) interaction wrapper."""

import logging
import re
import subprocess
import time
from typing import List, Optional, Tuple

logger = logging.getLogger("ShopeeAndroidBot")


class ADBController:
    """Controls an Android device via ADB for high-speed input and app management."""

    def __init__(self, device_id: Optional[str] = None):
        self.device_id = device_id
        self._adb_cmd = ["adb"]
        if self.device_id:
            self._adb_cmd.extend(["-s", self.device_id])

    def run_command(self, args: List[str]) -> subprocess.CompletedProcess:
        """Executes an adb command."""
        cmd = self._adb_cmd + args
        try:
            return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        except subprocess.CalledProcessError as e:
            logger.error("ADB command failed: %s | Error: %s", " ".join(cmd), e.stderr)
            raise

    def list_devices(self) -> List[str]:
        """Lists connected ADB devices."""
        proc = subprocess.run(["adb", "devices"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        lines = proc.stdout.strip().splitlines()
        devices = []
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 2 and parts[1] == "device":
                devices.append(parts[0])
        return devices

    def get_screen_resolution(self) -> Tuple[int, int]:
        """Gets current device screen resolution (width, height)."""
        proc = self.run_command(["shell", "wm", "size"])
        # Format usually: "Physical size: 1080x2400"
        match = re.search(r"(\d+)x(\d+)", proc.stdout)
        if match:
            return int(match.group(1)), int(match.group(2))
        return (1080, 2400)

    def open_shopee_product(self, url: str) -> None:
        """Opens product link directly in the Shopee Android App using VIEW intent."""
        logger.info("Launching Shopee deep link: %s", url)
        # Using Android VIEW intent to trigger Shopee app deep-link handler
        self.run_command([
            "shell", "am", "start",
            "-a", "android.intent.action.VIEW",
            "-d", url,
            "com.shopee.id",
        ])

    def tap(self, x: int, y: int) -> None:
        """Sends a tap event to coordinate (x, y)."""
        self.run_command(["shell", "input", "tap", str(x), str(y)])

    def tap_burst(self, x: int, y: int, count: int = 5, interval_sec: float = 0.08) -> None:
        """Sends a burst of rapid taps to the given coordinate."""
        logger.info("Executing tap burst x=%d, y=%d, count=%d", x, y, count)
        for _ in range(count):
            self.tap(x, y)
            time.sleep(interval_sec)
