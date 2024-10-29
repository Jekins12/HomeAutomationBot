# Use an official Python image for ARM architecture (suitable for Raspberry Pi)
FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /usr/src/app

# Install necessary system dependencies, including ping (iputils-ping)
RUN apt-get update && \
    apt-get install -y iputils-ping && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install Python dependencies
COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory into the container
COPY . /usr/src/app/

# Expose port (if needed for future use)
EXPOSE 8080

# Set the command to run your bot
CMD ["python", "bot.py"]
