#!/usr/bin/env python3
"""
RAI Televideo Telegram bot for Italian lottery results.
Uses RAI Televideo as the data source.
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
    telegram_available = True
    logger.info("Telegram components imported successfully")
except ImportError as e:
    logger.error(f"Telegram import failed: {e}")
    telegram_available = False

# Import our lottery scraper
try:
    from rai_scraper import RaiLottoScraper
    from utils import format_lottery_results
    scraper_available = True
    logger.info("RAI lottery scraper imported successfully")
except ImportError as e:
    logger.error(f"Scraper import failed: {e}")
    scraper_available = False


class RaiLotteryBot:
    """RAI Televideo lottery bot."""
    
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.scraper = RaiLottoScraper() if scraper_available else None
        
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
            elif text.startswith('/lotto') or text.startswith('/ultima'):
                await self.send_lottery_results(chat_id)
            # elif text.startswith('/test'):
            #     await self.send_test_message(chat_id)
            else:
                await self.send_unknown_command(chat_id)
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def send_start_message(self, chat_id):
        """Send welcome message."""
        welcome_message = """
Benvenuto nel Bot delle Estrazioni del Lotto!

Questo bot recupera gli ultimi risultati del lotto da RAI Televideo.

Comandi disponibili:
/start - Mostra questo messaggio di benvenuto
/help - Mostra informazioni di aiuto
/lotto - Ottieni gli ultimi risultati del lotto
/ultima - Ottieni gli ultimi risultati del lotto (stesso di /lotto)

Fonte dati: RAI Televideo (https://www.televideo.rai.it)
        """
        await self.bot.send_message(chat_id=chat_id, text=welcome_message)
    
    async def send_help_message(self, chat_id):
        """Send help message."""
        help_message = """
Aiuto Bot Lotto Italiano

Comandi:
• /start - Messaggio di benvenuto e panoramica
• /help - Questo messaggio di aiuto  
• /lotto - Recupera gli ultimi risultati del lotto
• /ultima - Stesso di /lotto

Il bot recupera i risultati ufficiali del lotto da RAI Televideo e ti fornisce i risultati dell'estrazione più recente.

I risultati includono i numeri estratti per le principali città italiane come Roma, Milano, Napoli, Bari, Cagliari, Firenze, Genova, Palermo, Torino, Venezia e altre.
        """
        await self.bot.send_message(chat_id=chat_id, text=help_message)
    
    async def send_test_message(self, chat_id):
        """Test connection to RAI Televideo."""
        await self.bot.send_message(chat_id=chat_id, text="Test connessione a RAI Televideo...")
        
        if not self.scraper:
            await self.bot.send_message(chat_id=chat_id, text="Scraper del lotto non disponibile")
            return
        
        try:
            # Test if we can fetch the page
            html_content = self.scraper.fetch_page()
            if html_content:
                await self.bot.send_message(chat_id=chat_id, text="Connessione riuscita a RAI Televideo!")
            else:
                await self.bot.send_message(chat_id=chat_id, text="Connessione fallita a RAI Televideo")
        except Exception as e:
            logger.error(f"Test command error: {e}")
            await self.bot.send_message(chat_id=chat_id, text=f"Test di connessione fallito: {str(e)}")
    
    async def send_lottery_results(self, chat_id):
        """Send lottery results."""
        await self.bot.send_message(chat_id=chat_id, text="Recupero gli ultimi risultati del lotto da RAI Televideo...")
        
        if not self.scraper:
            await self.bot.send_message(chat_id=chat_id, text="Scraper del lotto non disponibile")
            return
        
        try:
            results = self.scraper.get_latest_results()
            if results and results.get('cities'):
                formatted_message = format_lottery_results(results)
                await self.bot.send_message(chat_id=chat_id, text=formatted_message)
            else:
                await self.bot.send_message(chat_id=chat_id, text="Nessun risultato del lotto trovato. Riprova più tardi.")
        except Exception as e:
            logger.error(f"Error fetching lottery results: {e}")
            await self.bot.send_message(chat_id=chat_id, text=f"Errore nel recupero dei risultati: {str(e)}")
    
    async def send_unknown_command(self, chat_id):
        """Send message for unknown commands."""
        message = """Comando sconosciuto. 

Comandi disponibili:
/help - Mostra informazioni di aiuto
/lotto - Ottieni gli ultimi risultati del lotto
/ultima - Ottieni gli ultimi risultati del lotto"""
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
            
        logger.info("Starting RAI Televideo Lottery Bot...")
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
    logger.info("Initializing RAI Televideo Lottery Bot...")
    
    if not telegram_available:
        logger.error("Telegram libraries not available. Cannot start bot.")
        return
    
    bot = RaiLotteryBot()
    asyncio.run(bot.run())


if __name__ == "__main__":
    main()