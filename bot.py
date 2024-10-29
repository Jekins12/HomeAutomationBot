# bot.py
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram_bot import TelegramBot
from influxdb_handler import InfluxDBHandler
from network_scanner import NetworkScanner
from automation_handler import AutomationHandler  # Import AutomationHandler
from config import BOT_TOKEN, NETWORK, CHAT_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command that triggers the main menu."""
    bot = context.bot_data['telegram_bot']
    await bot.show_main_menu(update.effective_chat.id, context)

async def send_welcome_message(application):
    """Sends a welcome message to the configured chat ID when the bot starts."""
    bot = application.bot
    try:
        await bot.send_message(chat_id=CHAT_ID, text="Bot started! Type /start to begin.")
    except Exception as e:
        print(f"Failed to send welcome message: {e}")

async def start_air_quality_monitoring(application):
    """Starts the periodic air quality check task in the background."""
    automation_handler = application.bot_data['automation_handler']
    task = asyncio.create_task(automation_handler.check_air_periodically())
    application.bot_data['air_quality_task'] = task  # Store the task so we can cancel it later

async def shutdown(application):
    """Shutdown handler to cancel the background air quality monitoring task."""
    task = application.bot_data.get('air_quality_task')
    if task:
        task.cancel()  # Cancel the task
        try:
            await task  # Wait for task to be properly canceled
        except asyncio.CancelledError:
            print("Background task canceled.")

async def initialize_bot(application):
    """Initialize bot tasks and send welcome message."""
    # Send welcome message once on startup
    await send_welcome_message(application)
    # Start air quality monitoring task in the background
    await start_air_quality_monitoring(application)

def main():
    # Instantiate bot components
    bot = TelegramBot(BOT_TOKEN)
    influxdb_handler = InfluxDBHandler()
    network_scanner = NetworkScanner(NETWORK)
    automation_handler = AutomationHandler()  # Create an instance of AutomationHandler

    # Start the Telegram bot application
    application = ApplicationBuilder().token(BOT_TOKEN).post_init(initialize_bot).post_shutdown(shutdown).build()

    # Add command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', bot.process_command))
    application.add_handler(CommandHandler('scan', bot.process_command))

    # Add a generic message handler for other text commands
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))

    # Add handler for button callbacks
    application.add_handler(CallbackQueryHandler(bot.on_callback_query))

    # Set bot data
    application.bot_data['telegram_bot'] = bot
    application.bot_data['influxdb_handler'] = influxdb_handler
    application.bot_data['network_scanner'] = network_scanner
    application.bot_data['automation_handler'] = automation_handler

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
