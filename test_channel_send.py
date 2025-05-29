#!/usr/bin/env python3
"""
Test per l'invio di messaggi al canale @estrazionilotto
"""

import asyncio
import httpx
import os
import logging
from datetime import datetime

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Token del bot
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
if not BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN non trovato")
    exit(1)

class ChannelTester:
    def __init__(self):
        self.token = BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        # ID del canale @estrazionilotto
        self.channel_id = "@estrazionilotto"
    
    async def send_message(self, text):
        """Invia un messaggio al canale."""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.channel_id,
            "text": text,
            "parse_mode": "HTML"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)
                result = response.json()
                
                if result.get('ok'):
                    logger.info(f"✓ Messaggio inviato con successo al canale {self.channel_id}")
                    logger.info(f"Message ID: {result.get('result', {}).get('message_id')}")
                    return True
                else:
                    logger.error(f"✗ Errore nell'invio: {result.get('description', 'Errore sconosciuto')}")
                    return False
                    
        except Exception as e:
            logger.error(f"✗ Eccezione durante l'invio: {e}")
            return False
    
    async def test_simple_message(self):
        """Test con messaggio semplice."""
        logger.info("Test 1: Invio messaggio semplice")
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"🔔 Test del Bot Lotto - {timestamp}"
        
        return await self.send_message(message)
    
    async def test_lottery_format(self):
        """Test con formato dei risultati del lotto."""
        logger.info("Test 2: Invio messaggio formato lotto")
        
        timestamp = datetime.now().strftime("%d/%m/%Y alle %H:%M")
        message = f"""📊 <b>Test Risultati Lotto</b>
📅 Estrazione del {timestamp}

🎯 <b>BARI:</b> 01-23-45-67-89
🎯 <b>ROMA:</b> 12-34-56-78-90
🎯 <b>MILANO:</b> 11-22-33-44-55

<i>⚡ Aggiornamento automatico dal Bot Lotto</i>"""
        
        return await self.send_message(message)
    
    async def run_tests(self):
        """Esegue tutti i test."""
        logger.info("🚀 Avvio test invio messaggi al canale @estrazionilotto")
        
        # Test 1: Messaggio semplice
        success1 = await self.test_simple_message()
        await asyncio.sleep(2)
        
        # Test 2: Formato lotto
        success2 = await self.test_lottery_format()
        
        # Risultati
        logger.info("\n" + "="*50)
        logger.info("📋 RISULTATI TEST:")
        logger.info(f"Test messaggio semplice: {'✓ SUCCESSO' if success1 else '✗ FALLITO'}")
        logger.info(f"Test formato lotto: {'✓ SUCCESSO' if success2 else '✗ FALLITO'}")
        
        if success1 and success2:
            logger.info("🎉 Tutti i test sono passati! Il canale è configurato correttamente.")
        else:
            logger.info("⚠️  Alcuni test sono falliti. Controlla la configurazione del canale.")
        
        return success1 and success2

async def main():
    """Funzione principale."""
    tester = ChannelTester()
    await tester.run_tests()

if __name__ == "__main__":
    asyncio.run(main())