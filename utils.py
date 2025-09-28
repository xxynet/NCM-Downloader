from colorama import init, Fore, Style
from typing import Union
import configparser
import sys
import time
import requests
import os
import re

from config import VERSION, config_file

init() # colorma


def formatted_print(info_type, text, overwrite=False):

    output_text = ""
    if info_type == 'e':
        output_text = "[" + Fore.RED + "E" + Style.RESET_ALL + "] " + text
    elif info_type == 'ok':
        output_text = "[" + Fore.GREEN + "OK" + Style.RESET_ALL + "] " + text
    elif info_type == 'i':
        output_text = "[" + Fore.CYAN + "INFO" + Style.RESET_ALL + "] " + text
    elif info_type == 'w':
        output_text = "[" + Fore.YELLOW + "WARN" + Style.RESET_ALL + "] " + text

    if overwrite:
        print(f"\r{output_text}")
    else:
        print(output_text)


def safe_name(origin_name):
    illegal_chars = r'[\\/*?:"<>|\x00-\x1f]'
    file_name = re.sub(illegal_chars, "_", origin_name)
    return file_name


def generate_file_name(name, artists):
    if global_config.filename_format == "0":
        return f"{name} - {artists}"
    elif global_config.filename_format == "1":
        return f"{artists} - {name}"


def generate_file_path(base_path, name, artists, playlist_name):
    if global_config.filename_format == "0":
        return f"{base_path}/{playlist_name}/{name} - {artists}"
    elif global_config.filename_format == "1":
        return f"{base_path}/{playlist_name}/{artists} - {name}"


def is_cookie_format_valid(cookie_str: str) -> bool:
    if not cookie_str:
        return False

    parts = cookie_str.split(';')
    for part in parts:
        if '=' not in part:
            return False
        key, _ = part.strip().split('=', 1)
        if not key.strip():
            return False
    return True


def get_latest_release(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    response = requests.get(url, timeout=5)

    if response.status_code == 200:
        data = response.json()
        return {
            "tag_name": data["tag_name"],
            # "name": data["name"],
            # "body": data["body"],
            "html_url": data["html_url"],
            # "published_at": data["published_at"]
        }
    else:
        formatted_print('e', f"检查更新失败，状态码：{response.status_code}")
        return None


class Config:
    def __init__(self):
        self.music_path: Union[str, None] = None
        self.ncm_path: Union[str, None] = None
        self.filename_format: Union[str, None] = None
        self.lrc_enabled: Union[str, None] = None
        self.detect_update: Union[bool, None] = None

        self.cookie: Union[str, None] = None

        self._check_config_file()
        self._get_config()

    @staticmethod
    def _check_config_file():
        # setting up config files
        is_first_exec = False
        if not os.path.exists('config.ini'):
            is_first_exec = True
            with open("config.ini", "w", encoding="utf-8") as config:
                config.write(config_file)
            formatted_print('i', "首次运行，已自动创建config.ini文件")
        if not os.path.exists('cookie.txt'):
            is_first_exec = True
            with open("cookie.txt", "w", encoding="utf-8") as cookie_value:
                cookie_value.write("")
            formatted_print('i', "首次运行，已自动创建cookie.txt文件")
        if is_first_exec:
            formatted_print('i', "配置文件已准备好，请填写后重新运行本程序")
            time.sleep(5)
            sys.exit(1)

    def _get_config(self):
        """
        get config via config.ini
        """
        try:
            config = configparser.RawConfigParser()
            config.read('config.ini', encoding='utf-8')
            path = config.get('output', 'path')
            if path == '':
                self.music_path = os.getcwd()

            self.ncm_path = config.get('output', 'ncm_path')

            self.filename_format = config.get('output', 'filename')

            self.lrc_enabled = config.get('output', 'lrc')

            self.detect_update = True if config.get('settings', 'detect-update') == "1" else False

            with open("cookie.txt", "r") as cookie_file:
                self.cookie = cookie_file.read().strip()

            # if self.cookie:
            #     if is_cookie_format_valid(self.cookie):
            #         formatted_print('ok', "Cookie已注入")
            #     else:
            #         formatted_print('e', "不合法的Cookie")
            #         time.sleep(3)
            #         sys.exit(1)
            # else:
            #     formatted_print('w', "未注入Cookie")

        except Exception as e:
            print(e)
            formatted_print('e', "读取配置文件失败")
            time.sleep(3)
            sys.exit(1)


global_config = Config()
