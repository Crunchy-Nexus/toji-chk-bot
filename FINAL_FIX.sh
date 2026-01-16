# 🚀 FINAL FIX - INSTALLING ALL LIBRARIES FROM REQUIREMENTS.TXT

# 1. Enter project folder and activate venv
cd ~/toji-chk-bot
source venv/bin/activate

# 2. Update pip and install everything from requirements.txt
echo "📥 Installing all dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# 3. Double check critical libraries are installed
pip install fake-useragent aiohttp beautifulsoup4 httpx python-telegram-bot

# 4. Restart the bot service
echo "🔄 Restarting bot..."
sudo systemctl restart toji-bot

# 5. Check logs
echo "📊 Checking logs..."
sudo journalctl -u toji-bot -f
