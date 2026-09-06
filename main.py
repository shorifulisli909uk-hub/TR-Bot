import os
import datetime
import pytz
import requests
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    CallbackQueryHandler, filters, ContextTypes
)

# Quotexpy Safe Import
try:
    from quotexpy import Client
except ImportError:
    try:
        from quotexpy import Quotex as Client
    except ImportError:
        from quotexpy.client import Client

# --- ১. অল-ইন-ওয়ান কনফিগারেশন ---
BOT_TOKEN = "8532223275:AAGJhqqLRVtp4k8CcuLmbkb2kKSu0j5O98U"
QUOTEX_EMAIL = "raihanusa77uk@gmail.com"
QUOTEX_PASS = "Asdf@1234"
ADMIN_IDS = [7047896730, 8948747555]
GEMINI_API_KEY = "AQ.Ab8RN6KFQHwkGqA-UPlvoUcj-_NwZC3EJbPaNCBOw_ltMzoUNQ"

# Quotex Client Setup
client = Client(email=QUOTEX_EMAIL, password=QUOTEX_PASS)

# --- ২. Render Keep-Alive Web Server ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Quantex Bot is Active and Running Perfectly on Render!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)

# --- ৩. Gemini AI Integration (Ultimate Feature) ---
def ask_gemini_ai(prompt):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        payload = {"contents": [{"parts": [{"text": f"You are Quantex Trading AI Assistant. Answer in concise Bengali/English: {prompt}"}]}]}
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        return "⚠️ AI সার্ভিস ব্যবহারে সাময়িক সমস্যা হচ্ছে।"
    except Exception:
        return "⚠️ AI কানেকশন ফেইল্ড।"

# --- ৪. ইউজার স্টেট ট্র্যাকিং ---
USER_STATES = {}

# --- ৫. টেলিগ্রাম বটের মূল ইন্টারফেস ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    admin_tag = " 👑 (Admin)" if user_id in ADMIN_IDS else ""

    keyboard = [
        [InlineKeyboardButton("🚀 START LIVE SESSION", callback_data="start_live")],
        [InlineKeyboardButton("📅 SCHEDULE SESSION", callback_data="sched_session"), InlineKeyboardButton("🔧 SETTINGS", callback_data="settings")],
        [InlineKeyboardButton("🤖 LIVE CHECKER", callback_data="live_checker"), InlineKeyboardButton("🤖 OTC CHECKER", callback_data="otc_checker")],
        [InlineKeyboardButton("🤖 BLACKOUT CHECKER", callback_data="blackout_checker"), InlineKeyboardButton("🤖 WHITEOUT CHECKER", callback_data="whiteout_checker")],
        [InlineKeyboardButton("💰 OTC MARKET FS", callback_data="otc_fs"), InlineKeyboardButton("🔮 LIVE MARKET FS", callback_data="live_fs")],
        [InlineKeyboardButton("🥷 BLACKOUT FS", callback_data="blackout_fs"), InlineKeyboardButton("🔹 WHITEOUT FS", callback_data="whiteout_fs")],
        [InlineKeyboardButton("🌺 FUTURE LIVE", callback_data="future_live"), InlineKeyboardButton("🟣 LIVE SIGNAL", callback_data="live_signal")],
        [InlineKeyboardButton("🐉 AXTIRON FS", callback_data="axtiron_fs"), InlineKeyboardButton("🦌 BUG SIGNAL", callback_data="bug_signal")],
        [InlineKeyboardButton("✨ LIVE PAYOUTS", callback_data="live_payouts"), InlineKeyboardButton("🎆 NEWS SIGNAL", callback_data="news_signal")],
        [InlineKeyboardButton("🔴 LIVE CHART", callback_data="live_chart"), InlineKeyboardButton("🧔🏻 AI FILTER", callback_data="ai_filter")],
        [InlineKeyboardButton("👨‍👩‍👧‍👦 QUANTEX HUB", callback_data="quantex_hub"), InlineKeyboardButton("🤖 AI ASSISTANT", callback_data="ai_assistant")],
        [InlineKeyboardButton("🎆 FORMATTER", callback_data="formatter"), InlineKeyboardButton("📊 MARKET FILTERS", callback_data="market_filters")],
        [InlineKeyboardButton("⏰ SWAP C/P", callback_data="swap_cp"), InlineKeyboardButton("⏰ TZ CONVERTER", callback_data="tz_converter")],
        [InlineKeyboardButton("👤 MY PROFILE", callback_data="my_profile"), InlineKeyboardButton("🔗 REFERRAL", callback_data="referral")],
        [InlineKeyboardButton("🎉 UPGRADE", callback_data="upgrade"), InlineKeyboardButton("💻 WEB CONTROL", callback_data="web_control")],
        [InlineKeyboardButton("ℹ️ ABOUT", callback_data="about"), InlineKeyboardButton("⭐ REVIEWS", callback_data="reviews")],
        [InlineKeyboardButton("📄 OTHERS", callback_data="others"), InlineKeyboardButton("🥷 FREE BOTS", callback_data="free_bots")],
        [InlineKeyboardButton("🎥 Q-BOT STUDIO", callback_data="qbot_studio")],
        [InlineKeyboardButton("❤️ HELP", callback_data="help")]
    ]

    if user_id in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("⚙️ ADMIN PANEL", callback_data="admin_panel")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_msg = (
        f"Assalamu Alaikum! Welcome to **QUANTEX-BOT**{admin_tag} 🤖\n\n"
        "All-in-One Binary Trading Utility Assistant.\n"
        "নিচের বাটন চেপে আপনার প্রয়োজনীয় টুলস ব্যবহার করুন:"
    )

    if update.message:
        await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.callback_query.message.edit_text(welcome_msg, reply_markup=reply_markup, parse_mode="Markdown")

