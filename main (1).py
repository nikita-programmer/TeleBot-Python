import os
import uuid
import sqlite3
import telebot
from post import post
from telebot import types
import re
import webbrowser
import shutil
from time import sleep

TOKEN = '6211543841:AAHGQAJFsnMQzz9SDiEgkX7nhhywM4y_ezw'
bot = telebot.TeleBot(TOKEN)
PHOTOS = 1  

print("Current working directory:", os.getcwd())

# Check if the folder 'product_photos' exists, create it if not
if not os.path.exists('product_photos'):
    print('Created new folder: product_photos')
    os.makedirs('product_photos')


def handle_media(message):
    # Check the type of media in the message and handle accordingly
    if message.content_type == 'photo':
        process_photo(message)


def process_photo(message):
    # If the message contains a media group, process each photo in the group
    if message.media_group_id is not None:
        for photo in message.photo:
            process_photo_save(photo, message)
    else:
        # If there is a single photo, process it
        process_photo_save(message.photo[-1], message)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data.startswith('delete_'):
        # Extract the name to delete from the callback data
        name_to_delete = callback.data[len('delete_'):]
        
        # Try to delete the data associated with the name
        if delete_data(name_to_delete):
            bot.send_message(callback.message.chat.id, f'Product "{name_to_delete}" successfully deleted.')
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
        else:
            bot.send_message(callback.message.chat.id, f'Error deleting product: "{name_to_delete}".')

    # Check if the callback data is 'edit'
    elif callback.data == 'edit':
        # Create an inline keyboard for editing options
        markup = types.InlineKeyboardMarkup()
        bt1 = types.InlineKeyboardButton('Name', callback_data='edit_name')
        bt2 = types.InlineKeyboardButton('Description', callback_data='edit_description')
        markup.row(bt1, bt2)
        
        # Ask the user what they would like to change
        bot.send_message(callback.message.chat.id, 'What would you like to change', parse_mode='html', reply_markup=markup)

    elif callback.data.startswith('publish_'):
        product_name = callback.data[len('publish_'):]
        product = get_product_by_name(product_name)
        photopath = get_product_photo_folder_path(product_name)
        if product:
            product_data = list(product)
            print(product_data)
            post(product_data[0], product_data[1], product_data[2], product_data[3], photopath)
            #sleep(10000)
            #confirm_post_button = types.InlineKeyboardButton("Confirm Post", callback_data=f"confirm_post_{product_name}")
            #markup = types.InlineKeyboardMarkup().add(confirm_post_button)
            bot.send_message(callback.message.chat.id, f'Listing {product_data[0]} succesful listed')
        else:
            bot.send_message(callback.message.chat.id, f'Error publishing product: "{product_name}".')

        bot.answer_callback_query(callback.id)  # Отвечаем на callback-запрос



    elif callback.data == 'edit_name':
        # Handling edit name callback, prompting user for a new name
        bot.send_message(callback.message.chat.id, 'Put in the new name of the product:')
        bot.register_next_step_handler(callback.message, save_new_name)

    elif callback.data == 'edit_description':
        # Handling edit description callback, prompting user for a new description
        bot.send_message(callback.message.chat.id, 'Put in the new description of the product:')
        bot.register_next_step_handler(callback.message, save_new_description)

    elif callback.data == 'new':
        # Handling new callback, creating a new product
        create_new(callback.message)

    bot.answer_callback_query(callback.id)  # Answer the callback query

@bot.message_handler(func=lambda message: True)
def on_start_button(message):
    # Handle messages with the ReplyKeyboardMarkup

    # Create a custom keyboard with three buttons
    markup = types.ReplyKeyboardMarkup()
    bt1 = types.KeyboardButton('Create New')
    bt2 = types.KeyboardButton('/site')
    bt3 = types.KeyboardButton('/help')
    markup.row(bt1)
    markup.row(bt2, bt3)

    # Call the on_start function with the provided message and custom keyboard markup
    on_start(message, markup)


