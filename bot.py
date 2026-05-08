import telebot
from telebot import types
import time
import threading

# ================= CONFIG =================
TOKEN = "7913884752:AAFtcf1LP2RyVS3gftagtIyi1nSCBLPDokM"

CHANNEL_ID = -1002046725593

VIDEO_NOTE_ID = "DQACAgIAAxkBAAMmaZHbU1Le3aRiHRnhlzkLvs7ACAEAAtKcAAJckYlI7JubZ5GIKJY6BA"

PROMO_IMAGE = "https://i.ibb.co/Nghfc7KN/IMG-20260222-161712-757.jpg"

# ================= BOT =================
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# ================= PROMO =================
def send_promo(user_id):

    time.sleep(1500)  # 25 Minutes

    promo_text = """
🥳🥳😄🫣😬😴▶️❗️

😕10 Seats left guys hurry up

🔗 ULTIMATE TOURNAMENT SANJAY TRADER

📊 30$➜ 3000$ TOURNAMENT STRATEGY

💥 FULL REFUND IF LOSS

⏱ 1000% RECOVERY

☄️ OWNER: @SANJAYBHAGTANI
"""

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "💬 Message Now",
            url="https://t.me/m/grrnmylXYjE1"
        )
    )

    try:

        bot.send_photo(
            user_id,
            PROMO_IMAGE,
            caption=promo_text,
            reply_markup=markup
        )

    except Exception as e:

        print(f"PROMO ERROR: {e}")

# ================= JOIN REQUEST =================
@bot.chat_join_request_handler()
def join_handler(request):

    if request.chat.id != CHANNEL_ID:
        return

    try:

        bot.approve_chat_join_request(
            request.chat.id,
            request.from_user.id
        )

    except Exception as e:

        print(f"JOIN ERROR: {e}")
        return

    welcome_text = """
𝗪𝗲𝗹𝗰𝗼𝗺𝗲 🔥

𝗩𝗶𝗱𝗲𝗼 𝗱𝗲𝗸𝗵𝗼 𝗮𝘂𝗿 𝗹𝗶𝗻𝗸 𝗽𝗮𝗿 𝗰𝗹𝗶𝗰𝗸 𝗸𝗮𝗿𝗸𝗲 START 𝗯𝗵𝗲𝗷𝗼.
"""

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "💬 Message Now",
            url="https://t.me/m/grrnmylXYjE1"
        )
    )

    try:

        bot.send_message(
            request.from_user.id,
            welcome_text
        )

        bot.send_video_note(
            request.from_user.id,
            VIDEO_NOTE_ID,
            reply_markup=markup
        )

    except Exception as e:

        print(f"SEND ERROR: {e}")

    # Promo After 25 Minutes
    threading.Thread(
        target=send_promo,
        args=(request.from_user.id,),
        daemon=True
    ).start()

# ================= RUN =================
if __name__ == "__main__":

    print("🔥 BOT RUNNING")

    bot.remove_webhook()

    time.sleep(1)

    while True:

        try:

            bot.infinity_polling(
                skip_pending=True
            )

        except Exception as e:

            print(f"POLLING ERROR: {e}")

            time.sleep(5)
