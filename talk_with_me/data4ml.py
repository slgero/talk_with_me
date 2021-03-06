"""
Module for preparing and clearing text data from VK messages.
"""
import json
import os
import re
from abc import ABC, abstractmethod
from typing import List
from bs4 import BeautifulSoup
from typeguard import typechecked
from tqdm import tqdm
from perfect_regex import (
    perfect_url_regex,
    perfect_emoji_regex,
    perfect_email_regex,
    perfect_phone_regex,
)


class Data4ML(ABC):
    """The base class to prepare and clear text data from VK messages.
    """

    def __init__(self, path_to_config: str = "./data_params.json"):
        self.cfg = self.read_json(path_to_config)

        self.home_folder = "../messages"  # add to json
        self.blacklist = [
            "Фотография",
            "Документ",
            "Видеозапись",
            "Аудиозапись",
            "Видео",
            "История",
            "Запись на стене",
            "Подарок",
            "Ссылка",
        ]

        self.message_ends = [
            "прикреплённое сообщение",
            "прикреплённых сообщений",
            "прикреплённых сообщения",
            "Запись на стене",
            "Сообщение удалено",
            "Карта",
            "Стикер",
        ]

    @abstractmethod
    @typechecked
    def make_data(self, limit: int):
        """Starts a full cycle of preparing and cleaning text data from VK messages.
        """

    @abstractmethod
    @typechecked
    def parse_html(self, parent_folder: str, files: list) -> List[str]:
        """
        Parse text from html and place it in the correct order.

        Parameters
        ----------
        parent_folder : str
            Parent directory where the `files` are located.
        files : list of str
            HTML files for parsing.

        Returns
        -------
        list оf str
            Messages in the correct order.
        """

    @typechecked
    def get_list_of_folders(self, messages_path: str) -> List[str]:
        """
        Scans the folder and selects only valid chats, skipping group chats,
        applications or some kind of service letters.

        Parameters:
        -----------
        messages_path : str
            Path to `messages` folder from archive.

        Returns
        -------
        list of str
            List of folders with valid chats.
        """

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

                # This is so that the folders are in the same order as on the git:
                folders.sort()
        else:
            print(f"No such directory: {messages_path}")
        return folders

    @typechecked
    def get_list_of_files_in_folder(
        self, folder_name: str, limit: int = 1
    ) -> List[str]:
        """
        Returns a sorted list with files of messages if the number of files
        in the folder is greater than the limit

        Parameters:
        -----------
        folder_name : str
            The path to the folder in which files will be searched.
        limit : int (default=1)
            Limit the number of message files at which this chat  will be skipped.
            In one file 300 messages. Most likely this is not a chat with your friend
            if there is only one file in the folder. So it is better not to skip it.

        Returns
        -------
            Sorted list with files of messages.
        """

        files = []
        if os.path.isdir(folder_name):
            # Get list of only html files from folder:
            files = [file for file in os.listdir(folder_name) if file.endswith(".html")]

            if len(files) < limit:  # short dialogs
                return []

            # Descending sort to consider message order:
            files = sorted(
                files,
                key=lambda x: int(re.search(r"messages(\d+)\.html", x).group(1)),
                reverse=True,
            )
        else:
            print(f"No such directory: {folder_name}")
        return files

    @typechecked
    def _clear_message(self, message: str) -> str:
        """Сlean a message from attachments and garbage using regular expressions.
        """

        # If `Ссылка` in message - not append this message:
        if "\nСсылка\nhttps:" in message or "#comments" in message:
            return ""

        # Delete trash such as stickers, attached messages:
        for end in self.message_ends:
            if message.endswith(end):
                message = message[: message.rfind("\n")]

        # Delete attachments such as photos, documents, ect.:
        for attachment in self.blacklist:
            message = re.sub(f"[\n]?{attachment}[\n]?" + perfect_url_regex, "", message)
            message = re.sub(f"[\n]?{attachment}[\n]?$", "", message)

        # Delete trash:
        message = re.sub(perfect_emoji_regex, "", message)
        message = re.sub(perfect_email_regex, "", message)
        message = re.sub(perfect_phone_regex, " ", message)
        message = re.sub(perfect_url_regex, "", message)
        message = re.sub(f"[\n]?Аудиозапись[\n]?", "", message)
        message = re.sub("  ", " ", message)
        message = message.strip()

        return message

    @abstractmethod
    @typechecked
    def clear_messages(self, all_messages: list) -> list:
        pass

    @staticmethod
    @typechecked
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

    @typechecked
    def make_data(self, limit=2) -> list:
        result = []
        for folder in tqdm(self.get_list_of_folders(self.home_folder)):
            parent_folder = os.path.join(self.home_folder, folder)
            files = self.get_list_of_files_in_folder(parent_folder, limit=limit)
            if files:
                messages = self.parse_html(parent_folder, files)
                clear_messages = self.clear_messages(messages)
                result.append(clear_messages)
        return result

    @typechecked
    def parse_html(self, parent_folder: str, files: list) -> list:
        all_messages = []
        for file in files:
            with open(os.path.join(parent_folder, file), "rb") as f:
                soup = BeautifulSoup(f, "lxml")

            messages = []
            for message in soup.find_all("div", {"class": "message"}):
                message = message.text.strip()
                messages.append(message[message.find("\n") + 1 :])

            # Reverse the list to save the message sequence:
            all_messages.extend(messages[::-1])
        return all_messages

    @typechecked
    def clear_messages(self, all_messages: list) -> list:
        cleared_messages = []
        for message in all_messages:
            message = self._clear_message(message)
            if message:
                cleared_messages.append(message)

        return cleared_messages


