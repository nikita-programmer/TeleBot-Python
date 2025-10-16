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
        self.bot = telebot.TeleBot(self.TOKEN)
        self.categories = categories.categories
        self.selected_category = {}
        self.user_state = {}
        self.fully_cat = [1 for i in range(len(categories))]
        self.PHOTOS = 1

        print("Current working directory:", os.getcwd())
        if not os.path.exists('product_photos'):
            print('Created new folder: product_photos')
            os.makedirs('product_photos')


        def handle_media(message):
            if message.content_type == 'photo':
                process_photo(message)


        def process_photo(message):
            if message.media_group_id is not None:
                for photo in message.photo:
                    process_photo_save(photo, message)
            else:
                process_photo_save(message.photo[-1], message)
    
    def run(self):
        self.bot.polling()

    


class Log:
    @Start.bot.callback_query_handler(func=lambda callback: True)
    def callback_message(callback):
        if callback.data.startswith('delete_'):
            name_to_delete = callback.data[len('delete_'):]
            if delete_data(name_to_delete):
                bot.send_message(callback.message.chat.id, f'Товар "{name_to_delete}" успешно удален.')
                bot.delete_message(callback.message.chat.id, callback.message.message_id)
            else:
                bot.send_message(callback.message.chat.id, f'Ошибка при удалении товара "{name_to_delete}".')

        elif callback.data == 'edit':
            markup = types.InlineKeyboardMarkup()
            bt1 = types.InlineKeyboardButton('Название', callback_data='edit_name')
            bt2 = types.InlineKeyboardButton('Описание', callback_data='edit_description')
            markup.row(bt1, bt2)
            bot.send_message(callback.message.chat.id, 'Что вы хотите изменить?', parse_mode='html', reply_markup=markup)

        elif callback.data.startswith('publish_'):
            product_name = callback.data[len('publish_'):]
            product = get_product_by_name(product_name)
            photopath = get_product_photo_folder_path(product_name)
            if product:
                product_data = list(product)
                print(product_data)
                post(product_data[0], product_data[1], product_data[2], product_data[3], photopath)
                bot.send_message(callback.message.chat.id, f'Listing {product_data[0]} successful listed')
            else:
                bot.send_message(callback.message.chat.id, f'Error publishing product: "{product_name}".')
            bot.answer_callback_query(callback.id)  # Отвечаем на callback-запрос

        elif callback.data == 'edit_name':
            bot.send_message(callback.message.chat.id, 'Введите новое название товара:')
            bot.register_next_step_handler(callback.message, save_new_name)

        elif callback.data == 'edit_description':
            bot.send_message(callback.message.chat.id, 'Введите новое описание товара:')
            bot.register_next_step_handler(callback.message, save_new_description)

        elif callback.data == 'new':
            create_new(callback.message)

        bot.answer_callback_query(callback.id)


class Button:
    @Start.bot.message_handler(func=lambda message: True)
    def on_start_button(message):
        markup = types.ReplyKeyboardMarkup()
        bt1 = types.KeyboardButton('Создать новое')
        bt2 = types.KeyboardButton('/site')
        bt3 = types.KeyboardButton('/help')
        markup.row(bt1)
        markup.row(bt2, bt3)
        on_start(message, markup)


class Commands:
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


class Mainnp:
    @Start.bot.message_handler(func=lambda message: True)
    def create_new(message):
        bot.send_message(message.chat.id, 'Введите название товара:')
        bot.register_next_step_handler(message, save_name)

    def save_name(message):
        name = message.text
        bot.send_message(message.chat.id, f'Название товара сохранено: {name}')
        bot.send_message(message.chat.id, 'Введите цену товара:')
        bot.register_next_step_handler(message, save_price, name)

    def contains_letters(text):
        pattern = re.compile('[a-zA-Zа-яА-Я]')
        return bool(pattern.search(text))

    def save_price(message, name):
        price = message.text.strip()  # -пробелы

        if not price:
            bot.send_message(
                message.chat.id,
                'Ошибка! Цена не может быть пустой. Введите цену товара:')
            bot.register_next_step_handler(message, save_price, name)
        elif not price.isdigit() and contains_letters(price):
            bot.send_message(
                message.chat.id,
                'Ошибка! Цена должна быть числом без букв. Введите цену товара:')
            bot.register_next_step_handler(message, save_price, name)
        else:
            bot.send_message(message.chat.id, f'Цена товара сохранена: {price}')
            bot.register_next_step_handler(message, save_category, name, price)


