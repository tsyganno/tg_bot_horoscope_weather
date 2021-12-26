from transitions import Machine
from telebot import TeleBot, types
import requests
from bs4 import BeautifulSoup
from pyowm import OWM
from pyowm.commons import exceptions
from transliterate import translit
from dotenv import load_dotenv
import os
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OWM_TOKEN = os.getenv('OWM_TOKEN')

bot = TeleBot(TELEGRAM_TOKEN)
owm = OWM(OWM_TOKEN)
mgr = owm.weather_manager()


class TelegramBot(object):
    states = ['initial', 'weather', 'horoscope']

    def __init__(self):
        self.machine = Machine(model=self, states=TelegramBot.states, initial='initial')
        self.machine.add_transition('weather', 'initial', 'weather')
        self.machine.add_transition('horoscope', 'initial', 'horoscope')
        self.machine.add_transition('initial', '*', 'initial')


my_bot = TelegramBot()

sign_of_horoscope = ['Овен', 'Телец', 'Близнецы', 'Рак', 'Лев', 'Дева', 'Весы', 'Скорпион', 'Стрелец', 'Козерог',
                     'Водолей', 'Рыбы']
example_cities = ['Москва', 'Санкт-Петербург', 'Иркутск', 'Улан-Удэ', 'Сочи', 'Краснодар']


def get_horoscope(answer):
    """ Возвращает текст гороскопа по знаку зодиака парсингом кода страницы html"""
    link = 'https://retrofm.ru/index.php?go=goroskop'
    inquiry = requests.get(link)
    soup = BeautifulSoup(inquiry.text, 'html.parser')
    my_list_1 = soup.find_all("div", {"class": "text_box"})
    for el in my_list_1:
        element = str(el).strip()
        if answer in element:
            index_1 = element.find(f'<h6>{answer}</h6>') + len(answer) + 9
            index_2 = element.find('</div>') - 5
            return element[index_1: index_2].strip()


def city_weather(human_message):
    """ Производим транслитерацию с русского языка на английский,
    пытаемся получить данные погодных условий по переданному названию городы"""
    city = translit(human_message, "ru", reversed=True) + ', RU'
    try:
        observation = mgr.weather_at_place(city)
    except exceptions.NotFoundError:
        return None
    return observation.weather.temperature('celsius')


def dialog(my_bot, text):
    if my_bot.state == 'initial' and text == 'Погода':
        my_bot.weather()
    elif my_bot.state == 'initial' and text == 'Гороскоп':
        my_bot.horoscope()
    elif my_bot.state != 'initial' and text == 'Назад':
        my_bot.initial()


def keyboard_cities():
    """ Создаем клавиатуру в меню диалога с названиями городов и клавишу 'Назад'"""
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    city_buttons = []
    for city in example_cities:
        city_buttons.append(types.KeyboardButton(city))
    keyboard.add(*city_buttons, types.KeyboardButton('Назад'))
    return keyboard


@bot.message_handler(commands=['start'])
def start_message(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    button_1 = types.KeyboardButton('Погода')
    button_2 = types.KeyboardButton('Гороскоп')
    keyboard.add(button_1, button_2)
    bot.send_message(message.chat.id, 'Привет, меня зовут Гороскоп-Погодник-Бот. Выберите раздел: Погода или '
                                      'Гороскоп на сегодня.', reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def send_text(message):
    incoming = str(message.text)
    human_message = incoming[0].upper() + incoming[1:]
    dialog(my_bot, human_message)
    if my_bot.state == 'weather' and human_message == 'Погода':
        bot.send_message(message.chat.id, 'Введите название города, который вас интересует.',
                         reply_markup=keyboard_cities())
    elif my_bot.state == 'weather':
        data = city_weather(human_message)
        if data is None:
            bot.send_message(message.chat.id, 'Введите корректное название города.')
        else:
            output_message = f'Температура сейчас: {data["temp"]}\nМаксимальная температура сегодня: {data["temp_max"]}\n' \
                      f'Минимальная температура сегодня: {data["temp_min"]}\nОщущается как: {data["feels_like"]}'
            bot.send_message(message.chat.id, output_message)
            bot.send_message(message.chat.id, 'Введите название города, который вас интересует.',
                             reply_markup=keyboard_cities())
    elif my_bot.state == 'horoscope' and human_message == 'Гороскоп':
        keyboard = types.ReplyKeyboardMarkup(row_width=3)
        sign_buttons = []
        for sign in sign_of_horoscope:
            sign_buttons.append(types.KeyboardButton(sign))
        keyboard.add(*sign_buttons, types.KeyboardButton('Назад'))
        bot.send_message(message.chat.id, 'Выберите свой знак зодиака', reply_markup=keyboard)
    elif my_bot.state == 'initial':
        keyboard = types.ReplyKeyboardMarkup(row_width=2)
        button_1 = types.KeyboardButton('Погода')
        button_2 = types.KeyboardButton('Гороскоп')
        keyboard.add(button_1, button_2)
        bot.send_message(message.chat.id, 'Выберите раздел: Погода или Гороскоп на сегодня.', reply_markup=keyboard)
    elif my_bot.state == 'horoscope' and human_message in sign_of_horoscope:
        bot.send_message(message.chat.id, get_horoscope(human_message))
    else:
        bot.send_message(message.chat.id, 'Вы ввели некорректные данные, попробуйте еще раз.')


bot.infinity_polling()


