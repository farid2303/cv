"""Command Line Interface for Shopee Flash Sale Bot."""

import argparse
import sys
from shopee_bot.config import BotConfig
from shopee_bot.bot import ShopeeFlashSaleBot


def build_parser() -> argparse.ArgumentParser:
    """Creates the argument parser."""
    parser = argparse.ArgumentParser(
        description="Shopee Flash Sale Automated Checkout Bot",
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
        help="Shopee product URL",
    )
    parser.add_argument(
        "--time",
        type=str,
        help="Scheduled flash sale time in 'YYYY-MM-DD HH:MM:SS' format",
    )
    parser.add_argument(
        "--variation",
        action="append",
        dest="variations",
        help="Product variation/option to select (can be specified multiple times, e.g. --variation 'Black' --variation 'XL')",
    )
    parser.add_argument(
        "--quantity",
        type=int,
        default=1,
        help="Quantity to purchase",
    )
    parser.add_argument(
        "--payment",
        type=str,
        help="Payment method name (e.g. 'ShopeePay', 'COD')",
    )
    parser.add_argument(
        "--dry-run",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Dry run mode (stops right before clicking 'Buat Pesanan' / 'Place Order')",
    )
    parser.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Run browser in headless mode",
    )
    parser.add_argument(
        "--init-login",
        action="store_true",
        help="Open browser interactively so user can log in to Shopee and save cookies",
    )
    return parser


def main() -> None:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args()

    if args.config:
        config = BotConfig.from_json_file(args.config)
    else:
        config = BotConfig()

    if args.url:
        config.item_url = args.url
    if args.time:
        config.scheduled_time = args.time
    if args.variations:
        config.variations = args.variations
    if args.quantity:
        config.quantity = args.quantity
    if args.payment:
        config.payment_method = args.payment
    if args.dry_run is not None:
        config.dry_run = args.dry_run
    if args.headless is not None:
        config.headless = args.headless

    if args.init_login:
        print("Launching browser for user login. Please log in manually and close the browser or press Ctrl+C when done.")
        config.item_url = config.item_url or "https://shopee.co.id/buyer/login"
        config.dry_run = True
        bot = ShopeeFlashSaleBot(config)
        page = bot.setup_browser()
        page.goto(config.item_url)
        print("Waiting for login... Press Enter in terminal once logged in to save session:")
        try:
            input()
        except KeyboardInterrupt:
            pass
        bot.save_cookies()
        bot.close()
        print(f"Session saved to {config.user_data_dir} and {config.cookies_file}")
        return

    if not config.item_url:
        parser.print_help()
        print("\nError: Please specify --url or provide a config file with 'item_url'.")
        sys.exit(1)

    print("Starting Shopee Flash Sale Bot...")
    print(f"Target URL: {config.item_url}")
    print(f"Scheduled Time: {config.scheduled_time or 'Immediate'}")
    print(f"Dry Run: {config.dry_run}")
    print(f"Variations: {config.variations}")
    print(f"Quantity: {config.quantity}")

    bot = ShopeeFlashSaleBot(config)
    success = bot.run()
    if success:
        print("Flash sale operation completed successfully.")
    else:
        print("Flash sale operation did not complete.")
        sys.exit(1)


if __name__ == "__main__":
    main()
