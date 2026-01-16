# 🚀 FIXING ALL MISSING DEPENDENCIES

# 1. Enter project folder and activate venv
cd ~/toji-chk-bot
source venv/bin/activate

# 2. Install all known required libraries at once
echo "📥 Installing all dependencies..."
pip install aiohttp python-telegram-bot requests python-dotenv fake-useragent beautifulsoup4

# 3. Restart the bot service
echo "🔄 Restarting bot..."
sudo systemctl restart toji-bot

# 4. Check logs
echo "📊 Checking logs..."
sudo journalctl -u toji-bot -f
