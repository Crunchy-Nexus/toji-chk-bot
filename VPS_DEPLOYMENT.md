# 🚀 Complete VPS Deployment Guide - Step by Step

## 🎯 PART 1: Prepare Your Code for GitHub
1. **Create GitHub Repository:** Go to GitHub.com, create a new private repository named `toji-chk-bot`.
2. **Upload Your Code:** Upload all project files to the repository.

## 🎯 PART 2: Set Up Your VPS Server
1. **Connect to Your VPS:** `ssh root@YOUR_VPS_IP`
2. **Update System:** `sudo apt update && sudo apt upgrade -y`
3. **Install Required Software:**
   ```bash
   sudo apt install python3 python3-pip python3-venv git -y
   ```

## 🎯 PART 3: Clone and Install Bot
1. **Clone from GitHub:**
   ```bash
   cd ~
   git clone https://github.com/YOUR_USERNAME/toji-chk-bot.git
   cd toji-chk-bot
   ```
2. **Install with Auto-Script:**
   ```bash
   bash install.sh
   ```
   *This script automatically creates a virtual environment and installs dependencies safely.*

3. **Configure Environment:**
   ```bash
   nano .env
   ```
   Add your token: `BOT_TOKEN=your_token_here` and `ADMIN_USERNAME=your_username`.

## 🎯 PART 4: Set Up 24/7 Running (systemd)
Run the automated systemd setup script:
```bash
bash setup_systemd.sh
```
*This will configure the bot to start on boot and restart automatically if it crashes.*

## 🎯 PART 5: Essential Commands
| Command | Description |
|---------|-------------|
| `sudo systemctl status toji-bot` | Check if bot is running |
| `sudo journalctl -u toji-bot -f` | View live bot logs |
| `sudo systemctl restart toji-bot` | Restart the bot |
| `sudo systemctl stop toji-bot` | Stop the bot |

## 🔐 Security Best Practices
1. **Firewall Setup:**
   ```bash
   sudo apt install ufw -y
   sudo ufw allow ssh
   sudo ufw enable
   ```
2. **Updates:** `git pull && sudo systemctl restart toji-bot`
3. **Backups:** Regularly backup `users.json` and `access_control.json`.

🎉 **Your bot is now production-ready!**
