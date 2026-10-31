"""Configuration module for Shopee Flash Sale Bot."""

from dataclasses import dataclass, field, asdict
import json
import os
from typing import List, Optional


@dataclass
class BotConfig:
    """Configuration options for the flash sale bot."""
    item_url: str = ""
    # Format: "YYYY-MM-DD HH:MM:SS" or empty for immediate execution
    scheduled_time: Optional[str] = None
    # Variations/attributes to pick in order (e.g. ["Hitam", "XL"])
    variations: List[str] = field(default_factory=list)
    quantity: int = 1
    # Payment method keywords (e.g. "ShopeePay", "COD", "Transfer Bank")
    payment_method: Optional[str] = None
    # Shipping option keyword if specific preference
    shipping_option: Optional[str] = None
    # Pin for ShopeePay (if applicable)
    shopeepay_pin: Optional[str] = None
    # Offsets and timing (in milliseconds)
    refresh_offset_ms: int = 800  # Milliseconds before scheduled time to start refresh
    click_interval_ms: int = 50   # Interval between click retry attempts
    max_checkout_wait_sec: int = 15
    # Browser options
    headless: bool = False
    browser_type: str = "chromium"
    user_data_dir: str = "./shopee_user_data"
    cookies_file: Optional[str] = "./cookies.json"
    # Dry run mode: Stops before final 'Place Order' / 'Buat Pesanan' button click
    dry_run: bool = True

    @classmethod
    def from_json_file(cls, path: str) -> "BotConfig":
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
        """Validate critical configuration fields."""
        if not self.item_url:
            raise ValueError("item_url must not be empty.")
        if self.quantity < 1:
            raise ValueError("quantity must be at least 1.")
