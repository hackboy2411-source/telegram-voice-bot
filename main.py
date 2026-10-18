import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Render အတွက် Web Server (Port Timeout မဖြစ်အောင်)
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

# Background Thread နဲ့ Web Server စတင်ခြင်း
threading.Thread(target=run_web_server, daemon=True).start()

TELEGRAM_BOT_TOKEN = '8828858819:AAEV--N52xYk4_ycHbNwBDnemvIRgHy8PzI'
ELEVENLABS_API_KEY = 'sk_48e689d9519318fc953b82cfd7598603bd85f3900e98019c'
VOICE_ID = 'dmEkARJxJEqd5ADSYy8D'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါ။ Bot ထဲသို့ စာသားများ ပို့ပေးပါ၊ အသံဖိုင် ပြောင်းပေးပါမည်။")

async def text_to_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text("အသံဖိုင် ဖန်တီးနေပါသည်။ ခဏစောင့်ပါ...")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open("output.mp3", "wb") as f:
                f.write(response.content)
            await update.message.reply_audio(audio=open("output.mp3", "rb"))
        else:
            await update.message.reply_text(f"အသံဖန်တီးရာတွင် အမှားအယွင်း ရှိနေပါသည်။ (Error: {response.status_code})")
    except Exception as e:
        await update.message.reply_text("ချိတ်ဆက်မှု အမှားအယွင်း ရှိပါသည်။")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_to_voice))
    app.run_polling()
    
