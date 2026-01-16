# 🚀 FIXING TELEGRAM IMPORT ERROR

# 1. Enter project folder and activate venv
cd ~/toji-chk-bot
source venv/bin/activate

# 2. Uninstall conflicting packages and install correct one
echo "🧹 Cleaning up telegram packages..."
pip uninstall -y telegram python-telegram-bot
echo "📥 Installing correct python-telegram-bot..."
pip install python-telegram-bot --upgrade

# 3. Restart the bot service
echo "🔄 Restarting bot..."
sudo systemctl restart toji-bot

# 4. Check logs
echo "📊 Checking logs..."
sudo journalctl -u toji-bot -f
