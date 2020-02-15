import unittest
from data4ml import Data4TextGeneration, Data4Chatbot
from perfect_regex import (
    perfect_url_regex,
    perfect_emoji_regex,
    perfect_email_regex,
    perfect_phone_regex,
)
import re
import tempfile
from pathlib import Path


class TestData4ML(unittest.TestCase):
    def setUp(self):
        self.TextGen = Data4TextGeneration()

    def test_get_list_of_files_in_folder(self):
        def create_tmp_files(
            answer, files_count=None, file_numbers=None, suffix=".html", **kwargs
        ):
            """
            Сreate temporary files for testing.
            Params:
            ------
            
            answer: int or list
                Value for comparison.
            files_count: int or None (default=None)
                Number of files to create.
            file_numbers: list or None (default=None)
                List of file names for testing the sort function.
            """

            range_of_files = range(files_count) if files_count else file_numbers

            # Create a temporary directory:
            with tempfile.TemporaryDirectory() as dirpath:
                for i in range_of_files:
                    # Create a tmp file:
                    fd, path = tempfile.mkstemp(suffix=suffix, dir=dirpath)

                    # Rename the file to bring it to standard:
                    p = Path(path)
                    p.rename(Path(p.parent, f"messages{i}{p.suffix}"))

                files = self.TextGen.get_list_of_files_in_folder(dirpath, **kwargs)
                if files_count:
                    # Check the number of files in a folder:
                    self.assertEqual(len(files), answer)
                else:
                    # Check proper file sorting:
                    self.assertEqual(files, answer)

        # Check the number of files in a folder:
        create_tmp_files(answer=4, files_count=4)
        create_tmp_files(answer=0, files_count=4, suffix=".txt")
        create_tmp_files(answer=0, files_count=4, limit=5)
        create_tmp_files(answer=4, files_count=4, limit=4)

        # Check proper file sorting:
        create_tmp_files(
            answer=["messages100.html", "messages10.html", "messages1.html"],
            file_numbers=[1, 10, 100],
        )
        create_tmp_files(
            answer=["messages100.html", "messages10.html", "messages1.html"],
            file_numbers=[100, 10, 1],
        )
        create_tmp_files(
            answer=["messages100.html", "messages10.html", "messages1.html"],
            file_numbers=[100, 1, 10],
        )
        create_tmp_files(
            answer=["messages210.html", "messages200.html", "messages1.html"],
            file_numbers=[200, 1, 210],
        )
        create_tmp_files(
            answer=["messages300.html", "messages200.html", "messages40.html"],
            file_numbers=[300, 40, 200],
        )

    def test_get_list_of_folders(self):
        def create_tmp_folders(answer: int, folder_names: list):
            """
            Сreate temporary directories for testing.
            
            Params:
            ------
            
            answer: int
                Value for comparison.
            folder_names: list
                List of folder names.
            """

            # Create the main directory:
            with tempfile.TemporaryDirectory() as dirpath:
                for folder_name in folder_names:
                    # Create a tmp folder:
                    path = tempfile.mkdtemp(dir=dirpath)

                    # Rename the folder to bring it to standard:
                    p = Path(path)
                    p.rename(Path(p.parent, folder_name))

                folders = self.TextGen.get_list_of_folders(dirpath)
                self.assertEqual(len(folders), answer)

        create_tmp_folders(0, [])
        create_tmp_folders(0, ["-185144161"])  # VK groups or applications
        create_tmp_folders(0, ["18514"])  # some kind of service letters
        create_tmp_folders(0, ["2000000043"])  # group chats
        create_tmp_folders(1, ["185144161"])
        create_tmp_folders(1, ["185144161", "-185144161"])
        create_tmp_folders(1, ["185144161", "-185144161", "18514"])
        create_tmp_folders(1, ["185144161", "-185144161", "18514", "2000000043"])
        create_tmp_folders(2, ["185144161", "185144162"])

    def test_clear_messages(self):

        # Testing for garbage removal from messages:
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
            "Весело\nАудиозапись": "Весело",
            "Посмотри это видео": "Посмотри это видео",
            "Что за фотография": "Что за фотография",
            "Это мой подарок": "Это мой подарок",
            "История жизни": "История жизни",
            "жизни История": "жизни",  # it is necessary
        }
        for key, value in samples.items():
            self.assertEqual(self.TextGen.clear_messages([key]), [value])

        # Testing deleting an entire message:
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
            "Аудиозапись\n\nАудиозапись\n\nАудиозапись\n\nАудиозапись",
        ]
        for message in samples_empty:
            self.assertEqual(self.TextGen.clear_messages([message]), [])

        # Test atribute:
        self.assertRaises(AssertionError, self.TextGen.clear_messages, "message")

    def test_read_json(self):
        # Test valid path:
        res = self.TextGen.read_json("./data_params.json")
        self.assertIsInstance(res, dict)

        # Test wrong path:
        self.assertRaises(
            FileNotFoundError, self.TextGen.read_json, "./wrong_path.json"
        )


