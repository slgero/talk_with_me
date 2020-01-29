import unittest
from data4ml import Data4ML
from perfect_regex import *
import re
import tempfile
from pathlib import Path


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
