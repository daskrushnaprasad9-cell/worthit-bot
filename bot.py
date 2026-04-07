from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes
import os
import urllib.parse
import requests

# 🔑 ENV VARIABLES
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AMAZON_TAG = os.getenv("AMAZON_TAG")

user_query_store = {}

# 🧠 AI FUNCTION
def ask_ai(query):
    try:
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

        data = {
            "contents": [{
                "parts": [{
                    "text": f"Extract keywords from this: {query}"
                }]
            }]
        }

        response = requests.post(url, json=data)
        result = response.json()

        # 👉 Extract AI text safely
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        return text

    except Exception as e:
        print("AI Error:", e)
        return query  # fallback

# ▶️ START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Send any product")

# 💬 USER MESSAGE
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    user_id = update.message.from_user.id

    # 🧠 Use AI
    ai_result = ask_ai(query)

    user_query_store[user_id] = ai_result

    keyboard = [
        [InlineKeyboardButton("💰 Budget", callback_data="budget")],
        [InlineKeyboardButton("⭐ Quality", callback_data="quality")],
        [InlineKeyboardButton("🔥 Best", callback_data="best")]
    ]

    await update.message.reply_text(
        f"🤖 I understood: {ai_result}\n\nWhat do you want?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 🔘 BUTTON
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user_id = q.from_user.id
    choice = q.data
    user_query = user_query_store.get(user_id, "")

    search = urllib.parse.quote(user_query + " " + choice)
    link = f"https://www.amazon.in/s?k={search}&tag={AMAZON_TAG}"

    await q.edit_message_text(f"🔥 Here you go 👇\n\n{link}")

# 🚀 RUN
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, reply))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
