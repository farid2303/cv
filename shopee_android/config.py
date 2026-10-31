"""Configuration for Android Shopee Flash Sale Bot."""

from dataclasses import dataclass, field, asdict
import json
import os
from typing import Dict, List, Optional, Tuple


@dataclass
class AndroidBotConfig:
    """Settings for automating Shopee native app on Android."""
    # Target product deep-link or universal link (e.g. https://shopee.co.id/product/...)
    product_url: str = ""
    # Scheduled flash sale kickoff: "YYYY-MM-DD HH:MM:SS" or None
    scheduled_time: Optional[str] = None
    # ADB target device serial (optional, defaults to first attached device)
    device_id: Optional[str] = None
    # Screen resolution of device (width, height), default 1080x2400 (common Android standard)
    screen_resolution: Tuple[int, int] = (1080, 2400)
    # Coordinate presets or custom points (x, y) relative to screen_resolution
    # Format: {"variation_1": [x, y], "buy_now": [x, y], "checkout_confirm": [x, y], "place_order": [x, y]}
    coordinates: Dict[str, Tuple[int, int]] = field(
        default_factory=lambda: {
            "buy_now_product_page": (850, 2300),   # Bottom right 'Beli Sekarang'
            "variation_option": (300, 1800),       # First variation option in popup
            "buy_now_popup_confirm": (540, 2300),  # Confirm button at bottom of variation popup
            "checkout_place_order": (850, 2300),   # Bottom right 'Buat Pesanan'
        }
    )
    # Milliseconds before scheduled time to launch the deep-link in Shopee App
    open_app_offset_ms: int = 1500
    # Milliseconds between consecutive taps in the checkout sequence
    tap_interval_ms: int = 120
    # Number of rapid retry taps on 'Beli Sekarang'
    buy_now_burst_count: int = 10
    # Dry run mode: Stops before clicking final 'Buat Pesanan'
    dry_run: bool = True

    @classmethod
    def from_json_file(cls, path: str) -> "AndroidBotConfig":
        """Load configuration from a JSON file."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)

    def to_json_file(self, path: str) -> None:
        """Save configuration to a JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)

    def validate(self) -> None:
        """Validate config parameters."""
        if not self.product_url:
            raise ValueError("product_url must not be empty.")
        if self.tap_interval_ms < 10:
            raise ValueError("tap_interval_ms should be at least 10ms.")
