#!/usr/bin/env python3
"""
Simple working Telegram bot for Italian lottery results.
Uses only the core telegram functionality that's available.
"""

import asyncio
import logging
import os
import sys
import json
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
    telegram_available = True
    logger.info("✓ Basic Telegram components imported successfully")
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


class SimpleLotteryBot:
    """A simple lottery bot using basic telegram functionality."""
    
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.scraper = LottoScraper() if scraper_available else None
        
        if telegram_available:
            self.bot = Bot(token=self.bot_token)
        else:
            self.bot = None
            logger.error("Cannot create bot - telegram libraries not available")
    
    async def handle_message(self, update_data: Dict[str, Any]):
        """Handle incoming messages."""
        if not self.bot:
            return
            
        try:
            # Extract message info
            message = update_data.get('message', {})
            chat_id = message.get('chat', {}).get('id')
            text = message.get('text', '').strip()
            
            if not chat_id or not text:
                return
            
            logger.info(f"Received command: {text} from chat {chat_id}")
            
            # Handle different commands
            if text.startswith('/start'):
                await self.send_start_message(chat_id)
            elif text.startswith('/help'):
                await self.send_help_message(chat_id)
            elif text.startswith('/lotto') or text.startswith('/latest'):
                await self.send_lottery_results(chat_id)
            elif text.startswith('/test'):
                await self.send_test_message(chat_id)
            else:
                await self.send_unknown_command(chat_id)
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def send_start_message(self, chat_id):
        """Send welcome message."""
        welcome_message = """
🎰 Welcome to the Italian Lottery Results Bot!

This bot provides you with the latest lottery results from the official ADM website.

Available commands:
/start - Show this welcome message
/help - Show help information
/lotto - Get latest lottery results
/latest - Get latest lottery results (same as /lotto)
/test - Test connection to lottery website

The bot fetches real-time data from the official Italian lottery website.
        """
        await self.bot.send_message(chat_id=chat_id, text=welcome_message)
    
    async def send_help_message(self, chat_id):
        """Send help message."""
        help_message = """
🎰 Italian Lottery Bot Help

Commands:
• /start - Welcome message and overview
• /help - This help message  
• /lotto - Fetch latest lottery results
• /latest - Same as /lotto
• /test - Test website connection

The bot scrapes official lottery results from the ADM website and provides you with the most recent drawing results.

Results include numbers drawn for major Italian cities like Roma, Milano, Napoli, and others.
        """
        await self.bot.send_message(chat_id=chat_id, text=help_message)
    
    async def send_test_message(self, chat_id):
        """Test connection to the lottery website."""
        await self.bot.send_message(chat_id=chat_id, text="🔄 Testing connection to ADM lottery website...")
        
        if not self.scraper:
            await self.bot.send_message(chat_id=chat_id, text="❌ Lottery scraper not available")
            return
        
        try:
            # Test if we can fetch the page
            html_content = self.scraper.fetch_page()
            if html_content:
                await self.bot.send_message(chat_id=chat_id, text="✅ Successfully connected to lottery website!")
            else:
                await self.bot.send_message(chat_id=chat_id, text="❌ Failed to connect to lottery website")
        except Exception as e:
            logger.error(f"Test command error: {e}")
            await self.bot.send_message(chat_id=chat_id, text=f"❌ Connection test failed: {str(e)}")
    
    async def send_lottery_results(self, chat_id):
        """Send lottery results."""
        await self.bot.send_message(chat_id=chat_id, text="🎲 Fetching latest lottery results...")
        
        if not self.scraper:
            await self.bot.send_message(chat_id=chat_id, text="❌ Lottery scraper not available")
            return
        
        try:
            results = self.scraper.get_latest_results()
            if results and scraper_available:
                formatted_message = format_lottery_results(results)
                await self.bot.send_message(chat_id=chat_id, text=formatted_message)
            else:
                await self.bot.send_message(chat_id=chat_id, text="❌ No lottery results found. Please try again later.")
        except Exception as e:
            logger.error(f"Error fetching lottery results: {e}")
            await self.bot.send_message(chat_id=chat_id, text=f"❌ Error fetching results: {str(e)}")
    
    async def send_unknown_command(self, chat_id):
        """Send message for unknown commands."""
        message = "❓ Unknown command. Use /help to see available commands."
        await self.bot.send_message(chat_id=chat_id, text=message)
    
    async def get_updates(self, offset=None):
        """Get updates from Telegram."""
        try:
            updates = await self.bot.get_updates(offset=offset, timeout=30)
            return updates
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return []
    
    async def run(self):
        """Main bot loop."""
        if not telegram_available or not self.bot:
            logger.error("Cannot start bot - telegram libraries not available")
            return
            
        logger.info("Starting Italian Lottery Bot...")
        logger.info(f"Bot token configured: {bool(self.bot_token)}")
        logger.info(f"Scraper available: {scraper_available}")
        
        offset = None
        
        while True:
            try:
                updates = await self.get_updates(offset)
                
                for update in updates:
                    # Process each update
                    await self.handle_message(update.to_dict())
                    offset = update.update_id + 1
                
                # Small delay to prevent excessive API calls
                await asyncio.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in bot loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying


def main():
    """Main function to start the bot."""
    logger.info("Initializing Simple Lottery Bot...")
    
    if not telegram_available:
        logger.error("Telegram libraries not available. Cannot start bot.")
        return
    
    bot = SimpleLotteryBot()
    asyncio.run(bot.run())


if __name__ == "__main__":
    main()