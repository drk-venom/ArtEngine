import logging
import requests
import os
from flask import Flask, request
from telebot import TeleBot, types
import threading

# Tokens
TELEGRAM_TOKEN = "8103733606:AAFfw4COXT-3hkpyepzZdaatfkbSv5NaAro"
DEEPAI_API_KEY = "64c75589-7261-485f-8310-7167437c377c"
WEBHOOK_URL = "https://artengine.onrender.com"  # Make sure this matches your Render URL

# Logging
logging.basicConfig(level=logging.INFO)

# Initialize bot
bot = TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# Telegram bot handlers
@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.InlineKeyboardMarkup()
    developer_button = types.InlineKeyboardButton(
        "💻 Developer: \/ ē ⁿ ∅ |\/|",
        url="https://t.me/Scarface_786"
    )
    keyboard.add(developer_button)

    bot.send_message(
        message.chat.id,
        "👋 Welcome! Send me any prompt and I'll generate an image...\n\n"
        "Use the button below to contact the developer:",
        reply_markup=keyboard
    )

@bot.message_handler(func=lambda message: True)
def generate_image(message):
    prompt = message.text
    url = "https://api.deepai.org/api/text2img"

    try:
        # Send initial status message
        status_msg = bot.send_message(message.chat.id, "⏳ Generating your image...")

        # Make request to DeepAI
        response = requests.post(
            url,
            data={'text': prompt},
            headers={'api-key': DEEPAI_API_KEY},
            timeout=60
        )
        response_json = response.json()
        print(f"DeepAI Response: {response_json}")  # Debug

        # Delete status message
        bot.delete_message(message.chat.id, status_msg.message_id)

        if "output_url" in response_json:
            image_url = response_json['output_url']

            # Download and send image
            img_response = requests.get(image_url, timeout=30)

            if img_response.status_code == 200:
                # Send image directly from URL
                bot.send_photo(
                    message.chat.id,
                    photo=image_url,
                    caption=f"✨ Prompt: {prompt}"
                )
            else:
                bot.send_message(message.chat.id, "⚠️ Error: Could not download generated image")

        else:
            error_msg = response_json.get('err', 'Unknown error occurred')
            bot.send_message(message.chat.id, f"⚠️ API Error: {error_msg}")

    except requests.exceptions.Timeout:
        bot.send_message(message.chat.id, "⚠️ Error: Request timed out. Please try again.")
    except requests.exceptions.RequestException as e:
        bot.send_message(message.chat.id, f"⚠️ Network Error: {str(e)}")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Unexpected Error: {str(e)}")

# Flask route for Telegram webhook
@app.route(f"/webhook/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    """
    Webhook route for Telegram to send updates
    """
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    else:
        return "Invalid content type", 400

# Flask route for health check
@app.route("/")
def index():
    return "🤖 Bot is running successfully!"

@app.route("/set_webhook")
def set_webhook_route():
    """
    Route to manually set webhook
    """
    try:
        webhook_url = f"{WEBHOOK_URL}/webhook/{TELEGRAM_TOKEN}"
        result = bot.remove_webhook()
        result = bot.set_webhook(url=webhook_url)
        return f"Webhook set to: {webhook_url} - Success: {result}"
    except Exception as e:
        return f"Error setting webhook: {str(e)}"

@app.route("/remove_webhook")
def remove_webhook_route():
    """
    Route to remove webhook
    """
    try:
        result = bot.remove_webhook()
        return f"Webhook removed - Success: {result}"
    except Exception as e:
        return f"Error removing webhook: {str(e)}"

def run_flask():
    """
    Run Flask app
    """
    app.run(host="0.0.0.0", port=5000, debug=False)

def run_bot_polling():
    """
    Run bot in polling mode (for development)
    """
    print("Starting bot in polling mode...")
    bot.remove_webhook()
    bot.infinity_polling(timeout=60, long_polling_timeout=60)

if __name__ == "__main__":
    # For production with webhook
    if os.environ.get('RENDER', None):  # Running on Render
        print("Starting in webhook mode...")
        # Set webhook on startup
        webhook_url = f"{WEBHOOK_URL}/webhook/{TELEGRAM_TOKEN}"
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)
        print(f"Webhook set to: {webhook_url}")
        run_flask()
    else:
        # For local development - use polling
        print("Starting in polling mode for development...")
        run_bot_polling()
