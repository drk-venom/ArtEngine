import logging
import requests
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Hardcoded tokens/keys (⚠️ not recommended for production)
TELEGRAM_TOKEN = "8103733606:AAFfw4COXT-3hkpyepzZdaatfkbSv5NaAro"
DEEPAI_API_KEY = "64c75589-7261-485f-8310-7167437c377c"
WEBHOOK_URL = "https://artengine.onrender.com"

# Logging
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
app = Flask(__name__)

# --- Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(r"💻 Developer: \/ēⁿ∅|\/|", url="https://t.me/Scarface_786")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 Welcome! Send me any prompt and I'll generate an image...\n\n"
        "Use the button below to contact the developer:",
        reply_markup=reply_markup
    )

async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    url = "https://api.deepai.org/api/text2img"
    
    try:
        status_msg = await update.message.reply_text("⏳ Generating your image...")

        response = requests.post(
            url,
            data={'text': prompt},
            headers={'api-key': DEEPAI_API_KEY}
        )
        response_json = response.json()
        print(response_json)  # Debug

        if "output_url" in response_json:
            image_url = response_json['output_url']
            img_data = requests.get(image_url).content

            await status_msg.delete()
            await update.message.reply_photo(photo=img_data, caption=f"✨ Prompt: {prompt}")
        else:
            await status_msg.edit_text(f"⚠️ Error: {response_json}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)}")

# --- Flask Routes ---
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    application.update_queue.put(update)
    return "OK"

@app.route("/")
def index():
    return "Bot is running!"

# Build application
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_image))

# Set webhook
@app.before_first_request
def set_webhook():
    bot.set_webhook(f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
