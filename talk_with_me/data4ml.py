from bs4 import BeautifulSoup
import json
import os
import re
from abc import ABC, abstractmethod
from perfect_regex import (
    perfect_url_regex,
    perfect_emoji_regex,
    perfect_email_regex,
    perfect_phone_regex,
)


class Data4ML(ABC):
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

    @abstractmethod
    def make_data():
        pass

    @abstractmethod
    def parse_html(self, folder: str, files: list) -> list:
        pass

    def get_list_of_folders(self, messages_path: str) -> list:
        folders = []

        if os.path.isdir(messages_path):
            for folder in os.listdir(messages_path):
                if not os.path.isdir(os.path.join(messages_path, folder)):
                    continue
                if folder.startswith("-"):  # VK groups or applications
                    continue
                if len(folder) < 7:  # some kind of service letters
                    continue
                if len(folder) == 10:  # group chats
                    continue
                folders.append(folder)
                folders.sort()
        else:
            print(f"No such directory: {messages_path}")
        return folders

    def get_list_of_files_in_folder(self, folder_name: str, limit=1) -> list:

        files = []
        if os.path.isdir(folder_name):
            # Get list of only html files from folder:
            files = [file for file in os.listdir(folder_name) if file.endswith(".html")]

            if len(files) < limit:  # short dialogs
                return []

            # Descending sort to consider message order:
            files = sorted(
                files,
                key=lambda x: int(re.search("messages(\d+)\.html", x).group(1)),
                reverse=True,
            )
        else:
            print(f"No such directory: {folder_name}")
        return files

    def clear_message(self, messages: list) -> list:
        assert isinstance(messages, list)
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


class Data4TextGeneration(Data4ML):
    """
    Collects the entire message together, both yours and other 
    members in the correspondence.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def make_data(self, limit=2) -> list:
        result = []
        for folder in self.get_list_of_folders(self.home_folder):
            parent_folder = os.path.join(self.home_folder, folder)
            files = self.get_list_of_files_in_folder(parent_folder, limit=limit)
            if files:
                messages = self.parse_html(parent_folder, files)
                clear_messages = self.clear_message(messages)
                result.append(clear_messages)
        return result

    def parse_html(self, parent_folder: str, files: list) -> list:

        all_messages = []
        for file in files:
            with open(os.path.join(parent_folder, file), "rb") as f:
                soup = BeautifulSoup(f, "lxml")

            messages = []
            for message in soup.find_all("div", {"class": "message"}):
                message = message.text.strip()
                messages.append(message[message.find("\n") + 1 :])

            #           Reverse the list to save the message sequence:
            all_messages.extend(messages[::-1])
        return all_messages
