#!/usr/bin/env python3
"""
Test di invio al canale Telegram per verificare la connettività.
"""

import os
import sys
import asyncio
import logging
import httpx
from datetime import datetime

# Aggiungi il percorso corrente per gli import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rai_scraper import RaiLottoScraper
from utils import format_lottery_results

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ChannelTester:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.scraper = RaiLottoScraper()
        
        # Formato del canale da testare
        self.channel_id = "@estrazionilotto"
    
    async def send_message(self, chat_id, text):
        """Invia un messaggio al canale."""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            return response.json()
    
    async def test_channel_variants(self):
        """Testa diverse varianti del nome del canale."""
        logger.info("=== TEST VARIANTI DEL CANALE ===")
        
        timestamp = datetime.now().strftime("%H:%M:%S del %d/%m/%Y")
        message = f"🧪 Test di connessione\nBot delle Estrazioni del Lotto\nTest alle {timestamp}"
        
        for variant in self.channel_variants:
            logger.info(f"Testando canale: {variant}")
            try:
                result = await self.send_message(variant, message)
                
                if result.get('ok'):
                    logger.info(f"✅ Successo con: {variant}")
                    logger.info(f"ID messaggio: {result.get('result', {}).get('message_id', 'N/A')}")
                    return variant  # Ritorna la variante che funziona
                else:
                    logger.warning(f"❌ Fallito con {variant}: {result.get('description', 'Errore sconosciuto')}")
                    
            except Exception as e:
                logger.error(f"❌ Errore con {variant}: {e}")
            
            await asyncio.sleep(1)  # Pausa tra i tentativi
        
        logger.error("❌ Nessuna variante del canale ha funzionato")
        return None
    
    async def test_simple_message(self):
        """Test con messaggio semplice."""
        logger.info("=== TEST MESSAGGIO SEMPLICE ===")
        try:
            timestamp = datetime.now().strftime("%H:%M:%S del %d/%m/%Y")
            message = f"🧪 Test di connessione al canale\n\nBot delle Estrazioni del Lotto\nTest eseguito alle {timestamp}"
            
            result = await self.send_message(self.channel_id, message)
            
            if result.get('ok'):
                logger.info("✅ Messaggio di test inviato con successo!")
                logger.info(f"ID messaggio: {result.get('result', {}).get('message_id', 'N/A')}")
            else:
                logger.error(f"❌ Errore nell'invio: {result}")
                
        except Exception as e:
            logger.error(f"❌ Errore durante il test: {e}")
    
    async def test_lottery_results(self):
        """Test con risultati del lotto."""
        logger.info("=== TEST CON RISULTATI DEL LOTTO ===")
        try:
            results = self.scraper.get_latest_results()
            
            if results and 'extraction_date' in results:
                formatted_message = format_lottery_results(results)
                message = f"🎰 TEST - RISULTATI DEL LOTTO\n\n{formatted_message}\n\n📝 Questo è un messaggio di test"
                
                result = await self.send_message(self.channel_id, message)
                
                if result.get('ok'):
                    logger.info("✅ Risultati del lotto inviati con successo!")
                    logger.info(f"ID messaggio: {result.get('result', {}).get('message_id', 'N/A')}")
                else:
                    logger.error(f"❌ Errore nell'invio dei risultati: {result}")
            else:
                logger.warning("⚠️ Nessun risultato del lotto disponibile per il test")
                
        except Exception as e:
            logger.error(f"❌ Errore durante il test dei risultati: {e}")
    
    async def run_tests(self):
        """Esegue tutti i test."""
        logger.info("🚀 Avvio test di connessione al canale")
        
        if not self.bot_token:
            logger.error("❌ Token del bot non trovato")
            return
        
        logger.info(f"📱 Canale di destinazione: {self.channel_id}")
        
        # Test 1: Messaggio semplice
        await self.test_simple_message()
        
        # Pausa tra i test
        await asyncio.sleep(2)
        
        # Test 2: Risultati del lotto
        await self.test_lottery_results()
        
        logger.info("✨ Test completati")

async def main():
    """Funzione principale."""
    tester = ChannelTester()
    await tester.run_tests()

if __name__ == "__main__":
    asyncio.run(main())