@bot.message_handler(commands=['info', 'site', 'help', 'id', 'Hi', 'start', 'hello', 'Создать новое', 'read', 'Привет'])
def on_start(message, markup):
    # Handle commands
    
    if message.text.startswith('/'):
        if message.text == '/info':
            # Respond to /info command
            bot.send_message(message.chat.id, str(message), reply_markup=markup)

        elif message.text == '/site':
            # Respond to /site command and open a website
            bot.send_message(message.chat.id, 'Website is open', reply_markup=markup)
            webbrowser.open(url='https://www.google.com/')

        elif message.text == '/help':
            # Respond to /help command with help information
            helps = '⚠️<b>HELP:</b>\n <u>Functions of bot:</u> You can send the bot photos and videos, and it will evaluate them!\nAlso, you can post an ad using this bot.'
            bot.send_message(message.chat.id, helps, parse_mode='html', reply_markup=markup)

        elif message.text == '/id':
            # Respond to /id command with user ID
            bot.reply_to(message, f'ID: {message.from_user.id}', reply_markup=markup)

        elif message.text == '/Hi' or message.text == '/start' or message.text == 'hello':
            # Respond to greetings commands
            hi = f'Привет, {message.from_user.first_name} {message.from_user.username} 😊'
            bot.send_message(message.chat.id, hi, reply_markup=markup)

        elif message.text == '/read':
            # Respond to /read command and display all created lots
            bot.send_message(message.chat.id, '<b>All lots created</b>', parse_mode='html', reply_markup=markup)
            read_products(message)

        else:
            # Respond to unknown command
            response = "The given command does not exist. Enter /help to find out what I can do."
            bot.send_message(message.chat.id, response, reply_markup=markup)
    else:
     
        if message.text == 'Create New':
            # Respond to the 'Create New' button by prompting the user to input the name of the product
            bot.send_message(message.chat.id, 'Put in the name of the product:', reply_markup=markup)
            bot.register_next_step_handler(message, save_name)

        elif message.text == 'Hello' or message.text == 'hi' or message.text == 'Hi' or message.text == 'hello':
            # Respond to greetings and suggest using /help for more information
            bot.send_message(message.chat.id, 'Hi, would you like to find out what I can do \n/help', reply_markup=markup)

        else:
            # Respond to unknown non-command messages
            response = "At the moment, I do not know how to reply to this. Type /help to find out what I can do."
            bot.send_message(message.chat.id, response, reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def create_new(message):
    # Handling the creation of a new product
    bot.send_message(message.chat.id, 'Put in the name of the product:')
    bot.register_next_step_handler(message, save_name)


def save_name(message):
    # Saving the name of the product
    name = message.text
    bot.send_message(message.chat.id, f'Name of product saved: {name}')
    bot.send_message(message.chat.id, 'Put in the price of the product: ')
    bot.register_next_step_handler(message, save_price, name)


def contains_letters(text):
    # Check if the given text contains letters
    pattern = re.compile('[a-zA-Zа-яА-Я]')
    return bool(pattern.search(text))


def save_price(message, name):
    # Saving the price of the product
    price = message.text.strip()  # Remove leading and trailing spaces
    if not price:
        bot.send_message(message.chat.id, 'Error, price cannot be empty. Put in the name of the product:')
        bot.register_next_step_handler(message, save_price, name)
    elif not price.isdigit() and contains_letters(price):
        bot.send_message(message.chat.id, 'Error, the price cannot contain letters')
        bot.register_next_step_handler(message, save_price, name)
    else:
        bot.send_message(message.chat.id, f'Price of product saved: {price}')
        bot.send_message(message.chat.id, 'Put in the description of the product:')
        bot.register_next_step_handler(message, save_description, name, price)

def save_description(message, name, price):
    # Handling the saving of product description
    description = message.text
    print(f"DEBUG: scan: {name} | {price} | {description}")
    bot.send_message(message.chat.id, f'Description saved: {description}')

    # Creating a custom keyboard for selecting the condition of the product
    markup = types.ReplyKeyboardMarkup()
    bt1 = types.KeyboardButton('New')
    bt2 = types.KeyboardButton('Used – like new')
    bt3 = types.KeyboardButton('Used – good')
    bt4 = types.KeyboardButton('Used – fair')
    markup.row(bt1, bt2)
    markup.row(bt3, bt4)
    
    # Asking the user to select the condition of the product
    bot.send_message(message.chat.id, 'Select the condition of the product', reply_markup=markup)
    
    # Registering the next step handler for condition selection
    bot.register_next_step_handler(message, condition_select, name, price, description)


def condition_select(message, name, price, description):
    # Handling the user's selection of the product condition
    if message.text == 'New':
        condition = 'New'
        send_photos(message, name, price, description, condition)
    elif message.text == 'Used – like new':
        condition = 'Used – like new'
        send_photos(message, name, price, description, condition)
    elif message.text == 'Used – good':
        condition = 'Used – good'
        send_photos(message, name, price, description, condition)
    elif message.text == 'Used – fair':
        condition = 'Used – fair'
        send_photos(message, name, price, description, condition)
    else:
        # Handling an incorrect condition selection
        print(f"DEBUG: save: error: no correct condition: name: {name}")
        markup = types.InlineKeyboardMarkup()
        bt1 = types.InlineKeyboardButton('Create new', callback_data='new')
        markup.row(bt1)
        bot.send_message(message.chat.id, 'The request was not created because the status needs to be selected from the buttons on the keyboard', reply_markup=markup)


def send_photos(message, name, price, description, condition):
    # Handling the sending of product photos
    print(f"DEBUG: save: {name} | {price} | {description} | {condition}")
    
    # Saving the data to a database or any other storage
    save_data(name, price, condition, description)
    
    # Asking the user to send photos of the product
    bot.send_message(message.chat.id,
                     'Now send photos of the product (send one photo at a time).\nWhen you finish, type /done.')
    
    # Registering the next step handler for photo saving
    bot.register_next_step_handler(message, save_photos, name, price, condition, description)


def save_photos(message, name, price, condition, description, photos=[]):
    # Handling the saving of product photos
    
    if message.content_type == 'photo':
        # If the message contains a photo, save it
        photo = message.photo[-1]
        file_id = photo.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        project_root = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(project_root, 'product_photos', name)
        
        # Create the folder if it does not exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        # Save the photo with a unique filename
        filename = os.path.join(folder_path, f"{uuid.uuid4()}.jpg")
        with open(filename, 'wb') as new_file:
            new_file.write(downloaded_file)

        print(f"DEBUG: Photo saved: {filename}")
        
        # Inform the user that the photo is saved, and ask for the next photo or /done
        bot.send_message(message.chat.id, 'The photo is saved. Send the next photo or type /done.')
        photos.append(filename)
        
        # Register the next step handler for the next photo or /done
        bot.register_next_step_handler(message, save_photos, name, price, condition, description)

    elif message.text == '/done':
        # If the user types /done, check if any photos were saved and provide feedback
        if len(photos) > 0:
            bot.send_message(message.chat.id, 'All photos are saved.\nTo view the products, press /read.')
        else:
            bot.send_message(message.chat.id, 'You have not uploaded any photos. The ad is not created.')

    else:
        # If the user sends a message other than /done or a photo, inform about the error
        bot.send_message(message.chat.id, 'Error! Send a photo or type /done.')

def process_photo_save(photo, name, chat_id):
    # Process and save a photo for a given product
    file_id = photo.file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    project_root = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(project_root, 'product_photos', name)
    
    # Create the folder if it does not exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Save the photo with a unique filename
    filename = os.path.join(folder_path, f"{uuid.uuid4()}.jpg")
    with open(filename, 'wb') as new_file:
        new_file.write(downloaded_file)

    print(f"DEBUG: Photo saved: {filename}")
    
    # Inform the user that the photos are saved, and provide a way to view the products
    bot.send_message(chat_id, 'The photos are saved.\nTo view the products, press /read.')


def save_data(name, price, condition, description):
    # Save product data to a database
    conn = sqlite3.connect('products.db')
    cur = conn.cursor()
    try:
        cur.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price TEXT, condition TEXT, description TEXT)')
        cur.execute('INSERT INTO products (name, price, condition, description) VALUES (?, ?, ?, ?)',
                    (name, price, condition, description))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error saving data: {e}")
        return f"Error saving data: {e}"
    finally:
        cur.close()
        conn.close()


