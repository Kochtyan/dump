import telebot
from telebot import types
import wikipedia
from pathlib import Path


bot = telebot.TeleBot('5288217154:AAHkIMJh7TmOkGaA5QtN-vKlyAAemUyN_es')

lang = 'rus'



@bot.message_handler(commands=['start'])
def start(message):
    mess = f'<b>Привет, {message.from_user.first_name}!</b> Я <b>Википедия Бот</b>🤖. Сначала выбери язык на которым мы будем общаться, ' \
           f'или ты можешь написать <b>/commands</b> для получения списка доступных команд. \n\n' \
           f'<b>Hello, {message.from_user.first_name}!</b> Im <b>Wikipedia Bot</b>🤖. First choose the language in which we will communicate, ' \
           f'or you can write <b>/commands</b> to get list of available commands.'
    mess2 = 'Язык / Language'
    markup = types.InlineKeyboardMarkup(row_width=2)
    rus = types.InlineKeyboardButton("Рус", callback_data='rus')
    eng = types.InlineKeyboardButton("Eng", callback_data='eng')
    markup.add(rus, eng)
    bot.send_message(message.chat.id, mess, parse_mode='html')
    bot.send_message(message.chat.id, mess2, parse_mode='html', reply_markup=markup)


@bot.message_handler(commands=['commands'])
def commands(message):
    mess = 'Список доступных команд/List of available commands: \n' \
           '<b>/start</b> - запуск бота / run the bot \n' \
           '<b>/language</b> - выбор языка / language selection \n' \
           '<b>/commands</b> - список команд / list of commands lol'
    bot.send_message(message.chat.id, mess, parse_mode='html')

@bot.message_handler(commands=['language'])
def language(message):
    mess = 'Выбери язык на котором будем искать информацию / Chose the language in which we will to search the information'
    markup = types.InlineKeyboardMarkup(row_width=2)
    rus = types.InlineKeyboardButton("Рус", callback_data='rus')
    eng = types.InlineKeyboardButton("Eng", callback_data='eng')
    markup.add(rus, eng)
    bot.send_message(message.chat.id, mess, reply_markup=markup)

def set_language():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    set_lang = types.KeyboardButton('/language')
    markup.add(set_lang)


@bot.message_handler(content_types=["text"])
def query(message):
    try:
        if lang == 'rus':
            wikipedia.set_lang("ru")
            btn_text = 'Перейти на страницу Википедия'
        else:
            wikipedia.set_lang("en")
            btn_text = 'Go to Wikipedia page'

        wiki = wikipedia.WikipediaPage(title=wikipedia.page(message.text, auto_suggest=False).title)
        for img in wiki.images:
            if Path(img).suffix != '.svg':
                img_url = img
                break
        mess = f'<b>{wikipedia.page(message.text, auto_suggest=False).title}</b> \n\n {wikipedia.summary(message.text, auto_suggest=False, sentences=3)} {img_url}'
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(btn_text, url=wikipedia.page(message.text, auto_suggest=False).url))
        bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)

    except wikipedia.exceptions.DisambiguationError:
        if lang == 'rus':
            wikipedia.set_lang("ru")
            mess = 'Уточни пожалуйста свой запрос. \n\n'
        else:
            wikipedia.set_lang("en")
            mess = 'Please specify your request. \n\n'
        headers = wikipedia.search(message.text)
        for h in range(1,len(headers),1):
                mess += f'<code>{headers[h]}</code>' + '\n'
        bot.send_message(message.chat.id, mess, parse_mode='html')

    except wikipedia.exceptions.PageError:
        try:
            if lang == 'rus':
                wikipedia.set_lang("ru")
                btn_text = 'Перейти на страницу Википедия'
            else:
                wikipedia.set_lang("en")
                btn_text = 'Go to Wikipedia page'
            message_upper = message.text.title()
            mess = f'<b>{wikipedia.page(message_upper, auto_suggest=False).title}</b> \n\n {wikipedia.summary(message_upper, auto_suggest=False, sentences=3)}'
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton(btn_text, url=wikipedia.page(message_upper, auto_suggest=False).url))
            bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
        except wikipedia.exceptions.PageError:
            suggest = wikipedia.suggest(message.text)
            if lang == 'rus':
                wikipedia.set_lang("ru")
                if suggest != None:
                    mess = f'Возможно, ты имел ввиду это: <code>{suggest}</code>'
                else:
                    mess = 'Я ничего не смог найти <b>PoroSad</b>.'
            else:
                wikipedia.set_lang("en")
                if suggest != None:
                    mess = f'Perhaps, you meant this: <code>{suggest}</code>'
                else:
                    mess = "I can't find anything <b>PoroSad</b>."
            bot.send_message(message.chat.id, mess, parse_mode='html')






@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global lang
    try:
        if call.message:
            if call.data == 'rus':
                lang = 'rus'
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Ладно, будем общаться так PoroSad. <b>Русский язык установлен.</b> \n\n'
                                           'Теперь ты можешь что-нибудь написать, а я найду это в Википедии.',
                                      parse_mode='html', reply_markup=None)

            elif call.data == 'eng':
                lang = 'eng'
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='Wow, u seems like quiet a fella. <b>English language set.</b> \n\n'
                                           'Now you can write something that I have to find on Wikipedia.', parse_mode='html', reply_markup=None)
    except Exception as e:
        print(repr(e))


bot.polling(none_stop=True)

