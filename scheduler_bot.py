#!/usr/bin/env python3
"""
Scheduler Bot per le estrazioni del lotto.
Controlla automaticamente ogni sera alle 20:15, 20:20, 20:25 per nuove estrazioni.
"""

import os
import sys
import asyncio
import logging
import schedule
import time
from datetime import datetime, timedelta
from typing import Optional
import threading

# Aggiungi il percorso corrente per gli import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rai_scraper import RaiLottoScraper
from utils import format_lottery_results
# Configurazione per telegram
import httpx
import asyncio
import json

class Bot:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
    
    async def send_message(self, chat_id, text):
        """Invia un messaggio al canale o chat specificato."""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            return response.json()

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LotteryScheduler:
    """Scheduler per controlli automatici delle estrazioni del lotto."""
    
    def __init__(self):
        self.scraper = RaiLottoScraper()
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.channel_id = "estrazionilotto"  # ID del canale Telegram
        self.last_extraction_file = "last_extraction.txt"
        self.bot = None
        
        if self.bot_token:
            self.bot = Bot(token=self.bot_token)
            logger.info("Bot inizializzato per lo scheduler")
        else:
            logger.error("Token del bot non trovato")
    
    def read_last_extraction_date(self) -> Optional[str]:
        """Legge la data dell'ultima estrazione dal file."""
        try:
            if os.path.exists(self.last_extraction_file):
                with open(self.last_extraction_file, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            return None
        except Exception as e:
            logger.error(f"Errore leggendo il file dell'ultima estrazione: {e}")
            return None
    
    def write_last_extraction_date(self, date: str) -> None:
        """Scrive la data dell'ultima estrazione nel file."""
        try:
            with open(self.last_extraction_file, 'w', encoding='utf-8') as f:
                f.write(date)
            logger.info(f"Data ultima estrazione salvata: {date}")
        except Exception as e:
            logger.error(f"Errore scrivendo il file dell'ultima estrazione: {e}")
    
    async def check_for_new_extraction(self) -> bool:
        """Controlla se c'è una nuova estrazione disponibile."""
        try:
            logger.info("Controllo per nuove estrazioni...")
            results = self.scraper.get_latest_results()
            
            if not results or 'extraction_date' not in results:
                logger.warning("Nessun risultato o data estrazione trovata")
                return False
            
            current_date = results['extraction_date']
            last_date = self.read_last_extraction_date()
            
            logger.info(f"Data corrente: {current_date}, Ultima data: {last_date}")
            
            if last_date is None or current_date != last_date:
                # Nuova estrazione trovata
                logger.info(f"Nuova estrazione trovata: {current_date}")
                await self.send_results_to_channel(results)
                self.write_last_extraction_date(current_date)
                return True
            else:
                logger.info("Nessuna nuova estrazione trovata")
                return False
                
        except Exception as e:
            logger.error(f"Errore durante il controllo delle estrazioni: {e}")
            return False
    
    async def send_results_to_channel(self, results: dict) -> None:
        """Invia i risultati al canale Telegram."""
        try:
            if not self.bot:
                logger.error("Bot non disponibile per l'invio al canale")
                return
            
            formatted_message = format_lottery_results(results)
            message = f"🎰 NUOVA ESTRAZIONE DEL LOTTO!\n\n{formatted_message}"
            
            await self.bot.send_message(chat_id=self.channel_id, text=message)
            logger.info(f"Risultati inviati al canale {self.channel_id}")
            
        except Exception as e:
            logger.error(f"Errore inviando al canale: {e}")
    
    async def test_channel_send(self) -> None:
        """Testa l'invio di un messaggio al canale."""
        try:
            logger.info("=== TEST INVIO AL CANALE ===")
            
            # Ottieni i risultati correnti per il test
            results = self.scraper.get_latest_results()
            
            if results and 'extraction_date' in results:
                await self.send_results_to_channel(results)
                logger.info("Test completato con successo!")
            else:
                # Invia un messaggio di test semplice
                test_message = "🧪 Test di connessione al canale dal Bot delle Estrazioni del Lotto"
                await self.bot.send_message(chat_id=self.channel_id, text=test_message)
                logger.info("Messaggio di test inviato al canale!")
                
        except Exception as e:
            logger.error(f"Errore durante il test del canale: {e}")

    async def scheduled_check(self) -> None:
        """Esegue un controllo programmato."""
        logger.info("=== CONTROLLO PROGRAMMATO INIZIATO ===")
        
        # Tenta il controllo fino a 3 volte con intervalli di 5 minuti
        for attempt in range(1, 4):
            logger.info(f"Tentativo {attempt}/3")
            
            success = await self.check_for_new_extraction()
            if success:
                logger.info("Nuova estrazione trovata e inviata!")
                break
            
            if attempt < 3:
                logger.info("Attendo 5 minuti prima del prossimo tentativo...")
                await asyncio.sleep(300)  # 5 minuti
        
        logger.info("=== CONTROLLO PROGRAMMATO COMPLETATO ===")
    
    def run_scheduler(self):
        """Avvia lo scheduler."""
        logger.info("Avvio dello scheduler per le estrazioni del lotto")
        
        # Programma i controlli alle 20:15 ogni giorno
        schedule.every().day.at("20:15").do(self._schedule_async_job)
        
        logger.info("Scheduler configurato: controlli giornalieri alle 20:15")
        logger.info("Lo scheduler è ora in esecuzione...")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Controlla ogni minuto
    
    def _schedule_async_job(self):
        """Helper per eseguire job asincroni dallo scheduler."""
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.scheduled_check())
            loop.close()
        
        # Esegui in un thread separato per non bloccare lo scheduler
        thread = threading.Thread(target=run_async)
        thread.start()

def main():
    """Funzione principale."""
    logger.info("Avvio del Lottery Scheduler...")
    
    scheduler = LotteryScheduler()
    
    try:
        scheduler.run_scheduler()
    except KeyboardInterrupt:
        logger.info("Scheduler fermato dall'utente")
    except Exception as e:
        logger.error(f"Errore nello scheduler: {e}")

if __name__ == "__main__":
    main()