# 🚀 COMPLETE VPS DEPLOYMENT - COPY & PASTE COMMANDS

# 1. Install dependencies & Clone project
sudo apt update && sudo apt install python3 python3-pip python3-venv git -y
cd ~ && git clone https://github.com/mumirubro/dhsd.git toji-chk-bot
cd toji-chk-bot

# 2. Setup Virtual Environment (INSIDE project folder)
python3 -m venv venv
source venv/bin/activate
pip install python-telegram-bot requests python-dotenv

# 3. Configure Bot Credentials
echo "BOT_TOKEN=8574968899:AAFjYLts8tJ224qgkqTb-_shWZ42Qa7sVZY" > .env
echo "ADMIN_USERNAME=mumiru_01" >> .env

# 4. Create 24/7 System Service
sudo tee /etc/systemd/system/toji-bot.service > /dev/null <<EOF
[Unit]
Description=TOJI CHK Telegram Bot
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$(pwd)
EnvironmentFile=$(pwd)/.env
ExecStart=$(pwd)/venv/bin/python $(pwd)/main.py
Restart=always
RestartSec=10
EOF

# 5. Start Bot Service
sudo systemctl daemon-reload
sudo systemctl enable toji-bot
sudo systemctl start toji-bot

# 6. Verify Bot is Running
sudo systemctl status toji-bot
