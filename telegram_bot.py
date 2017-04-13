from datetime import datetime
import os

from flask import Flask
import telepot

try:
    from Queue import Queue
except ImportError:
    from queue import Queue

# Flask app
app = Flask(__name__)

# Setup telegram bot
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', 'defaulttoken')
TELEGRAM_WEBHOOK_URL = os.getenv('TELEGRAM_WEBHOOK_URL', 'webhook-url')
bot = telepot.Bot(TELEGRAM_TOKEN)
bot.setWebhook(TELEGRAM_WEBHOOK_URL)
update_queue = Queue()

# Telegram bot handler
def handler(message):
    print("DEBUG: message:", message)

bot.message_loop(handler, source=update_queue)

@app.route('/telegram-webhook', methods=['GET', 'POST'])
def telegram_webhook():
    update_queue.put(request.data)
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, use_reloader=True)
