import telebot
from categories import categories
print("Bot-Starting")


class Cat:
    def __init__(self):
        self.TOKEN = '6211543841:AAHGQAJFsnMQzz9SDiEgkX7nhhywM4y_ezw'
        self.my_bot = telebot.TeleBot(self.TOKEN)
        self.selected_category = {}
        self.user_state = {}
        self.categories = categories
        self.fully_cat = [1 for _ in range(len(categories))]
        

    def generate_keyboard(self, category_dict):
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        buttons = [telebot.types.KeyboardButton(text=key) for key in category_dict.keys()]
        keyboard.add(*buttons)
        return keyboard

    def start(self, message):
        self.user_state[message.chat.id] = categories
        self.fully_cat.clear()
        self.my_bot.send_message(message.chat.id, 'Available Categories:', reply_markup=self.generate_keyboard(categories))

    def handle_categories(self, message):
        selected_category = message.text
        subcategories = self.user_state[message.chat.id][selected_category]

        if subcategories:
            self.user_state[message.chat.id] = subcategories
            self.fully_cat.append(selected_category)
            self.my_bot.send_message(message.chat.id, 'Available Subcategories:', reply_markup=self.generate_keyboard(subcategories))
        else:
            self.fully_cat.append(selected_category)
            num_categories = len(self.fully_cat)

            if num_categories == 3:
                var1 = self.fully_cat[0]
                var2 = self.fully_cat[1]
                var3 = self.fully_cat[2]

                self.my_bot.send_message(message.chat.id, f'Selected categories: {var1} => {var2} => {var3}')

            elif num_categories == 2:
                var1 = self.fully_cat[0]
                var2 = self.fully_cat[1]

                self.my_bot.send_message(message.chat.id, f'Selected categories: {var1} => {var2}')
            else:
                self.my_bot.send_message(message.chat.id, f'Selected categories: ERROR')

    def run(self):
        @self.my_bot.message_handler(func=lambda message: message.text in self.user_state.get(message.chat.id, self.fully_cat))
        def handle_categories_wrapper(message):
            self.handle_categories(message)


        @self.my_bot.message_handler(commands=['start'])
        def start_wrapper(message):
            self.start(message)

       

        self.my_bot.polling()

if __name__ == "__main__":
    my_bot_instance = Cat()
    my_bot_instance.run()