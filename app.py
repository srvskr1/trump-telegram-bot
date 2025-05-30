import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters
from transformers import pipeline

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)
app = Flask(__name__)
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

# Define bot commands
def start(update, context):
    update.message.reply_text("👋 Welcome! Use /trump to get today’s Trump news.")

def trump(update, context):
    import requests
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "Donald Trump",
        "sortBy": "publishedAt",
        "pageSize": 3,
        "language": "en",
        "apiKey": os.getenv("NEWS_API_KEY")
    }
    res = requests.get(url, params=params).json()
    articles = res.get("articles", [])
    if not articles:
        update.message.reply_text("⚠️ No recent news found.")
        return

    for a in articles:
        summary = summarizer(a['content'][:500])[0]['summary_text']
        msg = f"🗞️ *{a['title']}*\n\n📝 {summary}\n🔗 [Read More]({a['url']})"
        update.message.reply_text(msg, parse_mode="Markdown", disable_web_page_preview=True)

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("trump", trump))

# Flask webhook route
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot is running", 200