def delete_data(name_to_delete):
    # Delete product data and associated photos from the database and file system
    conn = sqlite3.connect('products.db')
    cur = conn.cursor()

    try:
        cur.execute('DELETE FROM products WHERE name = ?', (name_to_delete,))
        conn.commit()
        project_root = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(project_root, 'product_photos', name_to_delete)
        
        # Remove the folder and its contents if it exists
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

        return True
    except sqlite3.Error as e:
        print(f"Error deleting product: {e}")
        return False
    finally:
        cur.close()
        conn.close()


def product_photos(product_id):
    # Retrieve the file paths of photos associated with a product
    photos = []
    project_root = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(project_root, 'product_photos', product_id)
    
    # If the folder exists, collect file paths of photos
    if os.path.exists(folder_path):
        photos = [os.path.join(folder_path, name) for name in os.listdir(folder_path) if name.endswith(".jpg")]
    return photos

# ...

def read_products(message):
    # Retrieve and display information about saved products
    products = fetch_data()

    if products:
        for i, product in enumerate(products, start=1):
            name = product[0]
            price = product[1]
            condition = product[2]
            description = product[3]
            photos = product_photos(name)
            
            # Display basic information about the product
            product_info = f'<b>{i} | Product:</b>\n<b>Name:</b> {name}\n<b>Price:</b> {price}£\n<b>Condition:</b> {condition}'
            
            if photos:
                # If the product has photos, send a media group with photos
                bot.send_message(message.chat.id, product_info, parse_mode='html')
                photo_caption = f""
                media = []
                
                for photo_filename in photos:
                    with open(photo_filename, 'rb') as photo_file:
                        media.append(types.InputMediaPhoto(media=photo_file.read(), caption=photo_caption, parse_mode='html'))
                
                bot.send_media_group(message.chat.id, media)
                markup_read(message, name, description)
            else:
                # If the product has no photos, send a simple message
                bot.send_message(message.chat.id, product_info, parse_mode='html')
                bot.send_message(message.chat.id, 'This product does not have photos')
                markup_read(message, name, description)
    else:
        # If there are no saved products, provide an option to create a new one
        markup = types.InlineKeyboardMarkup()
        bt1 = types.InlineKeyboardButton('Create new', callback_data='new')
        markup.row(bt1)
        bot.send_message(message.chat.id, 'Do not have saved products, would you like to create a new one', reply_markup=markup)


