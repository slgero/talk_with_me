import unittest
from data4ml import Data4ML
from perfect_regex import *
import re
import tempfile
from pathlib import Path


class TestData4ML(unittest.TestCase):
    def setUp(self):
        self.data4ml = Data4ML()

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

                files = self.data4ml.get_list_of_files_in_folder(dirpath, **kwargs)
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

                folders = self.data4ml.get_list_of_folders(dirpath)
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

        for numbers in telephone_numbers:
            self.assertEqual(re.sub(perfect_phone_regex, "", numbers), "")

    def test_emails(self):
        emails = [
            "example@gmail.com",
            "example@yandex.ru",
            "yanko.julia@yandex.ru",
            "yanko.julia1996@ya.ru",
        ]

        for email in emails:
            self.assertEqual(re.sub(perfect_email_regex, "", email), "")

    def test_urls(self):
        urls = [
            "https://habr.com/ru/company/otus/blog/484238/",
            "https://github.com/slgero/talk_with_me",
            "https://yandex.ru/",
            "https://stackoverflow.com/"
            "https://aliexpress.ru/item/32833281441.html?spm=a2g0v.search0104.3.25.5d7f6fe9ipJOgp&ws_ab_test=searchweb0_0%2Csearchweb201602_3_10152_10151_10065_10344_10068_10342_10343_10340_10341_10543_10084_10083_10618_10630_10307_10301_5722316_5711215_10313_10059_10534_100031_521_10103_10627_10626_10624_10623_10622_5711315_10621_10620_10142_10125%2Csearchweb201603_25%2CppcSwitch_5&algo_expid=569989c8-dc22-4f8b-95c2-e9825f281202-3&algo_pvid=569989c8-dc22-4f8b-95c2-e9825f281202&priceBeautifyAB=0",
        ]

        for url in urls:
            self.assertEqual(re.sub(perfect_url_regex, "", url), "")

    def test_emojis(self):
        emojis = ["👩\u200d", "👧\u200d"]

        for emoji in emojis:
            self.assertEqual(re.sub(perfect_emoji_regex, "", emoji), emoji[0])


if __name__ == "__main__":
    unittest.main()
