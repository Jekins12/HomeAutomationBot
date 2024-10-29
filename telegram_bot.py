# telegram_bot.py

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CallbackContext

import automation_handler
import endpoint_handler
from config import CHAT_ID

class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.chat_id = CHAT_ID

    async def send_message(self, chat_id, text, context: CallbackContext, reply_markup=None):
        """Send a message to the chat."""
        await context.bot.send_message(chat_id, text, reply_markup=reply_markup)


    async def handle_message(self, update: Update, context: CallbackContext):
        """Handles text messages sent to the bot."""
        message = update.message
        chat_id = message.chat_id
        command = message.text.strip()  # Clean up command input

        # Direct commands to appropriate handlers
        if command == '/help':
            await self.show_help(chat_id, context)

        elif "Air quality alert" in command:
            await endpoint_handler.handle(update, chat_id, self, context)

        elif command == '/scan':
            await context.bot_data['network_scanner'].scan_network(chat_id, context)
        else:
            await self.send_message(chat_id, "Unknown command. Type /help for available commands.", context)

    async def process_command(self, update: Update, context: CallbackContext):
        """Processes commands from users."""
        message = update.message
        chat_id = message.chat_id
        command = message.text.strip()  # Clean up command input

        if command == '/help':
            await self.show_help(chat_id, context)
        elif command == '/scan':
            await context.bot_data['network_scanner'].scan_network(chat_id, context)
        else:
            await self.send_message(chat_id, "Unknown command. Type /help for available commands.", context)

    async def show_help(self, chat_id, context: CallbackContext):
        """Shows the help menu with available commands."""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='💨 Air Data', callback_data='scd30'),
             InlineKeyboardButton(text='⚡ Energy Data', callback_data='pzem004')],
            [InlineKeyboardButton(text='🔎 Scan network', callback_data='scan')],
            [InlineKeyboardButton(text='💨 24h Air Report', callback_data='report_air_24h'),
             InlineKeyboardButton(text='⚡ 24h Energy Report', callback_data='report_energy_24h')],
            [InlineKeyboardButton(text='🔄 Switch ventilation mode', callback_data='switch_mode')],
            [InlineKeyboardButton(text='🙈 Hide', callback_data='hide')]
        ])
        await self.send_message(chat_id, "🕹️ Control:", context, reply_markup=keyboard)

    async def show_main_menu(self, chat_id, context: CallbackContext):
        """Displays the main menu with options."""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='🕹️ Control', callback_data='menu'),
             InlineKeyboardButton(text='🙈 Hide', callback_data='hide')]
        ])
        await self.send_message(chat_id, "📃 Main menu:", context, reply_markup=keyboard)

    async def on_callback_query(self, update: Update, context: CallbackContext):
        """Handles button presses from the inline keyboard."""
        query = update.callback_query
        query_data = query.data
        chat_id = query.message.chat.id
        message_id = query.message.message_id

        # Accessing the data from bot_data
        influxdb_handler = context.bot_data['influxdb_handler']
        network_scanner = context.bot_data['network_scanner']

        if query_data == 'menu':
            await self.show_help(chat_id, context)
        elif query_data == 'hide':
            await context.bot.delete_message(chat_id, message_id)
            await self.send_message(chat_id, "Menu hidden. Type /help to show it again.", context)
        elif query_data == 'scd30':
            await influxdb_handler.show_data(chat_id, "scd30", context)
            await self.show_main_menu(chat_id, context)
        elif query_data == 'pzem004':
            await influxdb_handler.show_data(chat_id, "pzem004", context)
            await self.show_main_menu(chat_id, context)
        elif query_data == 'scan':
            await network_scanner.scan_network(chat_id, context)
            await self.show_main_menu(chat_id, context)
        elif query_data == 'report_air_24h':
            await influxdb_handler.report(chat_id, "scd30", context)
            await self.show_main_menu(chat_id, context)
        elif query_data == 'report_energy_24h':
            await influxdb_handler.report(chat_id, "pzem004", context)
            await self.show_main_menu(chat_id, context)
        elif query_data.startswith("select_endpoint"):
            await endpoint_handler.handle(update, chat_id, self, context)
        elif query_data.startswith('switch_mode'):
            if(automation_handler.is_Auto):
                automation_handler.is_Auto = False
                await self.send_message(chat_id, "🔴 Ventilation mode has been changed to MANUAL", context)
                await self.show_main_menu(chat_id, context)
            else:
                automation_handler.is_Auto = True
                await self.send_message(chat_id, "🟢 Ventilation mode has been changed to AUTO", context)
                await self.show_main_menu(chat_id, context)

