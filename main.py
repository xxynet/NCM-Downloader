# NCM Downloader
# Author: Caleb@xxynet

# 请打开config.ini配置文件配置相应信息

# pyinstaller -F main.py -i music.ico

import requests
import jsonpath
import re
import os
import sys
import time
import configparser
from colorama import init, Fore, Style
import metadata

from api import NCMApi
from config import VERSION, config_file
from ncmdump import ncm_dump


def formatted_print(type, text):
    if type == 'e':
        print("[" + Fore.RED + "E" + Style.RESET_ALL + "] " + text)
    elif type == 'ok':
        print("[" + Fore.GREEN + "OK" + Style.RESET_ALL + "] " + text)
    elif type == 'i':
        print("[" + Fore.CYAN + "INFO" + Style.RESET_ALL + "] " + text)
    elif type == 'w':
        print("[" + Fore.YELLOW + "WARN" + Style.RESET_ALL + "] " + text)


init() # colorma
print(Fore.GREEN + "  _   _  _____ __  __   _____   ______          ___   _ _      ____          _____  ______ _____  ")
print(" | \ | |/ ____|  \/  | |  __ \ / __ \ \        / / \ | | |    / __ \   /\   |  __ \|  ____|  __ \ ")
print(" |  \| | |    | \  / | | |  | | |  | \ \  /\  / /|  \| | |   | |  | | /  \  | |  | | |__  | |__) |")
print(" | . ` | |    | |\/| | | |  | | |  | |\ \/  \/ / | . ` | |   | |  | |/ /\ \ | |  | |  __| |  _  / ")
print(" | |\  | |____| |  | | | |__| | |__| | \  /\  /  | |\  | |___| |__| / ____ \| |__| | |____| | \ \ ")
print(" |_| \_|\_____|_|  |_| |_____/ \____/   \/  \/   |_| \_|______\____/_/    \_\_____/|______|_|  \_\\" + Style.RESET_ALL)
print("Github: https://github.com/xxynet/NCM-Downloader")
print("Docs: https://ncm.xuxiny.top/")
print("Programmed by Caleb XXY")
print(f"当前版本：{VERSION}")

if not os.path.exists('config.ini'):
    with open("config.ini", "w", encoding="utf-8") as config:
        config.write(config_file)
    formatted_print('i', "首次运行，已自动创建config.ini文件")
if not os.path.exists('cookie.txt'):
    with open("cookie.txt", "w", encoding="utf-8") as cookie_value:
        cookie_value.write("")
    formatted_print('i', "首次运行，已自动创建cookie.txt文件")


def generate_file_path(name, artists, playlist_name):
    return path + "/" + playlist_name + "/" + name + " - " + artists


def safe_name(origin_name):
    illegal_chars = r'[\\/*?:"<>|\x00-\x1f]'
    file_name = re.sub(illegal_chars, "_", origin_name)
    return file_name


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


try:
    config = configparser.RawConfigParser()
    config.read('config.ini',encoding='utf-8')
    path = config.get('output','path')
    if path == '':
        path = os.getcwd()
    filename = config.get('output','filename')

    bool_lrc = config.get('output','lrc')

    detect_update = config.get('settings','detect-update')

    with open("cookie.txt", "r") as cookie_file:
        cookie = cookie_file.read().strip()

    if cookie:
        if is_cookie_format_valid(cookie):
            formatted_print('ok', "Cookie已注入")
        else:
            formatted_print('e', "不合法的Cookie")
            time.sleep(3)
            sys.exit(1)
    else:
        formatted_print('w', "未注入Cookie")

except Exception as e:
    print(e)
    formatted_print('e', "读取配置文件失败")
    time.sleep(3)
    sys.exit(1)

if detect_update == "1":
    formatted_print('i', "正在检查更新...")
    try:
        release_info = get_latest_release("xxynet", "NCM-Downloader")
        latest_version = release_info["tag_name"]
        release_url = release_info["html_url"]
        if latest_version:
            if latest_version != VERSION:
                formatted_print('i', f"发现新版本：{latest_version}\n前往更新：{release_url}")
            else:
                formatted_print('i', "已是最新版本！")
    except Exception as e:
        formatted_print('e', e)

success_num = 0

api = NCMApi(cookie)


class Song:

    def __init__(self, song_id):
        self.song_id = song_id
        self.name = None
        self.artists = None
        self.cover = None  # PicUrl
        self.album = None  # album name
        self.olrc = None
        self.tlrc = None
        self.get_song_info()

    def get_song_info(self):
        song_info = api.get_song_info(self.song_id)
        if song_info['status'] == "success":
            self.name = song_info['name']
            self.artists = song_info['artists']
            self.cover = song_info['picUrl']
            self.album = song_info['album_name']  # album name
            if bool_lrc != "0":
                try:
                    self.olrc, self.tlrc = api.get_lyrics(self.song_id)
                except Exception as e:
                    formatted_print('e', e)
        else:
            formatted_print('e', "获取歌曲信息失败！")

    def Download(self, playlist):
        global success_num
        name = safe_name(self.name) # illegal_chars = r'[\\/*?:"<>|]'
        id = self.song_id
        artists_list = self.artists
        artists = ''
        for artist in artists_list:
            artists += safe_name(artist) + ","
        artists = artists[:-1]

        cover = self.cover
        album = self.album
        full_path = generate_file_path(name, artists, playlist.playlist_name) + ".mp3"
        if not os.path.exists(full_path):
            self.music_down(playlist, id, name, artists)
            if os.path.exists(full_path):
                metadata.meta_data(full_path, name, artists_list, album, cover)
        else:
            success_num += 1
            formatted_print('ok', name + " - " + artists + ".mp3  " + "already exist")

    def music_down(self, playlist, id, name, artists):
        global success_num
        print("Downloading " + name + " - " + artists + ".mp3", end='\r')
        try:
            is_succeed, audio_data = api.get_mp3_data(id)

            if is_succeed:
                with open(generate_file_path(name, artists, playlist.playlist_name)+".mp3", "wb") as file:
                    file.write(audio_data.content)
                success_num += 1
                formatted_print('ok', name + " - " + artists + ".mp3")
            else:  # VIP
                formatted_print('e', name + " - " + artists + ".mp3")
        except Exception as e:
            formatted_print('e', e)
        if bool_lrc == '1':
            merged_lrc = metadata.merge_lrc(self.olrc, self.tlrc)
            with open(generate_file_path(name, artists, playlist.playlist_name) + ".lrc", "w",
                      encoding='utf-8') as file:
                file.write(merged_lrc)
        elif bool_lrc == '2' and is_succeed:
            merged_lrc = metadata.merge_lrc(self.olrc, self.tlrc)
            metadata.builtin_lyrics(generate_file_path(name, artists, playlist.playlist_name) + ".mp3", merged_lrc)


