#!/bin/bash
# TOJI CHK BOT - UPDATE SCRIPT
# This script updates the bot with the latest fixes for:
# 1. Shopify Dead Site Banning
# 2. /groups Command Markdown Fix

echo "🚀 Updating TOJI CHK BOT..."

# 1. Navigate to bot directory
cd ~/toji-chk-bot || exit

# 2. Pull latest changes from GitHub (if applicable)
# git pull origin main

# 3. Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# 4. Install dependencies in venv
echo "📥 Installing dependencies..."
./venv/bin/pip install -r requirements.txt

# 5. Fix Telegram Library Conflict (Ensure python-telegram-bot is used)
echo "🛠️ Fixing Telegram library conflict..."
./venv/bin/pip uninstall -y telegram
./venv/bin/pip install python-telegram-bot --upgrade

# 6. Restart the systemd service
echo "🔄 Restarting bot service..."
sudo systemctl restart toji-bot

# 7. Verify status
echo "📊 Bot Status:"
sudo systemctl status toji-bot --no-pager

echo "✅ Update complete! Check logs with: sudo journalctl -u toji-bot -f"
