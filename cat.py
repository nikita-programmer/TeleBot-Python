
import telebot
import categories

categories = categories.categories

bot = telebot.TeleBot('6211543841:AAHGQAJFsnMQzz9SDiEgkX7nhhywM4y_ezw')

selected_category = {}
user_state = {}
fully_cat = [1 for i in range(len(categories))]


def generate_keyboard(category_dict):
  keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1,
                                               resize_keyboard=True)
  buttons = [
      telebot.types.KeyboardButton(text=key) for key in category_dict.keys()
  ]
  keyboard.add(*buttons)
  return keyboard


@bot.message_handler(commands=['start'])
def start(message):
  user_state[message.chat.id] = categories
  fully_cat.clear()
  bot.send_message(message.chat.id,
                   'Available Categories:',
                   reply_markup=generate_keyboard(categories))


@bot.message_handler(func=lambda message: message.text in user_state.get(
    message.chat.id, fully_cat))
def handle_categories(message):
  selected_category = message.text
  subcategories = user_state[message.chat.id][selected_category]

  if subcategories:
    user_state[message.chat.id] = subcategories
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

    elif num_categories == 2:
      var1 = fully_cat[0]
      var2 = fully_cat[1]
      
      bot.send_message(message.chat.id,
                       f'Selected categories: {var1} => {var2} ')
    else:
      bot.send_message(message.chat.id, f'Selected categories:ERROR')


if __name__ == '__main__':
  bot.polling()
