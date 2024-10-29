#endpoint_handler.py

import aiohttp
import asyncio
from telegram import Update
from telegram.ext import ContextTypes

import automation_handler


async def handle(update: Update, chat_id, bot, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query_data = query.data

    if query_data.startswith("select_endpoint"):
        _, ip_address, endpoint = query_data.split(":")
        await send_endpoint_request(chat_id, ip_address, endpoint, bot, context)


async def send_endpoint_request(chat_id, ip_address, endpoint, bot, context: ContextTypes.DEFAULT_TYPE):
    """Send a request to the selected endpoint and return the result."""
    url = f"http://{ip_address}{endpoint}"

    if (endpoint == "/open" or endpoint == "/close") and automation_handler.is_Auto:
        if endpoint == "/open":
            automation_handler.is_Open = True
        elif endpoint == "/close":
            automation_handler.is_Open = False
        automation_handler.is_Auto = False
        await bot.send_message(chat_id, "🔴 Ventilation mode has been changed to MANUAL", context)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    text = await response.text()
                    await bot.send_message(chat_id, f"❗ {text} ❗", context)
                else:
                    await bot.send_message(chat_id, f"❗ Error {response.status} from {endpoint} at {ip_address} ❗",
                                           context)
    except asyncio.TimeoutError:
        await bot.send_message(chat_id, f"❗ Request to {endpoint} at {ip_address} timed out. Please try again later. ❗",
                               context)
    except aiohttp.ClientError as e:
        await bot.send_message(chat_id, f"❗ Failed to reach {endpoint} at {ip_address}: {str(e)} ❗", context)
