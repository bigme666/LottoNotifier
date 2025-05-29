#!/usr/bin/env python3
"""
Italian Lottery Results Telegram Bot

This bot scrapes lottery results from the official ADM website
and publishes them to Telegram users.

Author: Lottery Bot
Version: 1.0
"""

import sys
import signal
import logging
from bot import LotteryBot
from config import logger

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    logger.info("Received shutdown signal. Stopping bot...")
    sys.exit(0)

def main():
    """Main function to start the lottery bot."""
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        logger.info("=" * 50)
        logger.info("ITALIAN LOTTERY TELEGRAM BOT")
        logger.info("=" * 50)
        logger.info("Initializing bot...")
        
        # Create and start the bot
        bot = LotteryBot()
        
        logger.info("Bot initialized successfully")
        logger.info("Starting bot polling...")
        
        # Run the bot
        bot.run()
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please ensure TELEGRAM_BOT_TOKEN environment variable is set")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Unexpected error starting bot: {e}")
        sys.exit(1)
    
    finally:
        logger.info("Bot shutdown complete")

if __name__ == "__main__":
    main()
