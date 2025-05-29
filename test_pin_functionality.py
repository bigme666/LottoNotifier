#!/usr/bin/env python3
"""
Test per la funzionalità di gestione dei messaggi fissati nel canale
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

class PinTester:
    def __init__(self):
        self.token = BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.channel_id = "@estrazionilotto"
    
    async def send_message(self, text):
        """Invia un messaggio al canale."""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.channel_id,
            "text": text,
            "parse_mode": "HTML"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            result = response.json()
            return result
    
    async def unpin_chat_message(self):
        """Rimuove il messaggio fissato dal canale."""
        url = f"{self.base_url}/unpinChatMessage"
        payload = {
            "chat_id": self.channel_id
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            return response.json()
    
    async def pin_chat_message(self, message_id):
        """Fissa un messaggio nel canale."""
        url = f"{self.base_url}/pinChatMessage"
        payload = {
            "chat_id": self.channel_id,
            "message_id": message_id,
            "disable_notification": True
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            return response.json()
    
    async def test_pin_unpin_cycle(self):
        """Testa il ciclo completo: rimuovi pin precedente → invia messaggio → fissa nuovo messaggio."""
        logger.info("🧪 Test del ciclo completo di gestione messaggi fissati")
        
        try:
            # Step 1: Rimuovi messaggio fissato precedente
            logger.info("Step 1: Rimozione messaggio fissato precedente...")
            unpin_response = await self.unpin_chat_message()
            
            if unpin_response.get('ok'):
                logger.info("✓ Messaggio fissato precedente rimosso")
            else:
                logger.info("ℹ️ Nessun messaggio fissato da rimuovere")
            
            # Step 2: Invia nuovo messaggio
            timestamp = datetime.now().strftime("%d/%m/%Y alle %H:%M:%S")
            message = f"""📊 <b>ESTRAZIONE DEL LOTTO</b>
📅 Test del {timestamp}

🎯 <b>BARI:</b> 11-22-33-44-55
🎯 <b>CAGLIARI:</b> 66-77-88-99-10
🎯 <b>FIRENZE:</b> 12-23-34-45-56
🎯 <b>GENOVA:</b> 67-78-89-90-01
🎯 <b>MILANO:</b> 13-24-35-46-57
🎯 <b>NAPOLI:</b> 68-79-80-91-02
🎯 <b>PALERMO:</b> 14-25-36-47-58
🎯 <b>ROMA:</b> 69-70-81-92-03
🎯 <b>TORINO:</b> 15-26-37-48-59
🎯 <b>VENEZIA:</b> 60-71-82-93-04
🎯 <b>NAZIONALE:</b> 16-27-38-49-50

<i>⚡ Messaggio automatico dal Bot Lotto</i>"""
            
            logger.info("Step 2: Invio nuovo messaggio...")
            send_response = await self.send_message(message)
            
            if send_response.get('ok'):
                message_id = send_response.get('result', {}).get('message_id')
                logger.info(f"✓ Messaggio inviato (ID: {message_id})")
                
                # Step 3: Fissa il nuovo messaggio
                if message_id:
                    logger.info("Step 3: Fissaggio nuovo messaggio...")
                    pin_response = await self.pin_chat_message(message_id)
                    
                    if pin_response.get('ok'):
                        logger.info("✓ Messaggio fissato con successo!")
                        return True
                    else:
                        logger.error(f"✗ Errore nel fissaggio: {pin_response.get('description', 'Errore sconosciuto')}")
                        return False
                else:
                    logger.error("✗ Impossibile ottenere l'ID del messaggio")
                    return False
            else:
                logger.error(f"✗ Errore nell'invio: {send_response.get('description', 'Errore sconosciuto')}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Eccezione durante il test: {e}")
            return False

async def main():
    """Funzione principale."""
    tester = PinTester()
    
    logger.info("🚀 Avvio test funzionalità messaggi fissati")
    success = await tester.test_pin_unpin_cycle()
    
    logger.info("\n" + "="*60)
    if success:
        logger.info("🎉 Test completato con successo!")
        logger.info("La funzionalità di gestione messaggi fissati è operativa.")
    else:
        logger.info("⚠️ Test fallito. Verifica i permessi del bot nel canale.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())