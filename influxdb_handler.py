# influxdb_handler.py

from influxdb_client import InfluxDBClient
from config import INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG
from telegram.ext import ContextTypes
import itertools


class InfluxDBHandler:
    def __init__(self):
        self.client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

    async def show_data(self, chat_id: int, data_type: str, context: ContextTypes.DEFAULT_TYPE):
        # Query the database
        query_api = self.client.query_api()
        query = f'from(bucket: "{data_type}") |> range(start: -1h) |> last()'

        tables = query_api.query(query)
        self.check_air()
        if tables:
            for table in tables:
                for row in table.records:
                    # Use context.bot.send_message to send the message
                    await context.bot.send_message(chat_id, f"{row.get_value()}  {row.get_field()}")
        else:
            await context.bot.send_message(chat_id, "No data available.")

    def check_air(self):
        query_api = self.client.query_api()
        query = f'from(bucket: "scd30") |> range(start: -1h) |> last()'
        tables = query_api.query(query)

        if tables:
            for table in tables:
                for row in table.records:
                    if f"{row.get_field()}" == "air_quality":
                        return (f"{row.get_value()}")


    async def report(self, chat_id: int, data_type: str, context: ContextTypes.DEFAULT_TYPE):
        # Query the database
        query_api = self.client.query_api()

        # Queries to get max and min values
        max_query = f'from(bucket: "{data_type}") |> range(start: -24h) |> max()'
        min_query = f'from(bucket: "{data_type}") |> range(start: -24h) |> min()'
        median_query = f'from(bucket: "{data_type}") |> range(start: -24h) |> median()'

        # Execute the queries
        max_tables = query_api.query(max_query)
        min_tables = query_api.query(min_query)
        median_tables = query_api.query(median_query)


        # Combine max, min and median tables together
        if max_tables and min_tables and median_tables:
            # Use itertools.zip_longest to handle cases where max_tables and min_tables have unequal lengths
            for max_table, min_table, median_table in itertools.zip_longest(max_tables, min_tables, median_tables, fillvalue=None):
                message = ""  # Initialize an empty message string

                # Add Max Value details to the message
                if max_table:
                    for max_row in max_table.records:
                        message += f"⬆️ Max Value: {max_row.get_value()} {max_row.get_field()}\n"

                if median_table:
                    for median_row in median_table.records:
                        median_value = median_row.get_value()
                        median_value = str(round(median_value, 2))
                        message += f"➡️ Average Value: {median_value} {median_row.get_field()}\n"

                # Add Min Value details to the message
                if min_table:
                    for min_row in min_table.records:
                        message += f"⬇️ Min Value: {min_row.get_value()} {min_row.get_field()}\n"

                # Add empty lines to separate each block
                message += "\n\n"

                # Send the accumulated message
                await context.bot.send_message(chat_id, message)


