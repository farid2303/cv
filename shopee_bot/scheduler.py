"""Precise timing and scheduling module for flash sale execution."""

import time
from datetime import datetime
from typing import Callable, Optional


class PreciseScheduler:
    """Handles high-precision countdown and trigger timing for flash sales."""

    @staticmethod
    def parse_target_time(time_str: str) -> float:
        """Parse time string 'YYYY-MM-DD HH:MM:SS' into epoch timestamp."""
        dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        return dt.timestamp()

    @staticmethod
    def wait_until(
        target_timestamp: float,
        pre_offset_ms: int = 0,
        progress_callback: Optional[Callable[[float], None]] = None,
    ) -> None:
        """
        Wait until target_timestamp minus pre_offset_ms.
        Uses coarse sleep when far away, then high-resolution busy-wait loop for microsecond precision.
        """
        target_time = target_timestamp - (pre_offset_ms / 1000.0)
        last_reported_sec = -1

        while True:
            now = time.time()
            remaining = target_time - now

            if remaining <= 0:
                break

            # Report remaining seconds every integer second if callback provided
            remaining_sec_int = int(remaining)
            if progress_callback and remaining_sec_int != last_reported_sec:
                progress_callback(remaining)
                last_reported_sec = remaining_sec_int

            # Coarse sleep when remaining time is > 1.5s
            if remaining > 1.5:
                time.sleep(remaining - 1.0)
            elif remaining > 0.05:
                time.sleep(0.01)
            else:
                # Busy-wait spin for sub-millisecond precision
                pass
