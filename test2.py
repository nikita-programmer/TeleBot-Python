import os
import telebot
from telebot import types
import webbrowser
import categories

class Start:
    def __init__(self):
        self.TOKEN = '6211543841:AAHGQAJFsnMQzz9SDiEgkX7nhhywM4y_ezw'
        self.my_bot = telebot.TeleBot(self.TOKEN)
        self.categories = categories.categories

        @self.my_bot.message_handler(commands=['start'])
        def handle_start(message):
            user_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            user_markup.row('/site', '/help')
            user_markup.row('Создать новое')
            
            self.my_bot.send_message(message.from_user.id, "Привет! Я бот. Чем могу помочь?", reply_markup=user_markup)
            self.my_bot.register_next_step_handler(message, additional_function)

        def additional_function(message):           
            self.my_bot.send_message(message.from_user.id, "Вы вызвали дополнительную функцию!")

        self.my_bot.polling()

if __name__ == "__main__":
    my_bot_instance = Start()
    my_bot_instance.run()
