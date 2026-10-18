import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = '8828858819:AAEV--N52xYk4_ycHbNwBDnemvIRgHy8PzI'
ELEVENLABS_API_KEY = 'sk_3885be7f2510a94e8c20085aedc77012480588344fdafcc7'
VOICE_ID = 'dmEkARJxJEqd5ADSYy8D'

# Render ကပေးထားတဲ့ သင့်ရဲ့ Web Service URL (ဥပမာ - https://telegram-voice-bot-iley.onrender.com)
# ကိုယ့်ရဲ့ Render URL အမှန်နဲ့ အစားထိုးပေးပါ
RENDER_EXTERNAL_URL = 'https://telegram-voice-bot-iley.onrender.com'

app_flask = Flask(__name__)

# Telegram Application Setup
telegram_app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

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
            logger.error(f"ElevenLabs Error: {response.status_code} - {response.text}")
            await update.message.reply_text(f"အသံဖန်တီးရာတွင် အမှားအယွင်း ရှိနေပါသည်။ (Error: {response.status_code})")
    except Exception as e:
        logger.error(f"Exception: {e}")
        await update.message.reply_text("ဆာဗာတွင် ချိတ်ဆက်မှု အမှားအယွင်း ရှိနေပါသည်။")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_to_voice))

@app_flask.route('/')
def index():
    return "Bot is alive!"

@app_flask.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    asyncist_run = telegram_app.update_queue.put(update)
    return 'ok'

async def setup_webhook():
    webhook_url = f"{RENDER_EXTERNAL_URL}/{TELEGRAM_BOT_TOKEN}"
    await telegram_app.bot.set_webhook(webhook_url)

if __name__ == '__main__':
    import asyncio
    asyncio.get_event_loop().run_until_complete(setup_webhook())
    
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host='0.0.0.0', port=port)
    
