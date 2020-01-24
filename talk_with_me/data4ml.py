from bs4 import BeautifulSoup
import json
from os import listdir
from os.path import isfile, isdir, join
import re


class Data4ML:
    def __init__(self, path_to_config="./data_params.json"):
        cfg = self.read_json(path_to_config)
        self.blacklist = [
            "Фотография",
            "Аудиозапись",
            "Документ",
            "Видеозапись",
            "прикреплённое сообщение",
            "Запись на стене",
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
        blacklist = ["Фотография", "Документ", "Видеозапись"]
        message_ends = [
            "прикреплённое сообщение",
            "прикреплённых сообщений",
            "прикреплённых сообщения",
            "Запись на стене",
            "Сообщение удалено",
        ]

        perfect_url_regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        perfect_emoji_regex = r"(\u00a9|\u00ae|[\u2000-\u3300]|\ud83c[\ud000-\udfff]|\ud83d[\ud000-\udfff]|\ud83e[\ud000-\udfff])"

        clean_messages = []
        for i in messages:

            # TODO: add it into list
            for end in message_ends:
                if i.endswith(end):
                    i = i[: i.rfind("\n")]

            # If URL in message - not append this message:
            if "\nСсылка\nhttps:" in i:
                continue

            # delet url:
            for attachment in blacklist:
                i = re.sub(f"\n{attachment}\n" + perfect_url_regex, "", i)

            # delete trash after emoji:
            i = re.sub(perfect_emoji_regex, "", i)

            i = i.strip()
            if i:
                clean_messages.append(i)
        return clean_messages

    @staticmethod
    def read_json(path_to_config: str) -> dict:
        with open(path_to_config, "r") as f:
            cfg = json.load(f)
        return cfg
