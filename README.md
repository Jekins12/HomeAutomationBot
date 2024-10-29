# Telegram Bot as Docker container (Raspberry Pi)


## Prerequisites

1. Docker: Ensure Docker is installed on your Raspberry Pi.
2. Raspberry Pi: A working Raspberry Pi with an OS installed (Raspbian or Raspberry Pi OS recommended).
3. Telegram Bot Token: Get your bot token from BotFather at https://core.telegram.org/bots#botfather.

## Installation

### 1. Clone the repository

First, clone this repository to your Raspberry Pi

### 2. Configuration

Make sure to change config_template.py to config.py and edit it

### 3. Build the Docker Image

Navigate to the project directory and build the Docker image:
`docker build -t telegram_bot .`
This will create a Docker image named `telegram_bot`.

### 4. Run the Docker Container

Run the Docker container using the following command:
docker run -d --cap-add=NET_RAW --network host --name telegram_bot telegram_bot
- `-d`: Runs the container in detached mode.
- `--cap-add=NET_RAW`: Grants the necessary network capability for the bot to operate.
- `--network host`: Allows the bot to use the host network, which can be necessary for specific network configurations.
- `--name telegram_bot`: Assigns the container a name for easier management.
