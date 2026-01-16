# 🚀 FIXING THE ERROR & RESTARTING BOT

# 1. Enter the project folder and activate venv
cd ~/toji-chk-bot
source venv/bin/activate

# 2. Install the missing 'aiohttp' module
pip install aiohttp

# 3. Fix the System Service (Adding the [Install] section)
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

[Install]
WantedBy=multi-user.target
EOF

# 4. Reload and Restart
sudo systemctl daemon-reload
sudo systemctl enable toji-bot
sudo systemctl restart toji-bot

# 5. Check logs to confirm it's fixed
sudo journalctl -u toji-bot -f
