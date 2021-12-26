import unittest
from pythonProject.telegram_bot1 import TelegramBot, dialog, get_horoscope, city_weather


class TestStateMachine(unittest.TestCase):
    def test_dialog_change_state_to_weather(self):
        my_bot = TelegramBot()
        dialog(my_bot, 'Погода')
        self.assertEqual(my_bot.state, 'weather')

    def test_full_dialog_change_state_to_weather(self):
        my_bot = TelegramBot()
        dialog(my_bot, 'Гороскоп')
        dialog(my_bot, 'Назад')
        dialog(my_bot, 'Погода')
        self.assertEqual(my_bot.state, 'weather')

    def test_full_dialog_change_state_to_horoscope(self):
        my_bot = TelegramBot()
        dialog(my_bot, 'Погода')
        dialog(my_bot, 'Назад')
        dialog(my_bot, 'Гороскоп')
        self.assertEqual(my_bot.state, 'horoscope')

    def test_dialog_passing_an_invalid_value(self):
        my_bot = TelegramBot()
        dialog(my_bot, [1, 2, 3])
        self.assertEqual(my_bot.state, 'initial')

    def test_dialog_horoscope_valid_value(self):
        my_bot = TelegramBot()
        dialog(my_bot, 'Гороскоп')
        self.assertEqual(get_horoscope('Овен'), 'Овны – отвлекитесь от ежедневных дел и забот. '
                                                'Посвятите день себе и своим интересам.')

    def test_dialog_horoscope_invalid_value(self):
        my_bot = TelegramBot()
        dialog(my_bot, 'Гороскоп')
        get_horoscope('Мышь')
        self.assertEqual(get_horoscope('Мышь'), None)

    def test_dialog_weather_valid_value(self):
        my_bot = TelegramBot()
        dialog(my_bot, 'Погода')
        city_weather('Москва')
        self.assertEqual(city_weather('Москва'), {'temp': -6.32, 'temp_max': -5.86, 'temp_min': -7.14,
                                                  'feels_like': -13.32, 'temp_kf': None})

    def test_dialog_weather_invalid_value(self):
        my_bot = TelegramBot()
        dialog(my_bot, 'Погода')
        city_weather('Гиганотозавр')
        self.assertEqual(city_weather('Гиганотозавр'), None)


if __name__ == '__main__':
    unittest.main()

