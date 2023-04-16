import telebot
from telebot import types
import wikipedia
from pathlib import Path

import os
import requests
import speech_recognition as sr
import soundfile as sf
import numpy as np

import uuid
import schedule

import sqlite3

token = '5288217154:AAHkIMJh7TmOkGaA5QtN-vKlyAAemUyN_es'
bot = telebot.TeleBot(token)

lang = 'rus'
message_data_dict = {}
message_id_dict = {}

userId = None

conn = sqlite3.connect('wikipedia_db.db', check_same_thread=False)
cursor = conn.cursor()


def clear_message_data_dict():
    message_data_dict.clear()
    message_id_dict.clear()


schedule.every().hour.do(clear_message_data_dict)


def db_table_val(user_id: int, title: str, url: str):
    cursor.execute('INSERT INTO favorites (user_id, title, url) VALUES (?, ?, ?)', (user_id, title, url))
    conn.commit()


def db_table_del(id_record: int):
    sql_delete_query = """DELETE from favorites where id = ?"""
    cursor.execute(sql_delete_query, (id_record, ))
    conn.commit()


def db_check(user_id: int, title: str, url: str):
    info = cursor.execute('SELECT * FROM favorites WHERE user_id=? AND title=? AND url=?', (user_id, title, url)).fetchone()

    if info is None:
        return False
    else:
        return True


def audio_to_text(dest_name: str):
    r = sr.Recognizer()
    message = sr.AudioFile(dest_name)

    with message as source:
        audio = r.record(source)
    if lang == 'rus':
        result = r.recognize_google(audio, language="ru_RU")
    else:
        result = r.recognize_google(audio, language="en-US")

    return result


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


@bot.message_handler(commands=['language'])
def language(message):
    mess = 'Выбери язык на котором будем искать информацию / Chose the language in which we will to search the information'

    markup = types.InlineKeyboardMarkup(row_width=2)
    rus = types.InlineKeyboardButton("Рус", callback_data='rus')
    eng = types.InlineKeyboardButton("Eng", callback_data='eng')
    markup.add(rus, eng)

    bot.send_message(message.chat.id, mess, reply_markup=markup)


@bot.message_handler(commands=['commands'])
def commands(message):
    mess = 'Список доступных команд / List of available commands: \n' \
           '<b>/start</b> - запуск бота / run the bot \n' \
           '<b>/language</b> - выбор языка / language selection \n' \
           '<b>/commands</b> - список команд / list of commands lol\n' \
            '<b>/random</b> - случайная статья / random article \n' \
            '<b>/favorites</b> - список сохраненных статьей / list of saves articles \n' \
           '<b>/clear</b> - удаление всех сохраненных статьей / deleting all saved articles'

    bot.send_message(message.chat.id, mess, parse_mode='html')


@bot.message_handler(commands=['random'])
def random(message):
    try:
        global userId

        if lang == 'rus':
            wikipedia.set_lang("ru")
            btn_text = 'Перейти на страницу Википедия'
            btn_text2 = 'Сохранить статью'
        else:
            wikipedia.set_lang("en")
            btn_text = 'Go to Wikipedia page'
            btn_text2 = 'Save article'

        userId = message.chat.id
        rand_article = wikipedia.random(1)
        wiki = wikipedia.WikipediaPage(title=rand_article)
        title_db = rand_article
        url_db = wikipedia.page(rand_article, auto_suggest=False).url
        sentences = 3
        img_url = None

        for img in wiki.images:
            if Path(img).suffix != '.svg':
                img_url = img
                break
        if img_url is None:
            img_url = ''

        mess = f'<b>{rand_article}</b> \n\n {wikipedia.summary(rand_article, auto_suggest=False, sentences=sentences)} {img_url}'
        uid = uuid.uuid4().hex
        message_data = {"title": title_db, "link": url_db, "message": mess, "image": img_url}

        btn = types.InlineKeyboardButton(btn_text, url=url_db)
        save_button = types.InlineKeyboardButton(btn_text2, callback_data=uid)
        message_data_dict[uid] = message_data
        markup = types.InlineKeyboardMarkup().row(btn).row(save_button)

        bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)

    except wikipedia.exceptions.DisambiguationError:
        rand_article = wikipedia.random(1)
        wiki = wikipedia.WikipediaPage(title=rand_article)
        img_url = None

        for img in wiki.images:
            if Path(img).suffix != '.svg':
                img_url = img
                break
        if img_url is None:
            img_url = ''

        mess = f'<b>{rand_article}</b> \n\n {wikipedia.summary(rand_article, auto_suggest=False, sentences=sentences)} {img_url}'

        uid = uuid.uuid4().hex
        message_data = {"title": title_db, "link": url_db, "message": mess, "image": img_url}

        btn = types.InlineKeyboardButton(btn_text, url=url_db)
        save_button = types.InlineKeyboardButton(btn_text2, callback_data=uid)
        message_data_dict[uid] = message_data
        markup = types.InlineKeyboardMarkup().row(btn).row(save_button)

        bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)


