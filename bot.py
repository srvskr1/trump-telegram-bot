from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from transformers import pipeline
import requests
import os

# 🔐 Secure credentials via environment variables
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

summarizer = None  # delay initialization

async def trump(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global summarizer
    if summarizer is None:
        summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")


# 📡 Fetch news from NewsAPI
def fetch_trump_news():
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "Donald Trump",
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": 3,
        "apiKey": NEWS_API_KEY
    }
    response = requests.get(url, params=params)
    return response.json().get("articles", [])

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! Use /trump to get today’s Trump news.")

# /trump command handler
async def trump(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Fetching latest Trump news...")
    articles = fetch_trump_news()

    if not articles:
        await update.message.reply_text("⚠️ No recent news found.")
        return

    for article in articles:
        title = article.get("title", "No title")
        url = article.get("url", "")
        content = article.get("description") or article.get("content") or ""
        if content:
            try:
                summary = summarizer(content[:500], max_length=60, min_length=20, do_sample=False)[0]['summary_text']
            except Exception as e:
                summary = "⚠️ Could not summarize the content."

            message = f"🗞️ *{title}*\n\n📝 {summary}\n\n🔗 [Read More]({url})"
            await update.message.reply_text(message, parse_mode="Markdown", disable_web_page_preview=True)

# Launch the bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("trump", trump))
    app.run_polling()

if __name__ == "__main__":
    main()
