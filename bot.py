import requests
import time
import os
import urllib.parse

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AMAZON_TAG = os.getenv("AMAZON_TAG")

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
last_update_id = None

def ask_ai(query):
    try:
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        data = {
            "contents": [{
                "parts": [{"text": f"Short shopping keywords: {query}"}]
            }]
        }
        res = requests.post(url, json=data).json()
        return res["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return query

def send(chat_id, text):
    requests.post(f"{BASE_URL}/sendMessage", data={"chat_id": chat_id, "text": text})

def main():
    global last_update_id

    while True:
        updates = requests.get(f"{BASE_URL}/getUpdates", params={"offset": last_update_id}).json()

        for u in updates.get("result", []):
            last_update_id = u["update_id"] + 1
            msg = u.get("message", {})
            text = msg.get("text")

            if text:
                chat_id = msg["chat"]["id"]

                ai_text = ask_ai(text)
                search = urllib.parse.quote(ai_text + " best")
                link = f"https://www.amazon.in/s?k={search}&tag={AMAZON_TAG}"

                send(chat_id, f"🤖 {ai_text}\n\n🔥 Buy here 👇\n{link}")

        time.sleep(1)

if __name__ == "__main__":
    main()
