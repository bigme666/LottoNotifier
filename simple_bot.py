#!/usr/bin/env python3
"""
Simplified Telegram bot for lottery results.
This version uses a simpler import structure to avoid conflicts.
"""

import os
import logging
import asyncio
from datetime import datetime

try:
    import telegram
    from telegram.ext import Application, CommandHandler, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError as e:
    print(f"Telegram import error: {e}")
    TELEGRAM_AVAILABLE = False

import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SimpleLotteryBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        
        if not TELEGRAM_AVAILABLE:
            raise ImportError("Telegram libraries not available")
            
        self.application = Application.builder().token(self.token).build()
        self._setup_handlers()

    def _setup_handlers(self):
        """Set up command handlers."""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("lotto", self.lotto_command))
        self.application.add_handler(CommandHandler("test", self.test_command))

    async def start_command(self, update, context):
        """Handle the /start command."""
        welcome_message = (
            "🎰 Benvenuto nel Bot delle Estrazioni del Lotto! 🎰\n\n"
            "Comandi disponibili:\n"
            "• /lotto - Ottieni i risultati dell'ultima estrazione\n"
            "• /test - Test connessione al sito ADM\n"
            "• /help - Mostra questo messaggio di aiuto\n\n"
            "Il bot raccoglie i dati dalle estrazioni ufficiali ADM."
        )
        await update.message.reply_text(welcome_message)

    async def help_command(self, update, context):
        """Handle the /help command."""
        help_message = (
            "📋 Comandi disponibili:\n\n"
            "• /start - Messaggio di benvenuto\n"
            "• /lotto - Risultati ultima estrazione\n"
            "• /test - Test connessione sito ADM\n"
            "• /help - Questo messaggio\n\n"
            "ℹ️ I dati sono recuperati dal sito ufficiale ADM."
        )
        await update.message.reply_text(help_message)

    async def test_command(self, update, context):
        """Test connection to ADM website."""
        await update.message.reply_text("🔍 Sto testando la connessione al sito ADM...")
        
        try:
            url = "https://www.adm.gov.it/portale/monopoli/giochi/gioco-del-lotto/lotto_g"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                message = f"✅ Connessione OK!\n📊 Status: {response.status_code}\n📄 Dimensione pagina: {len(response.text)} caratteri"
            else:
                message = f"⚠️ Problema di connessione\n📊 Status: {response.status_code}"
                
        except Exception as e:
            message = f"❌ Errore di connessione: {str(e)}"
            
        await update.message.reply_text(message)

    async def lotto_command(self, update, context):
        """Handle the /lotto command."""
        await update.message.reply_text("🎲 Sto recuperando i risultati dell'ultima estrazione...")
        
        try:
            # Simple scraping test
            url = "https://www.adm.gov.it/portale/monopoli/giochi/gioco-del-lotto/lotto_g"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for lottery cities
                cities = ['Bari', 'Cagliari', 'Firenze', 'Genova', 'Milano', 'Napoli', 'Palermo', 'Roma', 'Torino', 'Venezia']
                found_cities = [city for city in cities if city.lower() in response.text.lower()]
                
                if found_cities:
                    message = f"📍 Sito ADM raggiunto!\n🏛️ Città trovate: {', '.join(found_cities)}\n\n⚠️ I dati completi richiedono JavaScript.\nSto lavorando per migliorare l'estrazione..."
                else:
                    message = "📄 Pagina ADM caricata ma senza dati evidenti del lotto.\nLa pagina potrebbe caricare i dati dinamicamente."
            else:
                message = f"❌ Errore HTTP {response.status_code} dal sito ADM"
                
        except Exception as e:
            message = f"❌ Errore nel recupero dati: {str(e)}"
            logger.error(f"Error in lotto_command: {e}")
            
        await update.message.reply_text(message)

    def run(self):
        """Start the bot."""
        logger.info("Starting Simple Lottery Bot...")
        self.application.run_polling()

if __name__ == "__main__":
    if TELEGRAM_AVAILABLE:
        bot = SimpleLotteryBot()
        bot.run()
    else:
        print("❌ Telegram libraries not available. Please install python-telegram-bot.")