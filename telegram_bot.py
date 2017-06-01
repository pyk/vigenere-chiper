#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import os

from flask import Flask, request
import telepot
import redis

import vigenere

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

def del_vigenere_key(user_id):
    redis_key = 'vigenere_key/{}'.format(user_id)
    rds.delete(redis_key)

def set_vigenere_key(user_id, key):
    redis_key = 'vigenere_key/{}'.format(user_id)
    key = rds.set(redis_key, key)
    return key

def set_chat_status(chat_id, status):
    redis_key = 'vigenere_status/{}'.format(chat_id)
    # Status ini akan otomatis kehapus jika udah lebih dari 60s
    rds.setex(redis_key, status, 60)

def get_chat_status(chat_id):
    redis_key = 'vigenere_status/{}'.format(chat_id)
    return rds.get(redis_key)


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
            cipher_text = ''
            try:
                cipher_text = vigenere.enkripsi(P=query_text, K=user_key)
            except Exception as err:
                print('DEBUG: gagal enkripsi:', err)
                cipher_text = "Maaf, terjadi kesalahan saat melakukan enkripsi. Pastikan plain teks hanya huruf abjad saja."
            # Jika kunci udah ke set maka kirim hasil enkripsinya
            reply_data = {
                'type': 'photo',
                'id': query_id,
                'photo_url': 'http://i.imgur.com/GpfBHuF.jpg',
                'thumb_url': 'http://i.imgur.com/GpfBHuF.jpg',
                'photo_width': 256,
                'photo_height': 256,
                'input_message_content': {
                    'message_text': cipher_text
                },
                'reply_markup': {
                    'inline_keyboard': [[{
                        'text': 'Dekripsi cipher teks',
                        'callback_data': cipher_text
                    }]]
                }
            }
            bot.answerInlineQuery(query_id, [reply_data],
                        cache_time=None,
                        is_personal=None)
        else:
            # Setup kunci user dulu
            bot.answerInlineQuery(query_id, [], 
                        switch_pm_text='Tentukan kunci Vigénere cipher',
                        switch_pm_parameter='setkunci')
    elif 'entities' in message:
        message_text = message['text']
        chat_id = message['chat']['id']
        message_id = message['message_id']
        first_name = message['from']['first_name']
        user_id = message['from']['id']
        
        # Setup kunci baru
        if message_text == '/start':
            # Answer dengan masukkan kunci
            pesan = "Hey {name}! Senang bisa chat denganmu. {name} bisa mention aku di chat mana aja untuk memulai enkripsi pesan yang ingin {name} kirim.".format(name=first_name)
            bot.sendMessage(chat_id, pesan)
            set_chat_status(chat_id, 'normal')

        # Setup kunci baru
        if message_text == '/buatkunci':
            # Answer dengan masukkan kunci
            pesan = "Hey {}, kirimkan kunci Vigénere cipher nya ke aku ya :). Kuncinya harus huruf abjad aja ya, tanpa spasi, nomor dan simbol-simbol.".format(first_name)
            bot.sendMessage(chat_id, pesan)
            set_chat_status(chat_id, 'menunggu_kunci')

        # Menghapus kunci
        if message_text == '/hapuskunci':
            # Cek apakah kuncinya ada
            kunci = get_vigenere_key(user_id)
            if kunci:
                del_vigenere_key(user_id)
                pesan = "Hey {}, kuncimu yang lama dah aku hapus ya. Untuk membuat kunci baru tinggal kirim perintah /buatkunci ke aku.".format(first_name)
                bot.sendMessage(chat_id, pesan)
                set_chat_status(chat_id, 'normal')
            else:
                pesan = "Hey {}, kamu belum punya kunci. Kirim perintah /buatkunci untuk membuat kunci baru.".format(first_name)
                bot.sendMessage(chat_id, pesan)
                set_chat_status(chat_id, 'normal')

        # Enkripsi dan dekripsi
        perintah_awal = message_text.split(' ')[0]
        if perintah_awal == '/enkripsi':
            kunci = get_vigenere_key(user_id)
            if kunci:
                plain_teks = message_text.split(' ')[1:]
                plain_teks = ' '.join(plain_teks)
                chiper_teks = vigenere.enkripsi(P=plain_teks, K=kunci)
                bot.sendMessage(chat_id, chiper_teks)
                set_chat_status(chat_id, 'normal')
            else:
                pesan = "Hey {}, kamu belum punya kunci. Kirim perintah /buatkunci untuk membuat kunci baru.".format(first_name)
                bot.sendMessage(chat_id, pesan)
                set_chat_status(chat_id, 'normal')
        if perintah_awal == '/dekripsi':
            kunci = get_vigenere_key(user_id)
            if kunci:
                chiper_teks = message_text.split(' ')[1:]
                chiper_teks = ' '.join(chiper_teks)
                plain_teks = vigenere.dekripsi(C=chiper_teks, K=kunci)
                bot.sendMessage(chat_id, plain_teks)
                set_chat_status(chat_id, 'normal')
            else:
                pesan = "Hey {}, kamu belum punya kunci. Kirim perintah /buatkunci untuk membuat kunci baru.".format(first_name)
                bot.sendMessage(chat_id, pesan)
                set_chat_status(chat_id, 'normal')

    elif 'text' in message:
        # Cek statusnya
        chat_id = message['chat']['id']
        chat_status = get_chat_status(chat_id)
        user_id = message['from']['id']
        first_name = message['from']['first_name']
        # Mengatur kuncinya
        if chat_status == 'menunggu_kunci':
            kunci = message['text']
            # Check kuncinya
            if kunci.isalpha():
                set_vigenere_key(user_id, kunci)
                chiper_teks = vigenere.enkripsi(P='pesan rahasia buat kamu',
                                                K=kunci)
                pesan = (
                    "Nice! Kunci Vigenere ciphernya berhasil diatur ke: *{}*\n\n"
                    "Sekarang kamu bisa melakukan enkripsi pesan dengan "
                    "cara mengirimkan perintah /enkripsi diikuti dengan "
                    "plain teks yang ingin di enkripsi. Contohnya "
                    "seperti ini:\n\n"
                    "/enkripsi pesan rahasia buat kamu\n\n"
                    "Lalu untuk dekripsinya menggunakan perintah /dekripsi "
                    "yang dikuti oleh chiper teks. Contohnya:\n\n"
                    "/dekripsi {}").format(kunci, chiper_teks)
                bot.sendMessage(chat_id, pesan, parse_mode='Markdown')
                set_chat_status(chat_id, 'normal')
            else:
                # Ingatkan jika kuncinya tidak valid
                pesan = "Hey {}, kunci yang kamu kirimkan tidak valid. Pastikan hanya huruf abjad aja ya, tanpa spasi, nomor dan simbol-simbol. Sekarang kirim kunci yang valid ya".format(first_name)
                bot.sendMessage(chat_id, pesan)
                set_chat_status(chat_id, 'menunggu_kunci')
    elif 'inline_message_id' in message:
        # Ketika user mengklik tombol dekripsi pada chat yang terenkripsi
        user_id = message['from']['id']
        user_firstname = message['from']['first_name']
        cipher_text = message['data']
        chat_id = '@{}'.format(message['from']['username'])

        # Cek apakah user udah punya kunci
        user_key = get_vigenere_key(user_id)
        if user_key:
            # Kirim hasil dekripsi ke personal chat
            plain_text = vigenere.dekripsi(C=cipher_text, K=user_key)
            pesan = (
                "Hey {name}, ini hasil dekripsinya menggunakan kunci {K}:\n"
                "\n{P}\n\n"
                "Kamu bisa merubah kuncinya menggunakan perintah /buatkunci."
                ).format(name=user_firstname, K=user_key, P=plain_text)
            bot.sendMessage(chat_id, pesan)
        else:
            pesan = "Hey {}, kamu belum punya kunci. Jadi belum bisa dekripsi pesan ini: \"{}\".\nKirim perintah /buatkunci untuk membuat kunci baru.".format(first_name, cipher_text)
            bot.sendMessage(chat_id, pesan)

    print("DEBUG: message:", message)

bot.message_loop(handler, source=update_queue)

@app.route('/telegram-webhook', methods=['GET', 'POST'])
def telegram_webhook():
    update_queue.put(request.data)
    return 'OK'

if __name__ == '__main__':
    bot.setWebhook(TELEGRAM_WEBHOOK_URL)
    app.run(host='0.0.0.0', debug=True, use_reloader=True)
