#!/bin/bash

# Get current path and python path
WORKING_DIR=$(pwd)
PYTHON_PATH="$WORKING_DIR/venv/bin/python3"

if [ ! -f "$PYTHON_PATH" ]; then
    PYTHON_PATH=$(which python3)
fi

echo "Detected Working Directory: $WORKING_DIR"
echo "Detected Python Path: $PYTHON_PATH"

# Create the service file
cat <<EOF > toji-bot.service
[Unit]
Description=TOJI CHK Telegram Bot
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$WORKING_DIR
EnvironmentFile=$WORKING_DIR/.env
ExecStart=$PYTHON_PATH $WORKING_DIR/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "New toji-bot.service file created!"
echo "To apply changes, run:"
echo "sudo cp toji-bot.service /etc/systemd/system/toji-bot.service"
echo "sudo systemctl daemon-reload"
echo "sudo systemctl restart toji-bot"
echo "sudo systemctl status toji-bot"
