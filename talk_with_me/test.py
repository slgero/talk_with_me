import unittest
from data4ml import Data4ML


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
        }
        for key, value in samples.items():
            self.assertEqual(self.data4ml.clear_message([key]), [value])

        samples_empty = [
            "  ",
            " \n \n \n ",
            "\nДокумент\nhttps://vk.com/doc224156076_529351508",
            "\nФотография\nhttps://sun9-31.userapi.com/c205628/v205628626/19be1/bCtv1V6LIkg.jpg",
            "\nФотография\nhttps://sun9-55.userapi.com/c836233/v836233679/58948/Yoe97VFsvp4.jpg\n\nФотография\nhttps://sun9-57.userapi.com/c836233/v836233679/58952/sxJ6MN8IIdc.jpg",
            "\nВидеозапись\nhttps://vk.com/video-111096931_456261957",
            "\nКарта",
            "\nСтикер",
            "\n1 прикреплённое сообщение",
            "\n2 прикреплённых сообщения",
            "\n25 прикреплённых сообщений",
        ]
        for mes in samples_empty:
            self.assertEqual(self.data4ml.clear_message([mes]), [])


if __name__ == "__main__":
    unittest.main()
