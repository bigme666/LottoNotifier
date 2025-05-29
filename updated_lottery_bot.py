#!/usr/bin/env python3
"""
Updated Telegram bot for Italian lottery results.
This version accepts prog and anno parameters from users.
"""

import asyncio
import logging
import os
import sys
import re
from typing import Dict, Any, List

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
    logger.info("Basic Telegram components imported successfully")
except ImportError as e:
    logger.error(f"Telegram import failed: {e}")
    telegram_available = False

# Import our lottery scraper
try:
    from scraper import LottoScraper
    from utils import format_lottery_results
    scraper_available = True
    logger.info("Lottery scraper imported successfully")
except ImportError as e:
    logger.error(f"Scraper import failed: {e}")
    scraper_available = False


class UpdatedLotteryBot:
    """Updated lottery bot that accepts prog and anno parameters."""
    
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.scraper = LottoScraper() if scraper_available else None
        
        if telegram_available:
            self.bot = Bot(token=self.bot_token)
        else:
            self.bot = None
            logger.error("Cannot create bot - telegram libraries not available")
    
    def parse_lottery_command(self, text: str) -> tuple:
        """
        Parse lottery command to extract prog and anno parameters.
        
        Args:
            text: Command text from user
            
        Returns:
            Tuple of (prog, anno) or (None, None) if invalid
        """
        # Look for patterns like "/lotto 84 2025" or "/latest prog=84 anno=2025"
        patterns = [
            r'/(?:lotto|latest)\s+(\d+)\s+(\d+)',  # "/lotto 84 2025"
            r'/(?:lotto|latest)\s+prog[=:]\s*(\d+)\s+anno[=:]\s*(\d+)',  # "/lotto prog=84 anno=2025"
            r'/(?:lotto|latest)\s+anno[=:]\s*(\d+)\s+prog[=:]\s*(\d+)',  # "/lotto anno=2025 prog=84"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if 'anno.*prog' in pattern:
                    # Anno comes first in this pattern
                    return int(match.group(2)), int(match.group(1))
                else:
                    # Prog comes first
                    return int(match.group(1)), int(match.group(2))
        
        return None, None
    
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
                await self.send_lottery_results(chat_id, text)
            elif text.startswith('/test'):
                await self.send_test_message(chat_id, text)
            else:
                await self.send_unknown_command(chat_id)
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def send_start_message(self, chat_id):
        """Send welcome message."""
        welcome_message = """
🎰 Welcome to the Italian Lottery Results Bot!

This bot fetches lottery results from the official ADM website using specific drawing parameters.

Available commands:
/start - Show this welcome message
/help - Show detailed help information
/lotto <prog> <anno> - Get lottery results for specific drawing
/latest <prog> <anno> - Same as /lotto
/test <prog> <anno> - Test connection with specific parameters

Example usage:
/lotto 84 2025
/latest prog=84 anno=2025
/test 84 2025

The bot fetches data from: https://www.adm.gov.it/portale/monopoli/giochi/gioco-del-lotto/lotto_g/lotto_estr
        """
        await self.bot.send_message(chat_id=chat_id, text=welcome_message)
    
    async def send_help_message(self, chat_id):
        """Send help message."""
        help_message = """
🎰 Italian Lottery Bot Help

Commands and Usage:

• /start - Welcome message and overview
• /help - This help message  
• /lotto <prog> <anno> - Fetch lottery results
• /latest <prog> <anno> - Same as /lotto
• /test <prog> <anno> - Test website connection

Command formats:
1. /lotto 84 2025
2. /lotto prog=84 anno=2025
3. /latest 84 2025
4. /test prog=84 anno=2025

Parameters:
• prog: Drawing/program number (e.g., 84)
• anno: Year (e.g., 2025)

The bot scrapes official lottery results from the ADM website and provides you with drawing results for the specified program and year.

Results include numbers drawn for major Italian cities like Roma, Milano, Napoli, and others.
        """
        await self.bot.send_message(chat_id=chat_id, text=help_message)
    
    async def send_test_message(self, chat_id, text):
        """Test connection to the lottery website."""
        prog, anno = self.parse_lottery_command(text)
        
        if prog is None or anno is None:
            await self.bot.send_message(
                chat_id=chat_id, 
                text="❌ Invalid format. Use: /test <prog> <anno>\nExample: /test 84 2025"
            )
            return
        
        await self.bot.send_message(
            chat_id=chat_id, 
            text=f"🔄 Testing connection to ADM lottery website for prog={prog}, anno={anno}..."
        )
        
        if not self.scraper:
            await self.bot.send_message(chat_id=chat_id, text="❌ Lottery scraper not available")
            return
        
        try:
            # Test if we can fetch the page
            html_content = self.scraper.fetch_page(prog, anno)
            if html_content:
                await self.bot.send_message(
                    chat_id=chat_id, 
                    text=f"✅ Successfully connected to lottery website for prog={prog}, anno={anno}!"
                )
            else:
                await self.bot.send_message(
                    chat_id=chat_id, 
                    text=f"❌ Failed to connect to lottery website for prog={prog}, anno={anno}"
                )
        except Exception as e:
            logger.error(f"Test command error: {e}")
            await self.bot.send_message(
                chat_id=chat_id, 
                text=f"❌ Connection test failed: {str(e)}"
            )
    
    async def send_lottery_results(self, chat_id, text):
        """Send lottery results."""
        prog, anno = self.parse_lottery_command(text)
        
        if prog is None or anno is None:
            await self.bot.send_message(
                chat_id=chat_id, 
                text="❌ Invalid format. Use: /lotto <prog> <anno>\nExample: /lotto 84 2025"
            )
            return
        
        await self.bot.send_message(
            chat_id=chat_id, 
            text=f"🎲 Fetching lottery results for prog={prog}, anno={anno}..."
        )
        
        if not self.scraper:
            await self.bot.send_message(chat_id=chat_id, text="❌ Lottery scraper not available")
            return
        
        try:
            results = self.scraper.get_latest_results(prog, anno)
            if results and scraper_available:
                formatted_message = format_lottery_results(results)
                # Add the prog and anno info to the message
                final_message = f"🎰 Lottery Results (prog={prog}, anno={anno})\n\n{formatted_message}"
                await self.bot.send_message(chat_id=chat_id, text=final_message)
            else:
                await self.bot.send_message(
                    chat_id=chat_id, 
                    text=f"❌ No lottery results found for prog={prog}, anno={anno}. Please try again later."
                )
        except Exception as e:
            logger.error(f"Error fetching lottery results: {e}")
            await self.bot.send_message(
                chat_id=chat_id, 
                text=f"❌ Error fetching results for prog={prog}, anno={anno}: {str(e)}"
            )
    
    async def send_unknown_command(self, chat_id):
        """Send message for unknown commands."""
        message = """❓ Unknown command. 

Available commands:
/help - Show help information
/lotto <prog> <anno> - Get lottery results
/test <prog> <anno> - Test connection

Example: /lotto 84 2025"""
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
            
        logger.info("Starting Updated Italian Lottery Bot...")
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
    logger.info("Initializing Updated Lottery Bot...")
    
    if not telegram_available:
        logger.error("Telegram libraries not available. Cannot start bot.")
        return
    
    bot = UpdatedLotteryBot()
    asyncio.run(bot.run())


if __name__ == "__main__":
    main()