class TestData4Chatbot(unittest.TestCase):
    def setUp(self):
        self.data4bot = Data4Chatbot()
        self.data4bot.home_folder = "./talk_with_me/data4test"

    def test_parse_html(self):
        pass

    def test_transform_message(self):
        pass

    def test_clear_messages(self):
        pass

    def test_make_data(self):
        pass

    def test_check_max_length(self):
        self.assertTrue(self.data4bot._check_max_length(["* " * 5, "* " * 5]))
        self.assertFalse(self.data4bot._check_max_length(["* " * 5, "* " * 11]))
        self.assertFalse(self.data4bot._check_max_length(["* " * 11, "* " * 5]))
        self.assertFalse(self.data4bot._check_max_length(["* " * 11, "* " * 11]))

    def test_filter_pairs(self):
        to_check = [
            ["* " * 11, "* " * 11],
            ["* " * 5, "* " * 5],
            ["* " * 6, "* " * 6],
            ["* " * 6, "* " * 11],
            ["* " * 11, "* " * 6],
        ]
        res = [["* " * 5, "* " * 5], ["* " * 6, "* " * 6]]
        self.assertEqual(self.data4bot.filter_pairs(to_check), res)

        empty_list = [[], []]
        self.assertRaises(IndexError, self.data4bot.filter_pairs, empty_list)

    def test_get_pais(self):
        to_check = ["1", "2 2", "3 3", "4 4", "5 5 5", "6 6 6 6"]
        ans1 = [
            ["1", "2 2"],
            ["2 2", "3 3"],
            ["3 3", "4 4"],
            ["4 4", "5 5 5"],
            ["5 5 5", "6 6 6 6"],
        ]
        ans2 = [["1", "2 2"], ["2 2", "3 3"], ["3 3", "4 4"]]
        ans3 = []

        self.assertEqual(self.data4bot.get_pairs(to_check), ans1)

        self.data4bot.max_length = 3
        self.assertEqual(self.data4bot.get_pairs(to_check), ans2)

        self.data4bot.max_length = 1
        self.assertEqual(self.data4bot.get_pairs(to_check), ans3)

    def test_normalize_message(self):

        # ru:
        self.assertEqual(self.data4bot.normalize_message("тест"), "тест")
        self.assertEqual(self.data4bot.normalize_message("тест."), "тест .")
        self.assertEqual(self.data4bot.normalize_message("тест..."), "тест . . .")
        self.assertEqual(self.data4bot.normalize_message("тест!?"), "тест ! ?")
        self.assertEqual(self.data4bot.normalize_message("тест   тест"), "тест тест")
        self.assertEqual(self.data4bot.normalize_message("тест12 3"), "тест")
        self.assertEqual(self.data4bot.normalize_message("тЁсть"), "тёсть")
        self.assertEqual(self.data4bot.normalize_message("ЁёЙйЪъЬь"), "ёёййъъьь")
        self.assertEqual(self.data4bot.normalize_message("тест-test"), "тест test")

        # en:
        self.assertEqual(self.data4bot.normalize_message("test"), "test")
        self.assertEqual(self.data4bot.normalize_message("test."), "test .")
        self.assertEqual(self.data4bot.normalize_message("test123"), "test")
        self.assertEqual(self.data4bot.normalize_message("test, test"), "test test")
        self.assertEqual(
            self.data4bot.normalize_message("test: test-test"), "test test test"
        )
        self.assertEqual(
            self.data4bot.normalize_message("test1  1 1 1 test"), "test test"
        )
        self.assertEqual(self.data4bot.normalize_message("Hello."), "hello .")
        self.assertEqual(self.data4bot.normalize_message("TEST"), "test")


