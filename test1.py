import os
import uuid
import sqlite3
import telebot
from telebot import types
import re
import webbrowser
import shutil

from telebot import handler_backends
import categories


class Start:
    def __init__(self):
        self.TOKEN = '6211543841:AAHGQAJFsnMQzz9SDiEgkX7nhhywM4y_ezw'
        self.my_bot = telebot.TeleBot(self.TOKEN)
        self.categories = categories.categories
        self.selected_category = {}
        self.user_state = {}
        self.fully_cat = [1 for _ in range(len(categories.categories))]
        self.PHOTOS = 1

    print("Current working directory:", os.getcwd())
    if not os.path.exists('product_photos'):
        print('Created new folder: product_photos')
        os.makedirs('product_photos')



    def handle_media(self, message):
        if message.content_type == 'photo':
            self.process_photo(message)


    def process_photo(self, message):
        if message.media_group_id is not None:
            for photo in message.photo:
                self.process_photo_save(photo, message)
        else:
                self.process_photo_save(message.photo[-1], message)


        

    def callback_message(self, callback):
        if callback.data.startswith('delete_'):
            name_to_delete = callback.data[len('delete_'):]
            if self.delete_data(name_to_delete):
                self.bot.send_message(callback.message.chat.id, f'Товар "{name_to_delete}" успешно удален.')
                self.bot.delete_message(callback.message.chat.id, callback.message.message_id)
            else:
                self.bot.send_message(callback.message.chat.id, f'Ошибка при удалении товара "{name_to_delete}".')

        elif callback.data == 'edit':
            markup = types.InlineKeyboardMarkup()
            bt1 = types.InlineKeyboardButton('Название', callback_data='edit_name')
            bt2 = types.InlineKeyboardButton('Описание', callback_data='edit_description')
            markup.row(bt1, bt2)
            self.bot.send_message(callback.message.chat.id, 'Что вы хотите изменить?', parse_mode='html', reply_markup=markup)
            
        elif callback.data.startswith('publish_'):
            product_name = callback.data[len('publish_'):]
            product = self.get_product_by_name(product_name)
            photopath = self.get_product_photo_folder_path(product_name)
            if product:
                product_data = list(product)
                print(product_data)
                self.post(product_data[0], product_data[1], product_data[2], product_data[3], photopath)
                self.bot.send_message(callback.message.chat.id, f'Listing {product_data[0]} successful listed')
            else:
                self.bot.send_message(callback.message.chat.id, f'Error publishing product: "{product_name}".')
            self.bot.answer_callback_query(callback.id)  # Отвечаем на callback-запрос

        elif callback.data == 'edit_name':
            self.bot.send_message(callback.message.chat.id, 'Введите новое название товара:')
            self.bot.register_next_step_handler(callback.message, save_new_name)

        elif callback.data == 'edit_description':
            self.bot.send_message(callback.message.chat.id, 'Введите новое описание товара:')
            self.bot.register_next_step_handler(callback.message, save_new_description)

        elif callback.data == 'new':
            self.create_new(callback.message)

        self.bot.answer_callback_query(callback.id)


        
    
    def on_start_button(message):
        markup = types.ReplyKeyboardMarkup()
        bt1 = types.KeyboardButton('Создать новое')
        bt2 = types.KeyboardButton('/site')
        bt3 = types.KeyboardButton('/help')
        markup.row(bt1)
        markup.row(bt2, bt3)
        


    def on_start(self, message, markup):
        if message.text.startswith('/'):
            if message.text == '/info':
                self.bot.send_message(message.chat.id, str(message), reply_markup=markup)

            elif message.text == '/site':
                self.bot.send_message(message.chat.id, 'Website is open', reply_markup=markup)
                webbrowser.open(url='https://www.youtube.com/channel/UCW4OwywfIvGvyrGmV3TWDgA')

            elif message.text == '/help':
                helps = '⚠️<b>HELP:</b>\n <u>Функции бота:</u> можно отправить ему фото, видео, и он их оценит! (Временно не работает)\n Так же вы можете выложить обьявление с помощью етого бота \n(В разработке)'
                self.bot.send_message(message.chat.id, helps, parse_mode='html', reply_markup=markup)

            elif message.text == '/id':
                self.bot.reply_to(message, f'ID: {message.from_user.id}', reply_markup=markup)

            elif message.text == '/Hi' or message.text == '/start' or message.text == 'hello':
                hi = f'Привет, {message.from_user.first_name} {message.from_user.username} 😊'
                self.bot.send_message(message.chat.id, hi, reply_markup=markup)

            elif message.text == '/read':
                self.bot.send_message(message.chat.id, '<b>Все ранее созданные лоты:</b>', parse_mode='html', reply_markup=markup)
                self.read_products(message)

            else:
                response = "Данной команды не существует. Введите /help, чтобы узнать что я умею."
                self.bot.send_message(message.chat.id, response, reply_markup=markup)
        else:
            if message.text == 'Создать новое':
                self.bot.send_message(message.chat.id, 'Введите название товара:', reply_markup=markup)
                self.bot.register_next_step_handler(message, self.save_name)

            elif message.text == 'Привет' or message.text == 'привет' or message.text == 'Hi' or message.text == 'Hello':
                self.bot.send_message(message.chat.id, 'Привет  хочешь узнать что я умею? \n/help', reply_markup=markup)

            else:
                response = "Пока что не знаю как на это ответить. Введите /help что бы узнать что я умею."
                self.bot.send_message(message.chat.id, response, reply_markup=markup)
    
    def run(self):
        @self.my_bot.message_handler(func=lambda message: True)
        def on_start_wrapper(message):
            self.on_start(message)


        @self.my_bot.callback_query_handler(func=lambda callback: True)
        def callback_message_wrapper(message):
            self.callback_message(message)

    
        self.my_bot.polling()


if __name__ == "__main__":
    my_bot_instance = Start()
    my_bot_instance.run()