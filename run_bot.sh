#!/bin/bash

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if BOT_TOKEN is set
if [ -z "$BOT_TOKEN" ] || [ "$BOT_TOKEN" == "your_bot_token_here" ]; then
    echo "❌ Error: BOT_TOKEN is not set correctly in .env!"
    echo "Your .env should look like this:"
    echo "BOT_TOKEN=8574968899:AAELdyTwlFdeaIbhJ5dqL80WPwyfjFR5Rnc"
    echo ""
    echo "Please edit .env and fix it:"
    echo "  nano .env"
    exit 1
fi

echo "🤖 Starting TOJI CHK Bot..."
if [ -f "./venv/bin/python3" ]; then
    ./venv/bin/python3 main.py
else
    python3 main.py
fi