class TestData4TextGeneration(unittest.TestCase):
    def setUp(self):
        self.data4gen = Data4TextGeneration()
        self.data4gen.home_folder = "./talk_with_me/data4test"

    def test_parse_html(self):
        answer = [
            "пришли фотки, пожалуйста",
            "wrong@yandex.ru",
            "Привет, сейчас",
            "Всё👌",
            "Спасибо большое",
            "👌",
            "Сережка, перешли мне письмо Смоленцевой.\n1 прикреплённое сообщение",
            "Заранее спасибо",
            "Какое именно?",
            "Последнее. Про кино",
            "Спасибо",
            "Скинул",
            "Подойдите завтра к смоленцевой",
            "зачем?",
            "Она попросила",
            "Хорошо",
            "Юль",
            "не забывай, что вы завтра в 12 танцуете",
            "И своим передай",
            "Хорошо",
            "спасибо",
            "\nФотография\nhttps://sun9-36.userapi.com/c636124/v636124076/cba1/MsjVQhRLUIEg.jpg",
            "Спасибо",
            "\nФотография\nhttps://sun9-21.userapi.com/c633831/v633831076/323f6/CsN5SSfrUUS0.jpg",
            "а до скольких?",
            "спасибо",
        ]

        parent_folder = "talk_with_me/data4test/153164714"
        files = ["messages0.html"]
        self.assertEqual(self.data4gen.parse_html(parent_folder, files), answer)

        # Test function attributes:
        self.assertRaises(
            AssertionError, self.data4gen.parse_html, parent_folder, "messages0.html"
        )

        # Test wrong path:
        parent_folder = "wrong_path"
        self.assertRaises(
            FileNotFoundError, self.data4gen.parse_html, parent_folder, files
        )

    def test_integration(self):
        answer = [
            [
                "Привет, Арин, ты уже считала физику? 16 лабу",
                "Привет, нет еще",
                "Хмм, ну ладно, я хотел графики сверить",
                "Воин, привет, скинь, пожалуйста контрольную по органу",
                "Арин*",
                "о, спасибо)",
                "Сереж, я 9 вариант по органике, но я тоже его сделала и переделывать не буду",
                "Блиииин",
                "Я дурак",
                "да ладно, может Ф.И не заметит, что у нас одинаковые варианты",
                "Он разрешил)",
                "Сереж, ты спрашивал у Екатерины Валерьевны про домашку?",
                "Ну да",
                "Она мне подсказывала",
                "Ты можешь кинуть формулы, если вы их вывели",
                "Да, но только как дома буду",
                "Сейчас неудобно",
                "В общем, мы кое-что вывели",
                "Ну это понятно",
                "Она сказала ещё проверить",
                "Ты точку эквивалентности уже считала?",
                "Потому что у тебя тоже возможно ошибка",
                "Ну да, я попыталась",
                "Там корень 3 из Кс/на 4",
                "Ну как я понимаю",
                "А у тебя какая соль?",
                "Ну осадок",
                "Хлорид кальция",
                "Ну у меня наоборот",
                "В общем",
                "Я как буду дома",
                "Напишу",
                "Арин",
                "Привет",
                "Извини, что не написал",
                "Я забыл совсем",
                "А ты не на понмила",
                "Арин",
                "Добрый вечер",
                "А ты 8 дз по органике сделать уже?",
                "пришли фотки, пожалуйста",
                "Привет, сейчас",
                "Всё👌",
                "Спасибо большое",
                "👌",
                "Сережка, перешли мне письмо Смоленцевой.",
                "Заранее спасибо",
                "Какое именно?",
                "Последнее. Про кино",
                "Спасибо",
                "Скинул",
                "Подойдите завтра к смоленцевой",
                "зачем?",
                "Она попросила",
                "Хорошо",
                "Юль",
                "не забывай, что вы завтра в 12 танцуете",
                "И своим передай",
                "Хорошо",
                "спасибо",
                "Спасибо",
                "а до скольких?",
                "спасибо",
            ],
            [
                "пришли фотки, пожалуйста",
                "Привет, сейчас",
                "Всё👌",
                "Спасибо большое",
                "👌",
                "Сережка, перешли мне письмо Смоленцевой.",
                "Заранее спасибо",
                "Какое именно?",
                "Последнее. Про кино",
                "Спасибо",
                "Скинул",
                "Подойдите завтра к смоленцевой",
                "зачем?",
                "Она попросила",
                "Хорошо",
                "Юль",
                "не забывай, что вы завтра в 12 танцуете",
                "И своим передай",
                "Хорошо",
                "спасибо",
                "Спасибо",
                "а до скольких?",
                "спасибо",
            ],
        ]

        # Test all folders:
        clear_messages = self.data4gen.make_data(limit=1)
        self.assertEqual(clear_messages, answer)

        # Test all folders with 2 files:
        clear_messages = self.data4gen.make_data(limit=2)
        self.assertEqual(len(clear_messages), 1)
        self.assertEqual(clear_messages[0], answer[0])

        # Test limit:
        clear_messages = self.data4gen.make_data(limit=3)
        self.assertEqual(clear_messages, [])