def markup_read(message, name, description):
    markup = types.InlineKeyboardMarkup()
    bt1 = types.InlineKeyboardButton('Delete', callback_data=f'delete_{name}')
    bt2 = types.InlineKeyboardButton('Change', callback_data=f'edit_{name}')  # Добавляем уникальный идентификатор
    bt3 = types.InlineKeyboardButton('Publish', callback_data=f'publish_{name}')  # Добавляем уникальный идентификатор
    markup.row(bt1, bt2, bt3)
    bot.send_message(message.chat.id, f'<b>Description:</b> {description}', reply_markup=markup, parse_mode='html')



def fetch_data():
    # Retrieve product information from the database
    conn = sqlite3.connect('products.db')
    cur = conn.cursor()
    try:
        cur.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price TEXT, condition TEXT, description TEXT)')
        cur.execute('SELECT name, price, condition, description FROM products')
        rows = cur.fetchall()
        return rows
    except sqlite3.Error as e:
        print(f"Error getting information: {e}")
        return None
    finally:
        cur.close()
        conn.close()

# Add more functions or code as needed

 # Assuming you have the 'telebot' library imported

# Define a function to extract product data from message text
def fetch_product_data(message_text):
    # Use regular expressions to search for specific patterns in the message text
    name_match = re.search(r'Name: (.+)', message_text)
    description_match = re.search(r'Description: (.+)', message_text)
    price_match = re.search(r'Price: (.+)', message_text)
    condition_match = re.search(r'Condition: (.+)', message_text)

    # Check if all required information is found in the message text
    if name_match and description_match and price_match and condition_match:
        # Extract values from the regular expression matches
        name = name_match.group(1)
        description = description_match.group(1)
        price = price_match.group(1)
        condition = condition_match.group(1)
        return name, description, price, condition
    else:
        # If any required information is missing, return None for each field
        return None, None, None, None


def get_product_photo_folder_path(product_name):
    # Get the absolute path of the current script
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Construct the folder path for the product photos
    folder_path = os.path.join(script_directory, 'product_photos', product_name)

    # Check if the folder exists
    if os.path.exists(folder_path):
        return folder_path
    else:
        return None

def get_product_by_name(product_name):
    # Получаем get о продукте из базы данных по его имени
    conn = sqlite3.connect('products.db')
    cur = conn.cursor()
    
    try:
        cur.execute('SELECT name, description, price, condition FROM products WHERE name = ?', (product_name,))
        product = cur.fetchone()
        print(product)
        return product
    except sqlite3.Error as e:
        print(f"Error getting product information: {e}")
        return None
    finally:
        cur.close()
        conn.close()

# Check if the script is run as the main module
if __name__ == '__main__':
    # Start the polling of the Telegram bot
    bot.polling()