class Data4Chatbot(Data4ML):
    def __init__(self, max_length: int = 10, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length

    @typechecked
    def make_data(self, limit=2) -> list:
        result = []
        for folder in tqdm(self.get_list_of_folders(self.home_folder)):
            parent_folder = os.path.join(self.home_folder, folder)
            files = self.get_list_of_files_in_folder(parent_folder, limit=limit)
            if files:
                messages = self.parse_html(parent_folder, files)
                clear_messages = self.clear_messages(messages)
                result.extend(self.get_pairs(clear_messages))
        return result

    @typechecked
    def parse_html(self, parent_folder: str, files: list) -> list:
        all_messages = []
        for file in files:
            with open(os.path.join(parent_folder, file), "rb") as f:
                soup = BeautifulSoup(f, "lxml")

            messages = []
            for message in soup.find_all("div", {"class": "message"}):
                message = message.text.strip()
                messages.append(message)

            # Reverse the list to save the message sequence:
            all_messages.extend(messages[::-1])
        return all_messages

    @typechecked
    def normalize_message(self, s: str) -> str:
        """Lowercase, trim, and remove non-letter characters"""

        s = s.lower().strip()
        s = re.sub("\n", ".", s)
        s = re.sub(r"([.!?])", r" \1", s)  # add space before `.`, `!` or `?`
        s = re.sub(r"[^а-яА-ЯёЁa-zA-Z.!?]+", r" ", s)  # remove non-letter characters
        s = re.sub(r"\s+", r" ", s).strip()
        return s

    @typechecked
    def _check_max_length(self, p: list) -> bool:
        """Return True if both sentences in a pair 'p' are underthe `self.max_length` threshold.
        """

        return (
            len(p[0].split(" ")) < self.max_length
            and len(p[1].split(" ")) < self.max_length
        )

    @typechecked
    def filter_pairs(self, pairs: list) -> list:
        """Filter pairs using filterPair condition."""

        return [pair for pair in pairs if self._check_max_length(pair)]

    @typechecked
    def get_pairs(self, messages: list) -> list:
        pairs = [[messages[i - 1], messages[i]] for i in range(1, len(messages))]
        return self.filter_pairs(pairs)

    @typechecked
    def check_last_character(self, messages: list) -> None:
        if not messages[-1][-1].isalnum():
            messages[-1] += " . "

    @typechecked
    def clear_messages(self, all_messages: list) -> list:
        messages = []

        # Who start the dialog:
        last_author = all_messages[0][: all_messages[0].find(",")]
        for message in all_messages:
            author = message[: message.find(",")]
            message = message[message.find("\n") + 1 :]
            clear_message = self.normalize_message(self._clear_message(message))
            if clear_message:

                if author == last_author:  # still one message
                    if messages:
                        messages[-1] += " \n " + clear_message
                    else:  # for the first iteration
                        messages.append(clear_message)
                else:  # if author change
                    messages.append(clear_message)

                last_author = author

            # TODO:
            """
            Продумать насчёт пустых сообщений. Например, это сообщение:
                Вы: Привет, скинь фотку.
                Они: [Фото#1]
                Вы: Спасибо
                Они: [Фото#2]
                Вы: Большое спасибо!

            Очистится в:
                Вы: Привет, скинь фотку.
                Вы: Спасибо
                Вы: Большое спасибо!

            Если менять автора каждый раз, то получится как выше, а если не менять, то::
                Вы: Привет, скинь фотку. Спасибо. Большое спасибо!

            И что вот лучше?
            """

            # TODO2:
            """
            1. Использовать неронку или ещё что-нибудь, чтобы генерировать пунктуацию уже после того, как мы сделали предсказание
            2. NER - увеличивать буквы у имён

            3. Нужны ли нам знаки вопроса и точки?
            """
        return messages
