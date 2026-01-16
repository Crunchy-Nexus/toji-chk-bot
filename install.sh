#!/bin/bash

echo "════════════════════════════════════════"
echo "   🤖 TOJI CHK BOT - Auto Installer"
echo "════════════════════════════════════════"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "Please install Python 3.11 or higher first:"
    echo "  sudo apt update"
    echo "  sudo apt install python3 python3-pip python3-full -y"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Create Virtual Environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment! Make sure python3-full is installed."
        echo "Trying: sudo apt install python3-full -y"
        sudo apt install python3-full -y
        python3 -m venv venv
    fi
fi

# Install required packages in venv
echo "📦 Installing dependencies into virtual environment..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install python-telegram-bot requests python-dotenv aiohttp fake-useragent beautifulsoup4 faker

echo ""
echo "✅ Dependencies installed successfully!"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    if [ -f .env.example ]; then
        cp .env.example .env
    else
        echo "BOT_TOKEN=your_bot_token_here" > .env
    fi
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your bot token!"
    echo ""
    echo "Please run:"
    echo "  nano .env"
    echo ""
    echo "Replace 'your_bot_token_here' with your actual token from @BotFather"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "════════════════════════════════════════"
echo "   ✅ Installation Complete!"
echo "════════════════════════════════════════"
echo ""
echo "📝 Next steps:"
echo "  1. Edit .env file: nano .env"
echo "  2. Add your bot token from @BotFather"
echo "  3. Run the bot: ./run_bot.sh"
echo ""
echo "Or use systemd for production (see VPS_DEPLOYMENT.md)"
echo ""
