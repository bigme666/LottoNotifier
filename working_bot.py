#!/usr/bin/env python3
"""
Working Telegram bot for Italian lottery results.
This version uses a simplified approach to avoid import issues.
"""

import asyncio
import logging
import os
import sys
from typing import Dict, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check if telegram token is available
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
if not BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN environment variable is required")
    sys.exit(1)

try:
    from telegram import Bot, Update
    from telegram.ext import Application, CommandHandler, ContextTypes
    telegram_available = True
    logger.info("✓ Telegram libraries imported successfully")
except ImportError as e:
    logger.error(f"✗ Telegram import failed: {e}")
    telegram_available = False

# Import our lottery scraper
try:
    from scraper import LottoScraper
    from utils import format_lottery_results
    scraper_available = True
    logger.info("✓ Lottery scraper imported successfully")
except ImportError as e:
    logger.error(f"✗ Scraper import failed: {e}")
    scraper_available = False


class WorkingLotteryBot:
    """A working lottery bot with simplified imports."""
    
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.scraper = LottoScraper() if scraper_available else None
        
        if telegram_available:
            self.application = Application.builder().token(self.bot_token).build()
            self._setup_handlers()
        else:
            self.application = None
            logger.error("Cannot create bot application - telegram libraries not available")
    
    def _setup_handlers(self):
        """Set up command handlers for the bot."""
        if not self.application:
            return
            
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("lotto", self.lotto_command))
        self.application.add_handler(CommandHandler("latest", self.lotto_command))
        self.application.add_handler(CommandHandler("test", self.test_command))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command."""
        welcome_message = """
🎰 Welcome to the Italian Lottery Results Bot!

This bot provides you with the latest lottery results from the official ADM website.

Available commands:
/start - Show this welcome message
/help - Show help information
/lotto - Get latest lottery results
/latest - Get latest lottery results (same as /lotto)
/test - Test connection to lottery website

The bot fetches real-time data from: https://www.adm.gov.it/portale/monopoli/giochi/gioco-del-lotto/lotto_g
        """
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /help command."""
        help_message = """
🎰 Italian Lottery Bot Help

Commands:
• /start - Welcome message and overview
• /help - This help message  
• /lotto - Fetch latest lottery results
• /latest - Same as /lotto
• /test - Test website connection

The bot scrapes official lottery results from the ADM (Agenzia delle Dogane e dei Monopoli) website and provides you with the most recent drawing results.

Results include numbers drawn for major Italian cities like Roma, Milano, Napoli, and others.
        """
        await update.message.reply_text(help_message)
    
    async def test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test connection to the lottery website."""
        await update.message.reply_text("🔄 Testing connection to ADM lottery website...")
        
        if not self.scraper:
            await update.message.reply_text("❌ Lottery scraper not available")
            return
        
        try:
            # Test if we can fetch the page
            html_content = self.scraper.fetch_page()
            if html_content:
                await update.message.reply_text("✅ Successfully connected to lottery website!")
            else:
                await update.message.reply_text("❌ Failed to connect to lottery website")
        except Exception as e:
            logger.error(f"Test command error: {e}")
            await update.message.reply_text(f"❌ Connection test failed: {str(e)}")
    
    async def lotto_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /lotto command to fetch latest lottery results."""
        await update.message.reply_text("🎲 Fetching latest lottery results...")
        
        if not self.scraper:
            await update.message.reply_text("❌ Lottery scraper not available")
            return
        
        try:
            results = self.scraper.get_latest_results()
            if results and scraper_available:
                formatted_message = format_lottery_results(results)
                await update.message.reply_text(formatted_message)
            else:
                await update.message.reply_text("❌ No lottery results found. Please try again later.")
        except Exception as e:
            logger.error(f"Error fetching lottery results: {e}")
            await update.message.reply_text(f"❌ Error fetching results: {str(e)}")
    
    def run(self):
        """Start the bot."""
        if not telegram_available:
            logger.error("Cannot start bot - telegram libraries not available")
            return
            
        if not self.application:
            logger.error("Cannot start bot - application not initialized")
            return
            
        logger.info("Starting Italian Lottery Bot...")
        logger.info(f"Bot token configured: {bool(self.bot_token)}")
        logger.info(f"Scraper available: {scraper_available}")
        
        # Run the bot
        self.application.run_polling()


def main():
    """Main function to start the bot."""
    logger.info("Initializing Working Lottery Bot...")
    
    if not telegram_available:
        logger.error("Telegram libraries not available. Cannot start bot.")
        return
    
    bot = WorkingLotteryBot()
    bot.run()


if __name__ == "__main__":
    main()