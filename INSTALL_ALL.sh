# 🚀 INSTALLING ALL BOT DEPENDENCIES AT ONCE

# 1. Enter project folder and activate venv
cd ~/toji-chk-bot
source venv/bin/activate

# 2. Install EVERYTHING needed to stop the errors
echo "📥 Installing all required libraries..."
pip install \
  python-telegram-bot \
  requests \
  python-dotenv \
  aiohttp \
  fake-useragent \
  beautifulsoup4 \
  httpx

# 3. Restart the bot service
echo "🔄 Restarting bot..."
sudo systemctl restart toji-bot

# 4. Check logs
echo "📊 Checking logs..."
sudo journalctl -u toji-bot -f
