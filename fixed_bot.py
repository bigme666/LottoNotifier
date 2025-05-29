#!/usr/bin/env python3
"""
Fixed RAI Televideo Telegram bot for Italian lottery results.
Uses direct API calls with proper error handling.
"""

import asyncio
import httpx
import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our modules
try:
    from rai_scraper import RaiLottoScraper
    from utils import format_lottery_results
    scraper_available = True
    logger.info("RAI lottery scraper imported successfully")
except ImportError as e:
    logger.error(f"Failed to import scraper: {e}")
    scraper_available = False

# Bot token
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
if not BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN environment variable is required")
    sys.exit(1)

class Bot:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
    
    async def send_message(self, chat_id, text):
        """Send message via Telegram API."""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            return response.json()
    
    async def get_updates(self, offset=None):
        """Get updates from Telegram."""
        url = f"{self.base_url}/getUpdates"
        params = {}
        if offset:
            params["offset"] = offset
        params["timeout"] = 10  # Shorter timeout
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            return response.json()

class FixedLotteryBot:
    """Fixed lottery bot with proper error handling."""
    
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.bot = Bot(self.bot_token)
        self.scraper = RaiLottoScraper() if scraper_available else None
        self.processed_messages = set()  # Track processed message IDs
        logger.info("Fixed lottery bot initialized")
    
    async def handle_message(self, update_data: Dict[str, Any]):
        """Handle incoming messages."""
        try:
            if 'message' not in update_data:
                return
            
            message = update_data['message']
            if 'text' not in message:
                return
            
            # Check for duplicate messages
            message_id = message.get('message_id')
            if message_id in self.processed_messages:
                logger.info(f"Skipping duplicate message {message_id}")
                return
            
            # Add to processed messages (keep last 100 to prevent memory issues)
            self.processed_messages.add(message_id)
            if len(self.processed_messages) > 100:
                self.processed_messages = set(list(self.processed_messages)[-50:])
                
            text = message['text'].strip()
            chat_id = message['chat']['id']
            
            logger.info(f"Processing message: {text} from chat {chat_id} (ID: {message_id})")
            
            if text == '/start':
                await self.send_start_message(chat_id)
            elif text in ['/help']:
                await self.send_help_message(chat_id)
            elif text in ['/ultima', '/lotto']:
                await self.send_lottery_results(chat_id)
            else:
                await self.send_unknown_command(chat_id)
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def send_start_message(self, chat_id):
        """Send welcome message."""
        message = """Benvenuto nel Bot delle Estrazioni del Lotto!

Usa /ultima per ottenere gli ultimi risultati del lotto italiano.

Comando disponibile:
/ultima - Mostra i risultati più recenti"""
        
        await self.bot.send_message(chat_id=chat_id, text=message)
    
    async def send_help_message(self, chat_id):
        """Send help message."""
        message = """Bot per le Estrazioni del Lotto Italiano

Comandi disponibili:
/ultima - Ottieni gli ultimi risultati del lotto

I risultati vengono recuperati dal sito ufficiale RAI Televideo."""
        
        await self.bot.send_message(chat_id=chat_id, text=message)
    
    async def send_lottery_results(self, chat_id):
        """Send lottery results."""
        try:
            if not self.scraper:
                await self.bot.send_message(
                    chat_id=chat_id, 
                    text="Servizio temporaneamente non disponibile."
                )
                return
            
            # Get results
            results = self.scraper.get_latest_results()
            
            if results and 'extraction_date' in results:
                formatted_message = format_lottery_results(results)
                await self.bot.send_message(chat_id=chat_id, text=formatted_message)
            else:
                await self.bot.send_message(
                    chat_id=chat_id, 
                    text="Non sono riuscito a recuperare i risultati. Riprova più tardi."
                )
                
        except Exception as e:
            logger.error(f"Error getting lottery results: {e}")
            await self.bot.send_message(
                chat_id=chat_id, 
                text="Errore nel recupero dei risultati. Riprova più tardi."
            )
    
    async def send_unknown_command(self, chat_id):
        """Send message for unknown commands."""
        message = """Comando sconosciuto.

Comandi disponibili:
/help - Mostra informazioni di aiuto
/ultima - Ottieni gli ultimi risultati del lotto"""
        
        await self.bot.send_message(chat_id=chat_id, text=message)
    
    async def run(self):
        """Main bot loop with proper error handling."""
        logger.info("Starting fixed lottery bot...")
        
        offset = None
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while True:
            try:
                # Get updates
                response = await self.bot.get_updates(offset)
                
                # Reset error counter on successful response
                consecutive_errors = 0
                
                # Process updates
                if response.get('ok') and response.get('result'):
                    updates = response['result']
                    
                    for update in updates:
                        await self.handle_message(update)
                        offset = update['update_id'] + 1
                
                # Short delay
                await asyncio.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                break
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Error in bot loop ({consecutive_errors}/{max_consecutive_errors}): {e}")
                
                if consecutive_errors >= max_consecutive_errors:
                    logger.error("Too many consecutive errors. Stopping bot.")
                    break
                
                await asyncio.sleep(5)

def main():
    """Main function to start the bot."""
    if not scraper_available:
        logger.error("Scraper not available. Cannot start bot.")
        return
    
    bot = FixedLotteryBot()
    asyncio.run(bot.run())

if __name__ == "__main__":
    main()