@bot.message_handler(commands=['favorites'])
def favorites(message):
    if lang == 'rus':
        text = 'Сохраненных записей  нет'
    else:
        text = 'No articles saved'

    sqlite_select_query = """SELECT * from favorites"""
    cursor.execute(sqlite_select_query)
    records = cursor.fetchall()
    records.reverse()

    mess = ''
    mess2 = ''

    for row in records:
        mess_check = mess + row[2]
        if row[1] == message.from_user.id:
            if len(mess_check) < 4096:
                mess += f'<code>{row[2]}</code>' + '\n'
            else:
                mess2 += f'<code>{row[2]}</code>' + '\n'

    if mess == '':
        mess = text

    bot.send_message(message.chat.id, mess, parse_mode='html')

    if mess2 != '':
        bot.send_message(message.chat.id, mess2, parse_mode='html')


@bot.message_handler(commands=['clear'])
def db_table_clear(message):
    if lang == 'rus':
        mess = 'Список сохраненных заголовков очищен'
    else:
        mess = 'List of saved articles cleared'

    sqlite_select_query = """SELECT * from favorites"""
    cursor.execute(sqlite_select_query)
    records = cursor.fetchall()

    for row in records:
        if row[1] == message.from_user.id:
            db_table_del(row[0])

    bot.send_message(message.chat.id, mess, parse_mode='html')


