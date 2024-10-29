#automation_handler.py

import asyncio
import aiohttp

from influxdb_handler import InfluxDBHandler
from config import VENTILATION_URL, REFRESH_TIME

is_Auto = True
is_Open = True

class AutomationHandler:

    def __init__(self):
        self.influx_handler = InfluxDBHandler()

    async def check_air_periodically(self):

        global is_Open
        while True:
            if is_Auto:
                air_quality = self.influx_handler.check_air()
                if air_quality:
                    print(f"Air Quality: {air_quality}")
                    if int(air_quality) >= 3 and not is_Open:
                        is_Open = True
                        await self.send_request("/open")
                    elif int(air_quality) <= 2 and is_Open:
                        is_Open = False
                        await self.send_request("/close")

            await asyncio.sleep(REFRESH_TIME)


    async def send_request(self, endpoint):
        url = VENTILATION_URL+endpoint
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        print(f"Request to {url} succeeded.")

                    else:
                        print(f"Request to {url} failed with status {response.status}.")
            except Exception as e:
                print(f"Failed to send request to {url}: {e}")