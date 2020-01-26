import unittest
from data4ml import Data4ML
from perfect_regex import *
import re


class TestData4ML(unittest.TestCase):
    def setUp(self):
        self.data4ml = Data4ML()

    def test_clear_message(self):
        samples = {
            "Привет, как дела?": "Привет, как дела?",
            "   Привет, как дела?   ": "Привет, как дела?",
            " \n \n Привет, как дела? \n \n": "Привет, как дела?",
            "Привет!\n Как дела?": "Привет!\n Как дела?",
            "\nПривет!\n Как дела?\n": "Привет!\n Как дела?",
            " \n \n \n f": "f",
            "Вариант подарка\nФотография\nhttps://sun9-31.userapi.com/c205628/v205628626/19be1/bCtv1V6LIkg.jpg": "Вариант подарка",
            "Ок\n1 прикреплённое сообщение": "Ок",
            "Ок\n2 прикреплённых сообщения": "Ок",
            "Ок\n25 прикреплённых сообщений": "Ок",
            "фотки \nФотография\nhttps://sun9-55.userapi.com/c836233/v836233679/58948/Yoe97VFsvp4.jpg\n\nФотография\nhttps://sun9-57.userapi.com/c836233/v836233679/58952/sxJ6MN8IIdc.jpg": "фотки",
            "Вот моя почта: yanko.julia@yandex.ru": "Вот моя почта:",
            "yanko.julia@yandex.ru - это моя почта": "- это моя почта",
            "Вот моя почта: yanko.julia@yandex.ru, записывай": "Вот моя почта: , записывай",
            "Вот мой номер телефона: 8(800)555-35-35": "Вот мой номер телефона:",
            "8(800)555-35-35 это мой номер": "это мой номер",
            "А это 8(800)555-35-35 мой номер": "А это мой номер",
        }
        for key, value in samples.items():
            self.assertEqual(self.data4ml.clear_message([key]), [value])

        samples_empty = [
            "  ",
            " \n \n \n ",
            "\nДокумент\nhttps://vk.com/doc224156076_529351508",
            "\nФотография\nhttps://sun9-31.userapi.com/c205628/v205628626/19be1/bCtv1V6LIkg.jpg",
            "\nФотография\nhttps://sun9-55.userapi.com/c836233/v836233679/58948/Yoe97VFsvp4.jpg\n\nФотография\nhttps://sun9-57.userapi.com/c836233/v836233679/58952/sxJ6MN8IIdc.jpg",
            "https://youtu.be/u5QL2SoHYdA",
            "\nВидеозапись\nhttps://vk.com/video-111096931_456261957",
            "\nКарта",
            "\nСтикер",
            "\n1 прикреплённое сообщение",
            "\n2 прикреплённых сообщения",
            "\n25 прикреплённых сообщений",
            "yanko.julia@yandex.ru",
        ]
        for message in samples_empty:
            self.assertEqual(self.data4ml.clear_message([message]), [])


if __name__ == "__main__":
    unittest.main()