class Mainc:
    def save_category(message, name, price):
        user_state[message.chat.id] = categories
        fully_cat.clear()
        bot.send_message(message.chat.id,
                         'Chose the categories:',
                         reply_markup=generate_keyboard(categories))
        bot.register_next_step_handler(message, handle_categories, name, price)

    def generate_keyboard(category_dict):
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1,
                                                     resize_keyboard=True)
        buttons = [
            telebot.types.KeyboardButton(text=key) for key in category_dict.keys()
        ]
        keyboard.add(*buttons)
        return keyboard

    @Start.bot.message_handler(func=lambda message: message.text in user_state.get(
        message.chat.id, fully_cat))
    def handle_categories(message, name, price):
        selected_category = message.text
        subcategories = user_state.get(message.chat.id, {}).get(selected_category)

        if subcategories:
            fully_cat.append(selected_category)
            bot.send_message(message.chat.id,
                             'Available Subcategories:',
                             reply_markup=generate_keyboard(subcategories))
        else:
            fully_cat.append(selected_category)
            num_categories = len(fully_cat)
            if num_categories == 3:
                var1 = fully_cat[0]
                var2 = fully_cat[1]
                var3 = fully_cat[2]
                bot.send_message(message.chat.id,
                                 f'Selected categories: {var1} => {var2} => {var3}')
                bot.register_next_step_handler(message, save_description, name, price)
            elif num_categories == 2:
                var1 = fully_cat[0]
                var2 = fully_cat[1]
                bot.send_message(message.chat.id,
                                 f'Selected categories: {var1} => {var2} ')
                bot.send_message(message.chat.id, 'Введите описание товара:')
                bot.register_next_step_handler(message, save_description, name, price)
            else:
                bot.send_message(message.chat.id, f'Selected categories: ERROR')




