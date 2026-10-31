"""CLI Runner and Calibration tool for Android Shopee Bot."""

import argparse
import sys
from shopee_android.config import AndroidBotConfig
from shopee_android.adb_controller import ADBController
from shopee_android.bot import ShopeeAndroidBot


def build_parser() -> argparse.ArgumentParser:
    """Creates the argument parser."""
    parser = argparse.ArgumentParser(
        description="Shopee Android Native App Flash Sale Bot",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to JSON configuration file",
    )
    parser.add_argument(
        "--url",
        type=str,
        help="Shopee product link to open in app",
    )
    parser.add_argument(
        "--time",
        type=str,
        help="Scheduled flash sale time in 'YYYY-MM-DD HH:MM:SS' format",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Specific ADB device serial ID",
    )
    parser.add_argument(
        "--dry-run",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Dry run mode (stops before final Buat Pesanan tap)",
    )
    parser.add_argument(
        "--check-devices",
        action="store_true",
        help="Check and list connected Android devices via ADB",
    )
    parser.add_argument(
        "--get-screen-size",
        action="store_true",
        help="Fetch resolution of connected Android phone",
    )
    return parser


def main() -> None:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args()

    controller = ADBController(device_id=args.device)

    if args.check_devices:
        devices = controller.list_devices()
        print(f"Connected Android Devices ({len(devices)}):")
        for dev in devices:
            print(f" - {dev}")
        if not devices:
            print("No devices found. Ensure USB Debugging is ON and 'adb devices' works.")
        return

    if args.get_screen_size:
        res = controller.get_screen_resolution()
        print(f"Connected device screen resolution: {res[0]}x{res[1]}")
        return

    if args.config:
        config = AndroidBotConfig.from_json_file(args.config)
    else:
        config = AndroidBotConfig()

    if args.url:
        config.product_url = args.url
    if args.time:
        config.scheduled_time = args.time
    if args.device:
        config.device_id = args.device
    if args.dry_run is not None:
        config.dry_run = args.dry_run

    if not config.product_url:
        parser.print_help()
        print("\nError: Please provide --url or a config file with 'product_url'.")
        sys.exit(1)

    print("=== Shopee Android Flash Sale Bot ===")
    print(f"Product URL: {config.product_url}")
    print(f"Scheduled Time: {config.scheduled_time or 'Immediate'}")
    print(f"Dry Run: {config.dry_run}")
    print(f"Coordinates: {config.coordinates}")

    bot = ShopeeAndroidBot(config, controller=controller)
    success = bot.run()
    if success:
        print("Sequence executed successfully!")
    else:
        print("Sequence failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