@bot.message_handler(content_types=["text"])
def query(message):
    try:
        global userId

        if lang == 'rus':
            wikipedia.set_lang("ru")
            btn_text = 'Перейти на страницу Википедия'
            btn_text2 = 'Сохранить статью'
            btn_text3 = 'Удалить статью'
        else:
            wikipedia.set_lang("en")
            btn_text = 'Go to Wikipedia page'
            btn_text2 = 'Save article'
            btn_text3 = 'Delete article'

        userId = message.chat.id
        wiki = wikipedia.WikipediaPage(title=wikipedia.page(message.text, auto_suggest=False).title)
        title_db = wikipedia.page(message.text, auto_suggest=False).title
        url_db = wikipedia.page(message.text, auto_suggest=False).url
        sentences = 3
        img_url = None

        for img in wiki.images:
            if Path(img).suffix != '.svg':
                img_url = img
                break
        if img_url is None:
            img_url = ''

        mess = f'<b>{wikipedia.page(message.text, auto_suggest=False).title}</b> \n\n ' \
               f'{wikipedia.summary(message.text, auto_suggest=False, sentences=sentences)} {img_url}'

        uid = uuid.uuid4().hex
        message_data = {"title": title_db, "link": url_db, "message": mess, "image": img_url}

        btn = types.InlineKeyboardButton(btn_text, url=url_db)
        message_data_dict[uid] = message_data
        markup = types.InlineKeyboardMarkup().row(btn)

        if db_check(userId, title_db, url_db):
            del_btn = types.InlineKeyboardButton(btn_text3, callback_data=uid)
            markup.row(del_btn)

            info = cursor.execute('SELECT * FROM favorites WHERE user_id=? AND title=? AND url=?',
                                  (userId, title_db, url_db)).fetchone()
            _id = info[0]
            message_id = {"id": _id}
            message_id_dict[uid] = message_id
        else:
            save_btn = types.InlineKeyboardButton(btn_text2, callback_data=uid)
            markup.row(save_btn)

        bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)

    except wikipedia.exceptions.DisambiguationError:
        if lang == 'rus':
            wikipedia.set_lang("ru")
            mess = 'Уточни пожалуйста свой запрос. \n\n'
        else:
            wikipedia.set_lang("en")
            mess = 'Please specify your request. \n\n'

        headers = wikipedia.search(message.text)

        for h in range(1, len(headers), 1):
            mess += f'<code>{headers[h]}</code>' + '\n'

        bot.send_message(message.chat.id, mess, parse_mode='html')

    except wikipedia.exceptions.PageError:
        try:
            if lang == 'rus':
                wikipedia.set_lang("ru")
                btn_text = 'Перейти на страницу Википедия'
                btn_text2 = 'Сохранить статью'
                btn_text3 = 'Удалить статью'
            else:
                wikipedia.set_lang("en")
                btn_text = 'Go to Wikipedia page'
                btn_text2 = 'Save article'
                btn_text3 = 'Delete article'

            message_upper = message.text.title()
            wiki = wikipedia.WikipediaPage(title=wikipedia.page(message_upper, auto_suggest=False).title)
            title_db = wikipedia.page(message_upper, auto_suggest=False).title
            url_db = wikipedia.page(message_upper, auto_suggest=False).url
            sentences = 3
            img_url = None

            for img in wiki.images:
                if Path(img).suffix != '.svg':
                    img_url = img
                    break
            if img_url is None:
                img_url = ''

            mess = f'<b>{wikipedia.page(message_upper, auto_suggest=False).title}</b> \n\n ' \
                   f'{wikipedia.summary(message_upper, auto_suggest=False, sentences=sentences)} {img_url}'
            uid = uuid.uuid4().hex
            message_data = {"title": title_db, "link": url_db, "message": mess, "image": img_url}

            btn = types.InlineKeyboardButton(btn_text, url=wikipedia.page(message_upper, auto_suggest=False).url)
            message_data_dict[uid] = message_data
            markup = types.InlineKeyboardMarkup().row(btn)

            if db_check(userId, title_db, url_db):
                del_btn = types.InlineKeyboardButton(btn_text3, callback_data=uid)
                markup.row(del_btn)

                info = cursor.execute('SELECT * FROM favorites WHERE user_id=? AND title=? AND url=?',
                                      (userId, title_db, url_db)).fetchone()
                _id = info[0]
                message_id = {"id": _id}
                message_id_dict[uid] = message_id
            else:
                save_btn = types.InlineKeyboardButton(btn_text2, callback_data=uid)
                markup.row(save_btn)

            bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)

        except wikipedia.exceptions.PageError:
            suggest = wikipedia.suggest(message.text)

            if lang == 'rus':
                wikipedia.set_lang("ru")
                if suggest is not None:
                    mess = f'Возможно, ты имел ввиду это: <code>{suggest}</code>'
                else:
                    mess = 'Я ничего не смог найти <b>PoroSad</b>.'
            else:
                wikipedia.set_lang("en")
                if suggest is not None:
                    mess = f'Perhaps, you meant this: <code>{suggest}</code>'
                else:
                    mess = "I can't find anything <b>PoroSad</b>."

            bot.send_message(message.chat.id, mess, parse_mode='html')

        except telebot.apihelper.ApiTelegramException:
            sentences = 2

            mess = f'<b>{wikipedia.page(message_upper, auto_suggest=False).title}</b> \n\n ' \
                   f'{wikipedia.summary(message_upper, auto_suggest=False, sentences=sentences)} {img_url}'
            uid = uuid.uuid4().hex
            message_data = {"title": title_db, "link": url_db, "message": mess, "image": img_url}

            btn = types.InlineKeyboardButton(btn_text, url=wikipedia.page(message_upper, auto_suggest=False).url)
            message_data_dict[uid] = message_data
            markup = types.InlineKeyboardMarkup().row(btn)

            if db_check(userId, title_db, url_db):
                del_btn = types.InlineKeyboardButton(btn_text3, callback_data=uid)
                markup.row(del_btn)

                info = cursor.execute('SELECT * FROM favorites WHERE user_id=? AND title=? AND url=?',
                                      (userId, title_db, url_db)).fetchone()
                _id = info[0]
                message_id = {"id": _id}
                message_id_dict[uid] = message_id
            else:
                save_btn = types.InlineKeyboardButton(btn_text2, callback_data=uid)
                markup.row(save_btn)

            bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)

    except telebot.apihelper.ApiTelegramException:
        sentences = 2

        mess = f'<b>{wikipedia.page(message.text, auto_suggest=False).title}</b> \n\n ' \
               f'{wikipedia.summary(message.text, auto_suggest=False, sentences=sentences)} {img_url}'

        uid = uuid.uuid4().hex
        message_data = {"title": title_db, "link": url_db, "message": mess, "image": img_url}

        btn = types.InlineKeyboardButton(btn_text, url=url_db)
        message_data_dict[uid] = message_data
        markup = types.InlineKeyboardMarkup().row(btn)

        if db_check(userId, title_db, url_db):
            del_btn = types.InlineKeyboardButton(btn_text3, callback_data=uid)
            markup.row(del_btn)

            info = cursor.execute('SELECT * FROM favorites WHERE user_id=? AND title=? AND url=?',
                                  (userId, title_db, url_db)).fetchone()
            _id = info[0]
            message_id = {"id": _id}
            message_id_dict[uid] = message_id
        else:
            save_btn = types.InlineKeyboardButton(btn_text2, callback_data=uid)
            markup.row(save_btn)

    except Exception as e:
        print(repr(e))

        if lang == 'rus':
            bot.send_message(message.from_user.id, "Неизвестная ошибка")
        else:
            bot.send_message(message.from_user.id, "Unknown error")


