import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
try:
    from telegram.constants import ParseMode
except ImportError:
    # For older versions of python-telegram-bot
    from telegram import ParseMode
from scraper import LottoScraper
from utils import format_lottery_results, get_current_timestamp
from config import BOT_TOKEN

logger = logging.getLogger(__name__)

class LotteryBot:
    def __init__(self):
        self.scraper = LottoScraper()
        self.application = Application.builder().token(BOT_TOKEN).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up command handlers for the bot."""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("lotto", self.lotto_command))
        self.application.add_handler(CommandHandler("latest", self.latest_command))
        self.application.add_handler(CommandHandler("info", self.info_command))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command."""
        welcome_message = """
🎱 **Benvenuto nel Bot delle Estrazioni del Lotto!** 🎱

Questo bot ti permette di ricevere i risultati delle estrazioni del Lotto italiano direttamente da ADM (Agenzia delle Dogane e dei Monopoli).

**Comandi disponibili:**
/lotto - Ottieni gli ultimi risultati del Lotto
/latest - Alias per /lotto
/info - Informazioni sul bot
/help - Mostra questo messaggio di aiuto

📊 I dati sono prelevati direttamente dal sito ufficiale ADM.
        """
        
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN
        )
        
        logger.info(f"User {update.effective_user.id} started the bot")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /help command."""
        help_message = """
🆘 **Aiuto - Comandi del Bot** 🆘

**Comandi principali:**
• /lotto - Recupera e mostra gli ultimi risultati delle estrazioni del Lotto
• /latest - Stesso comando di /lotto
• /info - Mostra informazioni dettagliate sul bot
• /help - Mostra questo messaggio di aiuto

**Come funziona:**
1. Il bot recupera i dati dal sito ufficiale ADM
2. Analizza i risultati delle estrazioni più recenti
3. Ti mostra i numeri estratti per ogni città

**Nota:** I risultati sono prelevati in tempo reale dal sito ufficiale.

📞 **Supporto:** Se hai problemi, riprova più tardi o contatta l'amministratore.
        """
        
        await update.message.reply_text(
            help_message,
            parse_mode=ParseMode.MARKDOWN
        )
        
        logger.info(f"User {update.effective_user.id} requested help")
    
    async def lotto_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /lotto command to fetch latest lottery results."""
        user_id = update.effective_user.id
        logger.info(f"User {user_id} requested lottery results")
        
        # Send "typing" action to show bot is working
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        
        try:
            # Fetch latest results
            results = self.scraper.get_latest_results()
            
            if results:
                # Format and send results
                formatted_message = format_lottery_results(results)
                await update.message.reply_text(
                    formatted_message,
                    parse_mode=ParseMode.MARKDOWN
                )
                logger.info(f"Successfully sent lottery results to user {user_id}")
            else:
                # Send error message if no results
                error_message = """
❌ **Errore nel recupero dei dati**

Non sono riuscito a recuperare i risultati delle estrazioni al momento.

**Possibili cause:**
• Il sito ADM potrebbe essere temporaneamente non disponibile
• Potrebbe non esserci ancora una nuova estrazione
• Problemi di connessione

🔄 **Riprova tra qualche minuto**
                """
                
                await update.message.reply_text(
                    error_message,
                    parse_mode=ParseMode.MARKDOWN
                )
                logger.warning(f"Failed to get lottery results for user {user_id}")
                
        except Exception as e:
            logger.error(f"Error processing lottery command for user {user_id}: {e}")
            
            error_message = """
❌ **Errore del Sistema**

Si è verificato un errore durante il recupero dei dati.

🔄 **Per favore riprova tra qualche minuto**

Se il problema persiste, il servizio potrebbe essere temporaneamente non disponibile.
            """
            
            await update.message.reply_text(
                error_message,
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def latest_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /latest command (alias for /lotto)."""
        await self.lotto_command(update, context)
    
    async def info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /info command."""
        info_message = f"""
ℹ️ **Informazioni sul Bot** ℹ️

**Nome:** Bot Estrazioni Lotto Italia
**Versione:** 1.0
**Fonte Dati:** ADM - Agenzia delle Dogane e dei Monopoli
**URL Fonte:** https://www.adm.gov.it

**Funzionalità:**
• Recupero automatico dei risultati del Lotto
• Dati ufficiali e aggiornati
• Formato di visualizzazione ottimizzato per Telegram

**Orario di aggiornamento:** {get_current_timestamp()}

**Disclaimer:**
Questo bot non è affiliato con ADM. I dati sono recuperati dal sito pubblico ufficiale per scopi informativi.

⚠️ **Attenzione:** Gioca responsabilmente!
        """
        
        await update.message.reply_text(
            info_message,
            parse_mode=ParseMode.MARKDOWN
        )
        
        logger.info(f"User {update.effective_user.id} requested bot info")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors in the bot."""
        logger.error(f"Exception while handling an update: {context.error}")
        
        if update and update.message:
            try:
                await update.message.reply_text(
                    "❌ Si è verificato un errore. Riprova più tardi.",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Failed to send error message: {e}")
    
    def run(self):
        """Start the bot."""
        logger.info("Starting Lottery Bot...")
        
        # Add error handler
        self.application.add_error_handler(self.error_handler)
        
        # Start the bot
        logger.info("Bot is now running and polling for updates...")
        self.application.run_polling(
            allowed_updates=['message'],
            drop_pending_updates=True
        )
