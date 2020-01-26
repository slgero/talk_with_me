from bs4 import BeautifulSoup
import json
from os import listdir
from os.path import isfile, isdir, join
import re
from perfect_regex import *


class Data4ML:
    def __init__(self, path_to_config="./data_params.json"):
        cfg = self.read_json(path_to_config)
        self.blacklist = ["Фотография", "Документ", "Видеозапись"]
        self.message_ends = [
            "прикреплённое сообщение",
            "прикреплённых сообщений",
            "прикреплённых сообщения",
            "Запись на стене",
            "Сообщение удалено",
            "\nКарта",
            "\nСтикер",
        ]

    def get_list_of_files_in_folder(self, folder_name: str) -> list:

        if os.path.isdir(folder_name):
            # Get list of only html files from folder:
            files = [file for file in listdir(folder_name) if file.endswith(".html")]

            # Descending sort to consider message order:
            files = sorted(
                files,
                key=lambda x: int(re.search("messages(\d+)\.html", x).group(1)),
                reverse=True,
            )
            return files
        else:
            print(f"No such directory: {folder_name}")
            return []

    def parse_html(self, folder: str, files: list):
        all_messages = []

        for file in files:
            with open(join(folder, file), "r") as f:
                soup = BeautifulSoup(f, "lxml")

            messages = []
            for message in soup.find_all("div", {"class": "meassage"}):
                message = message.text.strip()

    def clear_message(self, messages: list) -> list:
        cleared_messages = []
        for i in messages:
            # If `Ссылка` in message - not append this message:
            if "\nСсылка\nhttps:" in i:
                continue

            # Delete trash such as stickers, attached messages:
            for end in self.message_ends:
                if i.endswith(end):
                    i = i[: i.rfind("\n")]

            # Delete attachments such as photos, documents, ect.:
            for attachment in self.blacklist:
                i = re.sub(f"\n{attachment}\n" + perfect_url_regex, "", i)

            # Delete trash:
            i = re.sub(perfect_emoji_regex, "", i)
            i = re.sub(perfect_email_regex, "", i)
            i = re.sub(perfect_phone_regex, " ", i)
            i = re.sub(perfect_url_regex, "", i)

            i = i.replace("  ", " ")  # remove double space
            i = i.strip()
            if i:
                cleared_messages.append(i)
        return cleared_messages

    @staticmethod
    def read_json(path_to_config: str) -> dict:
        with open(path_to_config, "r") as f:
            cfg = json.load(f)
        return cfg
