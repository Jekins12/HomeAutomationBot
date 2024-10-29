# network_scanner.py

import asyncio
import json
import subprocess
import platform
import aiohttp
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

class NetworkScanner:
    def __init__(self, base_ip, max_concurrent=50):
        self.base_ip = base_ip
        self.semaphore = asyncio.Semaphore(max_concurrent)  # Limit concurrent tasks

    async def scan_network(self, chat_id, context: ContextTypes.DEFAULT_TYPE):
        ip_range = range(1, 254)
        results = []

        # Use asyncio.gather with concurrency control
        tasks = [self.ping_ip(f"{self.base_ip}{ip}", results, chat_id, context) for ip in ip_range]
        await asyncio.gather(*tasks)

        # Send results
        if not results:
            for result in results:
                await context.bot.send_message(chat_id, result)
        else:
            await context.bot.send_message(chat_id, "No online hosts found.")

    async def ping_ip(self, ip_address, results, chat_id, context: ContextTypes.DEFAULT_TYPE):
        async with self.semaphore:
            is_windows = platform.system() == "Windows"
            command = ["ping", "-n", "1", "-w", "100", ip_address] if is_windows else ["ping", "-c", "1", "-W", "1", ip_address]

            try:
                # Run the ping command asynchronously
                process = await asyncio.create_subprocess_exec(
                    *command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                stdout, _ = await process.communicate()
                output = stdout.decode()

                if "Reply from" in output or "bytes from" in output:
                    await self.check_discover_endpoint(ip_address, results, chat_id, context)
            except Exception as e:
                print(f"Error pinging {ip_address}: {e}")

    async def check_discover_endpoint(self, ip_address, results, chat_id, context: ContextTypes.DEFAULT_TYPE):
        url = f"http://{ip_address}/discover"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=2) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            name = data.get("name", "Unknown")
                            ip = data.get("ip_address", ip_address)
                            endpoints = data.get("endpoints", [])

                            # Format result message and create buttons for endpoints
                            result_message = f"Name: {name}, IP Address: {ip}"
                            if endpoints:
                                await self.send_message_with_buttons(chat_id, context, result_message, endpoints, ip)
                            else:
                                await context.bot.send_message(chat_id, f"{result_message}, Endpoints: None")
                        except json.JSONDecodeError:
                            results.append(f"IP: {ip_address} returned non-JSON response")
            except aiohttp.ClientError as e:
                print(f"Error connecting to {ip_address}: {e}")

    async def send_message_with_buttons(self, chat_id, context: ContextTypes.DEFAULT_TYPE, message, endpoints, ip_address):
        """Send a message with buttons for each endpoint."""
        buttons = [InlineKeyboardButton(text=endpoint, callback_data=f"select_endpoint:{ip_address}:{endpoint}") for endpoint in endpoints]
        markup = InlineKeyboardMarkup(inline_keyboard=[buttons])
        await context.bot.send_message(chat_id, message, reply_markup=markup)