@bot.message_handler(content_types=['voice'])
def get_audio_messages(message):
    try:
        result = None
        file_info = bot.get_file(message.voice.file_id)
        path = os.path.splitext(file_info.file_path)[0]
        fname = os.path.basename(path)
        doc = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path))

        with open(fname + '.oga', 'wb') as f:
            f.write(doc.content)

        data, samplerate = sf.read(fname + '.oga')
        sf.write(fname + '.wav', data, samplerate)
        result = audio_to_text(fname + '.wav')
        # bot.send_message(message.from_user.id, f'<code>{format(result)}</code>', parse_mode='html')

    except sr.UnknownValueError:
        if lang == 'rus':
            bot.send_message(message.from_user.id, "Не могу распознать сообщение, или оно пустое")
        else:
            bot.send_message(message.from_user.id, "Can't recognize the message or it's empty")

    except Exception as e:
        print(repr(e))

        if lang == 'rus':
            bot.send_message(message.from_user.id, "Неизвестная ошибка")
        else:
            bot.send_message(message.from_user.id, "Unknown error")

    finally:
        os.remove(fname + '.wav')
        os.remove(fname + '.oga')

        if result is not None:
            msg = types.Message(message_id=0,
                                from_user=0,
                                date='',
                                chat=message.chat,
                                content_type='text',
                                options=[],
                                json_string='')
            msg.text = format(result)
            query(msg)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global lang

    if call.data in message_data_dict:
        message_data = message_data_dict[call.data]

        if lang == 'rus':
            wikipedia.set_lang("ru")
            btn_text = 'Перейти на страницу Википедия'
        else:
            wikipedia.set_lang("en")
            btn_text = 'Go to Wikipedia page'

        if not db_check(userId, message_data['title'], message_data['link']):
            db_table_val(user_id=userId, title=message_data['title'], url=message_data['link'])

        mess = message_data['message']
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(btn_text, url=wikipedia.page(message_data['title'], auto_suggest=False).url))

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=mess, parse_mode='html', reply_markup=markup)

    if call.data in message_id_dict:
        message_id = message_id_dict[call.data]

        db_table_del(message_id['id'])

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
                                       'Now you can write something that I have to find on Wikipedia.',
                                  parse_mode='html', reply_markup=None)


bot.polling(none_stop=True)