class TestPerfectRegex(unittest.TestCase):
    def test_telephone_numbers(self):
        telephone_numbers = [
            "+7(903)888-88-88",
            "8(999)99-999-99",
            "+79261234567",
            "89261234567",
            "79261234567",
            "+7 926 123 45 67",
            "8(926)123-45-67",
            "9261234567",
            "79261234567",
            "(495)1234567",
            "(495) 123 45 67",
            "89261234567",
            "8-926-123-45-67",
            "8 927 1234 234",
            "8 927 12 12 888",
            "8 927 12 555 12",
            "8 927 123 8 123",
            "+380(67)777-7-777",
            "001-541-754-3010",
            "+1-541-754-3010",
            "19-49-89-636-48018",
            "+233 205599853",
            "8(800)555-35-35",
        ]

        for number in telephone_numbers:
            self.assertRegex(number, perfect_phone_regex)

    def test_emails(self):
        emails = [
            "example@gmail.com",
            "example@yandex.ru",
            "yanko.julia@yandex.ru",
            "yanko.julia1996@ya.ru",
        ]

        for email in emails:
            self.assertRegex(email, perfect_email_regex)

    def test_urls(self):
        urls = [
            "https://habr.com/ru/company/otus/blog/484238/",
            "https://github.com/slgero/talk_with_me",
            "https://yandex.ru/",
            "https://stackoverflow.com/"
            "https://aliexpress.ru/item/32833281441.html?spm=a2g0v.search0104.3.25.5d7f6fe9ipJOgp&ws_ab_test=searchweb0_0%2Csearchweb201602_3_10152_10151_10065_10344_10068_10342_10343_10340_10341_10543_10084_10083_10618_10630_10307_10301_5722316_5711215_10313_10059_10534_100031_521_10103_10627_10626_10624_10623_10622_5711315_10621_10620_10142_10125%2Csearchweb201603_25%2CppcSwitch_5&algo_expid=569989c8-dc22-4f8b-95c2-e9825f281202-3&algo_pvid=569989c8-dc22-4f8b-95c2-e9825f281202&priceBeautifyAB=0",
        ]

        for url in urls:
            self.assertRegex(url, perfect_url_regex)

    def test_emojis(self):
        emojis = ["👩\u200d", "👧\u200d"]

        for emoji in emojis:
            self.assertRegex(emoji, perfect_emoji_regex)


if __name__ == "__main__":
    unittest.main()
