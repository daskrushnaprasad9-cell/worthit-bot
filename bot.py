import requests
import time
import os
import urllib.parse

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AMAZON_TAG = os.getenv("AMAZON_TAG")

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
last_update_id = None

user_data = {}

# 🧠 AI to understand product
def ask_ai(query):
    try:
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        data = {
            "contents": [{
                "parts": [{"text": f"Extract product name from: {query}"}]
            }]
        }
        res = requests.post(url, json=data).json()
        return res["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return query

# 📩 Send message
def send(chat_id, text, keyboard=None):
    url = f"{BASE_URL}/sendMessage"
    data = {"chat_id": chat_id, "text": text}

    if keyboard:
        data["reply_markup"] = keyboard

    requests.post(url, json=data)

# 🔘 Show options
def show_options(chat_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": "💰 Budget", "callback_data": "budget"}],
            [{"text": "⭐ Best Quality", "callback_data": "quality"}],
            [{"text": "🔥 Best Overall", "callback_data": "best"}]
        ]
    }
    send(chat_id, "Choose option:", keyboard)

# 🛒 Generate product links (dummy smart logic)
def get_products(product, choice):
    base = f"https://www.amazon.in/s?k={urllib.parse.quote(product)}&tag={AMAZON_TAG}"

    if choice == "budget":
        return [
            f"1️⃣ Budget Option\n{base}&sort=price-asc-rank",
            f"2️⃣ Affordable Pick\n{base}&sort=price-asc-rank",
            f"3️⃣ Value for Money\n{base}&sort=price-asc-rank"
        ]

    elif choice == "quality":
        return [
            f"1️⃣ Premium Quality\n{base}&sort=-review-rank",
            f"2️⃣ Top Rated\n{base}&sort=-review-rank",
            f"3️⃣ High Performance\n{base}&sort=-review-rank"
        ]

    else:
        return [
            f"1️⃣ Best Overall\n{base}",
            f"2️⃣ Most Popular\n{base}",
            f"3️⃣ Trending Now\n{base}"
        ]

# 🔁 Main loop
def main():
    global last_update_id

    while True:
        updates = requests.get(f"{BASE_URL}/getUpdates", params={"offset": last_update_id}).json()

        for u in updates.get("result", []):
            last_update_id = u["update_id"] + 1

            # 📩 Message
            if "message" in u:
                msg = u["message"]
                chat_id = msg["chat"]["id"]
                text = msg.get("text")

                if text:
                    product = ask_ai(text)
                    user_data[chat_id] = product

                    send(chat_id, f"🔍 Searching for: {product}")
                    show_options(chat_id)

            # 🔘 Button click
            elif "callback_query" in u:
                cq = u["callback_query"]
                chat_id = cq["message"]["chat"]["id"]
                choice = cq["data"]

                product = user_data.get(chat_id, "product")

                results = get_products(product, choice)

                reply = "\n\n".join(results)

                send(chat_id, f"🔥 Results for {product}:\n\n{reply}")

        time.sleep(1)

if __name__ == "__main__":
    main()
