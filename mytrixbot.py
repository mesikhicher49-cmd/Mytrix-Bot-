import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException
import json
import os
import time
import threading
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ================= CONFIG =================
TOKEN = "7913884752:AAFtcf1LP2RyVS3gftagtIyi1nSCBLPDokM"

ADMINS = [1251961776, 5665198013]
CHANNEL_ID = -1002046725593
VIDEO_NOTE_ID = "DQACAgIAAxkBAAMmaZHbU1Le3aRiHRnhlzkLvs7ACAEAAtKcAAJckYlI7JubZ5GIKJY6BA"

PROMO_IMAGE = "https://i.ibb.co/Nghfc7KN/IMG-20260222-161712-757.jpg"

USERS_DB = "users.json"
LAST_BROADCAST = "last_broadcast.json"
BROADCAST_MODE = "broadcast_mode.txt"

# ============ ROBUST SESSION SETUP ============
session = requests.Session()

# Retry strategy: retry on common server errors & timeouts
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
)
adapter = HTTPAdapter(
    max_retries=retry_strategy,
    pool_connections=100,
    pool_maxsize=100
)
session.mount("https://", adapter)
session.mount("http://", adapter)

# Force a default timeout for every request
def request_with_timeout(method, url, **kwargs):
    kwargs.setdefault('timeout', 30)  # 30 seconds
    return session.request(method, url, **kwargs)

session.request = request_with_timeout

# Create bot with our custom session
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")
bot.session = session

# ================= FILE HELPERS =================
def load(file):
    if not os.path.exists(file):
        return {}
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return {}

def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

# Ensure files exist
for f in [USERS_DB, LAST_BROADCAST]:
    if not os.path.exists(f):
        save(f, {})

# Remove stale broadcast flag on startup
if os.path.exists(BROADCAST_MODE):
    os.remove(BROADCAST_MODE)

# ================= PROMO =================
def send_promo_later(user_id):
    time.sleep(1800)  # 30 minutes

    promo_text = """🥳🥳😄🫣😬😴▶️❗️

😕10 Seats left guys hurry up 

🔗 ULTIMATE TOURNAMENT SANJAY TRADER 

📊 30$➜ 3000$ TOURNAMENT STRATEGY

💥 FULL REFUND IF LOSS

⏱ 1000% RECOVERY 

👍https://t.me/m/J8aThFwmMzdl

☄️OWNER: @SANJAYBHAGTANI
"""

    try:
        bot.send_photo(user_id, PROMO_IMAGE, caption=promo_text)
    except Exception:
        pass  # user may have blocked or left

# ================= JOIN REQUEST =================
@bot.chat_join_request_handler()
def join_handler(request):
    try:
        # Only handle our target channel
        if request.chat.id != CHANNEL_ID:
            return

        # Approve the request – may fail if user already in channel
        bot.approve_chat_join_request(
            chat_id=request.chat.id,
            user_id=request.from_user.id
        )
    except ApiTelegramException as e:
        # Ignore "already participant" error (user somehow already in channel)
        if e.error_code == 400 and "USER_ALREADY_PARTICIPANT" in e.description:
            return
        else:
            # Unexpected API error – log and give up for this user
            print(f"JOIN ERROR (approve): {e}")
            return
    except Exception as e:
        print(f"JOIN ERROR (approve): {e}")
        return

    # Save user to database
    users = load(USERS_DB)
    users[str(request.from_user.id)] = request.from_user.username
    save(USERS_DB, users)

    # Send welcome message
    welcome_text = """𝗪𝗲𝗹𝗰𝗼𝗺𝗲 🔥  
𝗔𝗴𝗮𝗿 𝗹𝗶𝗳𝗲 𝗰𝗵𝗮𝗻𝗴𝗲 𝗸𝗮𝗿𝗻𝗶 𝗵𝗮𝗶 𝘁𝗿𝗮𝗱𝗶𝗻𝗴 𝘀𝗲,  
𝘃𝗶𝗱𝗲𝗼 𝗱𝗲𝗸𝗵𝗼 𝗮𝘂𝗿 𝗹𝗶𝗻𝗸 𝗽𝗮𝗿 𝗰𝗹𝗶𝗰𝗸 𝗸𝗮𝗿𝗸𝗲 𝗦𝗧𝗔𝗥𝗧 𝗯𝗵𝗲𝗷𝗼.
"""
    try:
        bot.send_message(request.from_user.id, welcome_text)
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(
                "💬 Message Now",
                url="https://t.me/m/grrnmylXYjE1"
            )
        )
        bot.send_video_note(
            request.from_user.id,
            VIDEO_NOTE_ID,
            reply_markup=markup
        )
    except ApiTelegramException as e:
        if e.error_code == 403:  # bot blocked by user
            pass  # silently ignore
        else:
            print(f"JOIN ERROR (send): {e}")
    except Exception as e:
        print(f"JOIN ERROR (send): {e}")

    # Schedule promo message after 30 minutes
    threading.Thread(
        target=send_promo_later,
        args=(request.from_user.id,),
        daemon=True
    ).start()

# ================= ADMIN PANEL =================
@bot.message_handler(commands=['panel'])
def panel(message):
    if message.chat.id not in ADMINS:
        return

    total = len(load(USERS_DB))

    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("📢 Start Broadcast", callback_data="broadcast"))
    markup.row(types.InlineKeyboardButton(f"👥 Users: {total}", callback_data="stats"))
    markup.row(types.InlineKeyboardButton("🗑 Delete Last Msg", callback_data="delete"))

    bot.send_message(
        message.chat.id,
        "🔥 *ADMIN CONTROL PANEL* 🔥",
        reply_markup=markup
    )

# ================= CALLBACK =================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.message.chat.id not in ADMINS:
        return

    if call.data == "stats":
        total = len(load(USERS_DB))
        bot.answer_callback_query(call.id, f"Total Users: {total}", show_alert=True)

    elif call.data == "broadcast":
        with open(BROADCAST_MODE, "w") as f:
            f.write("on")
        bot.send_message(call.message.chat.id, "📢 Send message to broadcast now.")

    elif call.data == "delete":
        sent = load(LAST_BROADCAST)
        for uid, msg_id in sent.items():
            try:
                bot.delete_message(int(uid), msg_id)
            except Exception:
                pass
        bot.send_message(call.message.chat.id, "✅ Deleted last broadcast.")

# ================= BROADCAST =================
@bot.message_handler(func=lambda m: m.chat.id in ADMINS and os.path.exists(BROADCAST_MODE))
def broadcast(message):
    # Remove flag immediately to avoid double-trigger
    os.remove(BROADCAST_MODE)

    users = load(USERS_DB)
    sent_data = {}

    for uid in users.keys():
        try:
            msg = bot.copy_message(int(uid), message.chat.id, message.message_id)
            sent_data[uid] = msg.message_id
            time.sleep(0.2)  # avoid hitting rate limits
        except Exception:
            # User blocked, deleted account, or any other error – skip
            continue

    save(LAST_BROADCAST, sent_data)
    bot.send_message(message.chat.id, "✅ Broadcast completed.")

# ================= RUN =================
if name == "main":
    print("🔥 FULL FEATURE BOT RUNNING...")
    while True:
        try:
            bot.infinity_polling(skip_pending=True, timeout=20, long_polling_timeout=20)
        except Exception as e:
            print(f"Polling error: {e}, restarting in 5 seconds...")
            time.sleep(5)