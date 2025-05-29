import os
import logging

# Bot configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN",
                      "8131597720:AAEd1vGmLPYtCcjydwQgTX4OA6_diOzcGJ4")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

# Scraping configuration
LOTTO_BASE_URL = "https://www.adm.gov.it/portale/monopoli/giochi/gioco-del-lotto/lotto_g/lotto_estr"
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 5

# User agent to appear as a regular browser
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('bot.log'),
              logging.StreamHandler()])

logger = logging.getLogger(__name__)