class Playlist:

    def __init__(self, playlist_id, download_path):
        self.playlist_id = playlist_id
        self.download_path = download_path
        self.playlist_name = None
        self.playlist_song_amount = None
        self.ids = None
        self.creator = None

        self.fetch_playlist_data()
        self.create_playlist_dir()

    def fetch_playlist_data(self):
        try:
            playlist_info = api.get_playlist_info(self.playlist_id)
        except:
            formatted_print('e', f"获取歌曲信息异常，正在重试")
            global attempts
            attempts += 1
            time.sleep(1)
            download(self.playlist_id)

        if playlist_info['status'] == "success":
            self.playlist_name = safe_name(playlist_info['name']) # illegal_chars = r'[\\/*?:"<>|]'
            self.playlist_id = playlist_info['id']
            self.playlist_song_amount = playlist_info['song_num']
            self.creator = playlist_info['creator']
            self.ids = playlist_info['trackIds']

            print("==================下载前确认==================")
            print(f"歌单名称：{self.playlist_name}    歌单ID：{self.playlist_id}")
            print(f"歌曲数量：{self.playlist_song_amount}      创建者：{self.creator}")
            input("按回车键继续")
        else:
            formatted_print('e', f"请求失败！状态码：{playlist_info['status']}")
            sys.exit(1)

    def create_playlist_dir(self):
        try:
            if not os.path.exists(self.download_path + "/" + self.playlist_name):
                os.mkdir(self.download_path + "/" + self.playlist_name)
        except Exception as e:
            formatted_print('e',f"创建歌单文件夹失败! 错误信息：{str(e)}")
            time.sleep(3)
            sys.exit(1)


def download(playlist_id):
    global attempts, success_num
    if attempts <= 3:
        downloader = Playlist(playlist_id, path)

        for i in range(downloader.playlist_song_amount):
            song_id = downloader.ids[i]
            song = Song(song_id)

            song.Download(downloader)

        print(f"Total: {downloader.playlist_song_amount} Success: {success_num}")
        input("按回车键退出")
        time.sleep(0.5)
        sys.exit(1)
    else:
        formatted_print('e', "获取失败，请重新运行本程序")
        time.sleep(3)
        sys.exit(1)


attempts = 1


def main():
    print("==================模式选择==================")
    print("1.下载歌单                  2.ncm文件转mp3文件")
    print("3.音乐刮削")
    choice = input("请输入选项：")
    if choice == "1":
        try:
            list_url = input("歌单URL或ID：")
            if list_url.isdigit():
                playlist_id = list_url
            else:
                ids = re.findall(r'[?&]id=(\d+)', list_url)
                if ids:
                    playlist_id = ids[0]
                else:
                    formatted_print('e', "未识别到有效的输入！")
                    time.sleep(3)
                    sys.exit(1)
        except:
            time.sleep(3)
            sys.exit(1)

        download(playlist_id)
    elif choice == "2":
        ncm_file_path = input("请输入ncm文件所在文件夹路径（留空则使用E:/CloudMusic/VipSongsDownload）：")
        formatted_print('i', "开始转换")
        if ncm_file_path:
            converted_files = ncm_dump(ncm_file_path)
        else:
            converted_files = ncm_dump()
        formatted_print('i', "已转换文件：")
        print(converted_files)
        input("按回车键退出")
        time.sleep(0.5)
        sys.exit(1)
    elif choice == "3":
        music_file_path = input("请输需要刮削的音乐文件夹路径：")
        if music_file_path:
            formatted_print('i', "开始刮削")
            mp3_files = [f for f in os.listdir(music_file_path) if f.endswith(".mp3")]
            for mp3_file in mp3_files:
                song_info = api.get_song_info_by_keyword(mp3_file[:-4])
                is_succeed = song_info['status']
                if is_succeed == "success":
                    metadata.meta_data(music_file_path+"/"+mp3_file, song_info["name"], song_info["artists"], song_info["album_name"], song_info["picUrl"])
                    formatted_print('ok', mp3_file)
                else:
                    formatted_print('e', mp3_file)
            input("按回车键退出")
            time.sleep(0.5)
            sys.exit(1)
        else:
            formatted_print('e', "请输入有效的路径")
            time.sleep(3)
            sys.exit(1)


if __name__ == '__main__':
    main()