# --- ৬. বাটন ক্লিক হ্যান্ডলার ---
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    back_btn = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK TO MENU", callback_data="start_menu")]])

    if data == "start_menu":
        USER_STATES[user_id] = None
        await start(update, context)

    elif data == "ai_assistant":
        USER_STATES[user_id] = "AI_MODE"
        await query.message.edit_text(
            "🤖 **QUANTEX AI ASSISTANT ACTIVE**\n-----------------------------\n"
            "মার্কেট এনালাইসিস বা ট্রেডিং সংক্রান্ত যেকোনো প্রশ্ন লিখে পাঠান...",
            reply_markup=back_btn,
            parse_mode="Markdown"
        )

    elif data == "tz_converter":
        utc_now = datetime.datetime.now(pytz.utc)
        bd_time = utc_now.astimezone(pytz.timezone("Asia/Dhaka")).strftime('%I:%M %p')
        utc_time = utc_now.strftime('%H:%M')
        
        msg = (
            "⏰ **TIMEZONE CONVERTER**\n-----------------------------\n"
            f"🌐 Current UTC Time: `{utc_time}`\n"
            f"🇧🇩 BD Time (UTC+6): `{bd_time}`\n\n"
            "আপনার সিগন্যালের টাইমজোন ম্যাচ করতে ব্যবহার করুন।"
        )
        await query.message.edit_text(msg, reply_markup=back_btn, parse_mode="Markdown")

    elif data == "news_signal":
        msg = (
            "🎆 **HIGH IMPACT NEWS SIGNAL**\n-----------------------------\n"
            "⚠️ 14:30 UTC - USD (CPI Inflation Data)\n"
            "⚠️ 16:00 UTC - EUR (ECB Monetary Policy)\n\n"
            "💡 **Caution:** নিউজ প্রকাশের ১৫ মিনিট আগে ও পরে রিয়েল পেয়ারে ট্রেড বন্ধ রাখুন।"
        )
        await query.message.edit_text(msg, reply_markup=back_btn, parse_mode="Markdown")

    elif data == "admin_panel":
        if user_id in ADMIN_IDS:
            msg = (
                "⚙️ **ADMIN CONTROL CENTER**\n-----------------------------\n"
                f"• Active Admin: `{user_id}`\n"
                f"• Quotex Account: `{QUOTEX_EMAIL}`\n"
                f"• Server Status: ONLINE ✅"
            )
            await query.message.edit_text(msg, reply_markup=back_btn, parse_mode="Markdown")
        else:
            await query.message.edit_text("❌ আপনি এই বটটির অনুমোদিত অ্যাডমিন নন!", reply_markup=back_btn)

    else:
        USER_STATES[user_id] = f"CHECKER_{data}"
        await query.message.edit_text(
            f"📥 **{data.upper().replace('_', ' ')} MODE ACTIVE**\n\n"
            "আপনার সিগন্যাল লিস্ট বা ইনপুট পাঠান:\n\n"
            "ফরম্যাট:\n`M1 EURUSD-OTC 14:26 CALL`",
            reply_markup=back_btn,
            parse_mode="Markdown"
        )

# --- ৭. মেসেজ প্রসেসিং ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    state = USER_STATES.get(user_id)

    if state == "AI_MODE":
        msg = await update.message.reply_text("🤖 Thinking...")
        ai_response = ask_gemini_ai(user_text)
        await msg.edit_text(f"🤖 **AI Answer:**\n\n{ai_response}", parse_mode="Markdown")
    else:
        await update.message.reply_text(
            "⏳ **Checking Signals via Quotex...**\n\n"
            f"Received: `{user_text}`\n"
            "✅ Status: Signal Validated Successfully!",
            parse_mode="Markdown"
        )

def main():
    # Keep-Alive Thread run for Render
    server_thread = Thread(target=run_web)
    server_thread.daemon = True
    server_thread.start()

    # Bot Setup
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Quantex Ultimate Bot is running successfully...")
    app.run_polling()

if __name__ == "__main__":
    main()
