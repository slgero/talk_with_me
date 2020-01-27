from bs4 import BeautifulSoup
import json
from os import listdir
from os.path import isfile, isdir, join
import re
from perfect_regex import *


class Data4ML:
    def __init__(self, path_to_config="./data_params.json"):
        cfg = self.read_json(path_to_config)

        self.home_folder = "../messages"  # add to json
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

    def make_data(self):
        HOME_FOLDER = "../messages"  # add to json

        RES = []
        for folder in self.get_list_of_folders(HOME_FOLDER):
            files = self.get_list_of_files_in_folder(join(HOME_FOLDER, folder), limit=4)
            if files:
                RES.append(self.parse_html(join(HOME_FOLDER, folder), files))

    def get_list_of_folders(self, messages_path: str) -> list:
        folders = []

        if os.path.isdir(messages_path):
            for folder in listdir(messages_path):
                if not os.path.isdir(join(messages_path, folder)):
                    continue
                if folder.startswith("-"):  # VK groups or applications
                    continue
                if len(folder) < 7:  # some kind of service letters
                    continue
                if len(folder) == 10:  # group chats
                    continue
                folders.append(folder)
        else:
            print(f"No such directory: {messages_path}")

        return folders

    def get_list_of_files_in_folder(self, folder_name: str, limit=1) -> list:

        if os.path.isdir(folder_name):
            # Get list of only html files from folder:
            files = [file for file in listdir(folder_name) if file.endswith(".html")]

            if len(files) < limit:  # short dialogs
                return []

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
        messages = []

        for file in files:
            with open(join(folder, file), "rb") as f:
                soup = BeautifulSoup(f, "lxml")

            for message in soup.find_all("div", {"class": "message"}):
                message = message.text.strip()
                messages.append(message[message.find("\n") + 1 :])

        messages = messages[::-1]  # reverse
        return messages

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
