import telebot

TOKEN = "8647264299:AAGtbTlNMs6CvFFUWkLN-6IHi1Ysx9WVzAc"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ Bot Working Successfully!")

print("Bot Started...")

bot.infinity_polling()
