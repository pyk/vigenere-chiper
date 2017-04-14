#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import os

from flask import Flask, request
import telepot
import redis

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
update_queue = Queue()

# Setup redis untuk menyimpan vigenere keys nya
REDIS_URL = os.getenv('REDIS_URL', 'defaultredisurl')
rds = redis.from_url(REDIS_URL) 

# Fungsi untuk mengambil vigenere key
def get_vigenere_key(user_id):
    redis_key = 'vigenere_key/{}'.format(user_id)
    key = rds.get(redis_key)
    return key

# Telegram bot handler
def handler(message):
    # Answer inline query
    if 'query' in message:
        print('DEBUG: answer inline_query')
        query_id = message['id']
        query_text = message['query']
        print('DEBUG: query_id:', query_id)
        # Cek dulu apakah user sudah menentukan kuncinya
        user_id = message['from']['id']
        user_key = get_vigenere_key(user_id)
        print('DEBUG: user_id:', user_id)
        print('DEBUG: user_key:', user_key)
        if user_key:
            # Answer inline query here
            return 'OK'
        else:
            # Setup kunci user dulu
            bot.answerInlineQuery(query_id, [], 
                        switch_pm_text='Tentukan kunci Vigénere cipher',
                        switch_pm_parameter='setkunci')
    elif 'text' in message:
        message_text = message['text']
        if message_text == '/start setkunci':
            chat_id = message['chat']['id']
            message_id = message['message_id']
            # Answer dengan masukkan kunci
            bot.sendMessage(chat_id, 
                    'OK. Kirimkan kunci Vigénere cipher nya ke aku boz',
                    reply_to_message_id=message_id)
            print("DEBUG: menunggu reply kunci vigenere chipernya")
    print("DEBUG: message:", message)

bot.message_loop(handler, source=update_queue)

@app.route('/telegram-webhook', methods=['GET', 'POST'])
def telegram_webhook():
    update_queue.put(request.data)
    return 'OK'

if __name__ == '__main__':
    bot.setWebhook(TELEGRAM_WEBHOOK_URL)
    app.run(host='0.0.0.0', debug=True, use_reloader=True)