class Main:
    def save_description(message, name, price):
        description = message.text
        print(f"DEBUG: scan: {name} | {price} | {description}")
        bot.send_message(message.chat.id, f'Описание товара сохранено: {description}')
        markup = types.ReplyKeyboardMarkup()
        bt1 = types.KeyboardButton('Новый товар')
        bt2 = types.KeyboardButton('Б/у в идеальном состоянии')
        bt3 = types.KeyboardButton('Б/у в хорошем состоянии')
        bt4 = types.KeyboardButton('Б/у в удовлетворительном состоянии')
        markup.row(bt1, bt2)
        markup.row(bt3, bt4)
        bot.send_message(message.chat.id, 'Выберите состояние товара:', reply_markup=markup)
        
        bot.register_next_step_handler(message, condition_select, name, price, description)


    def condition_select(message, name, price, description):
        if message.text == 'Новый товар':
            condition = 'Новый товар'
            send_photos(message, name, price, description, condition)
        elif message.text == 'Б/у в идеальном состоянии':
            condition = 'Б/у в идеальном состоянии'
            send_photos(message, name, price, description, condition)
        elif message.text == 'Б/у в хорошем состоянии':
            condition = 'Б/у в хорошем состоянии'
            send_photos(message, name, price, description, condition)
        elif message.text == 'Б/у в удовлетворительном состоянии':
            condition = 'Б/у в удовлетворительном состоянии'
            send_photos(message, name, price, description, condition)
        else:
            print(f"DEBUG: save: error: no correct condition: name: {name}")
            markup = types.InlineKeyboardMarkup()
            bt1 = types.InlineKeyboardButton('Создать новое', callback_data='new')
            markup.row(bt1)
            bot.send_message(
                message.chat.id,
                'Объявление не создано так как состояние нужно выбирать из кнопок на клавиатуре ⌨️',
                reply_markup=markup)


    def send_photos(message, name, price, description, condition):
        print(f"DEBUG: save: {name} | {price} | {description} | {condition}")
        save_data(name, price, condition, description)
        bot.send_message(
            message.chat.id,
            'Теперь пришлите фотографии товара (отправьте по одной фотографии каждый раз).\nКогда закончите, напишите /done:'
        )
        bot.register_next_step_handler(message, save_photos, name, price, condition, description)


    def save_photos(message, name, price, condition, description, photos=[]):
        if message.content_type == 'photo':
            photo = message.photo[-1]
            file_id = photo.file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            project_root = os.path.dirname(os.path.abspath(__file__))
            folder_path = os.path.join(project_root, 'product_photos', name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            filename = os.path.join(folder_path, f"{uuid.uuid4()}.jpg")
            with open(filename, 'wb') as new_file:
                new_file.write(downloaded_file)

            print(f"DEBUG: Photo saved: {filename}")
            bot.send_message(
                message.chat.id,
                'Фотография сохранена. Отправьте следующую фотографию или напишите /done:'
            )
            photos.append(filename)
            bot.register_next_step_handler(message, save_photos, name, price, condition, description)

        elif message.text == '/done':
            if len(photos) > 0:
                bot.send_message(
                    message.chat.id,
                    'Все фотографии сохранены.\nДля просмотра товаров нажмите /read.')
            else:
                bot.send_message(
                    message.chat.id,
                    'Вы не загрузили ни одной фотографии. Объявление не создано.')

        else:
            bot.send_message(message.chat.id, 'Ошибка! Отправьте фотографию или напишите /done.')

    def process_photo_save(photo, name, chat_id):
        file_id = photo.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        project_root = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(project_root, 'product_photos', name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        filename = os.path.join(folder_path, f"{uuid.uuid4()}.jpg")
        with open(filename, 'wb') as new_file:
            new_file.write(downloaded_file)

        print(f"DEBUG: Photo saved: {filename}")
        bot.send_message(
            chat_id, 'Фотографии сохранены\nДля просмотра товаров нажмите\n /read')   


    def save_data(name, price, condition, description):
        conn = sqlite3.connect('products.db')
        cur = conn.cursor()
        try:
            cur.execute(
                'CREATE TABLE IF NOT EXISTS products (name TEXT, price TEXT, condition TEXT, description TEXT)'
            )
            cur.execute(
                'INSERT INTO products (name, price, condition, description) VALUES (?, ?, ?, ?)',
                (name, price, condition, description))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при сохранении данных: {e}")
            return f"Ошибка при сохранении данных: {e}"
        finally:
            cur.close()
            conn.close()


    def delete_data(name_to_delete):
        conn = sqlite3.connect('products.db')
        cur = conn.cursor()

        try:
            cur.execute('DELETE FROM products WHERE name = ?', (name_to_delete, ))
            conn.commit()
            project_root = os.path.dirname(os.path.abspath(__file__))
            folder_path = os.path.join(project_root, 'product_photos', name_to_delete)
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)

            return True
        except sqlite3.Error as e:
            print(f"Ошибка при удалении товара: {e}")
            return False
        finally:
            cur.close()
            conn.close()


    def product_photos(product_id):
        photos = []
        project_root = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(project_root, 'product_photos', product_id)
        if os.path.exists(folder_path):
            photos = [
                os.path.join(folder_path, name) for name in os.listdir(folder_path)
                if name.endswith(".jpg")
            ]
        return photos


    def read_products(message):
        products = fetch_data()

        if products:
            for i, product in enumerate(products, start=1):
                name = product[0]
                price = product[1]
                condition = product[2]
                description = product[3]
                photos = product_photos(name)
                product_info = f'<b>{i} | Объявление:</b>\n<b>Название:</b> {name}\n<b>Цена:</b> {price}£\n<b>Состояние:</b> {condition}'
                if photos:
                    bot.send_message(message.chat.id, product_info, parse_mode='html')
                    photo_caption = f""
                    media = []
                    for photo_filename in photos:
                        with open(photo_filename, 'rb') as photo_file:
                            media.append(
                                types.InputMediaPhoto(media=photo_file.read(),
                                                      caption=photo_caption,
                                                      parse_mode='html'))
                    bot.send_media_group(message.chat.id, media)
                    markup_read(message, name, description)
                else:
                    bot.send_message(message.chat.id, product_info, parse_mode='html')
                    bot.send_message(message.chat.id, 'У этого товара нет фотографий.')
                    markup_read(message, name, description)
        else:
            markup = types.InlineKeyboardMarkup()
            bt1 = types.InlineKeyboardButton('Создать новое', callback_data='new')
            markup.row(bt1)
            bot.send_message(message.chat.id,
                             'Нет сохраненных товаров. Хотите создать новый?',
                             reply_markup=markup)


    def markup_read(message, name, description):
        markup = types.InlineKeyboardMarkup()
        bt1 = types.InlineKeyboardButton('Удалить', callback_data=f'delete_{name}')
        bt2 = types.InlineKeyboardButton('Изменить', callback_data='edit')
        bt3 = types.InlineKeyboardButton('Выложить', callback_data='publish')
        markup.row(bt1, bt2, bt3)
        bot.send_message(message.chat.id,
                         f'<b>Описание:</b> {description}',
                         reply_markup=markup,
                         parse_mode='html')


    def fetch_data():
        conn = sqlite3.connect('products.db')
        cur = conn.cursor()
        try:
            cur.execute(
                'CREATE TABLE IF NOT EXISTS products (name TEXT, price TEXT, condition TEXT, description TEXT)'
            )
            cur.execute('SELECT name, price, condition, description FROM products')
            rows = cur.fetchall()
            return rows
        except sqlite3.Error as e:
            print(f"Ошибка при получении данных: {e}")
            return None
        finally:
            cur.close()
            conn.close()


    def fetch_product_data(message_text):
        name_match = re.search(r'Название: (.+)', message_text)
        description_match = re.search(r'Описание: (.+)', message_text)
        price_match = re.search(r'Цена: (.+)', message_text)
        condition_match = re.search(r'Состояние: (.+)', message_text)

        if name_match and description_match and price_match and condition_match:
            name = name_match.group(1)
            description = description_match.group(1)
            price = price_match.group(1)
            condition = condition_match.group(1)
            return name, description, price, condition
        else:
            return None, None, None, None


    

if __name__ == "__main__":
    my_bot = Start()
    my_bot.run()


    my_bot = Start()
    my_bot = Log()
    my_bot = Button()
    my_bot = Commands()
    my_bot = Mainnp()
    my_bot = Mainc()
    my_bot = Main()
    my_bot.bot.polling()