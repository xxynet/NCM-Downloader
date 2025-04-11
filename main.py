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


def formatted_print(type, text):
    if type == 'e':
        print("[" + Fore.RED + "E" + Style.RESET_ALL + "] " + text)
    elif type == 'ok':
        print("[" + Fore.GREEN + "OK" + Style.RESET_ALL + "] " + text)
    elif type == 'i':
        print("[" + Fore.CYAN + "INFO" + Style.RESET_ALL + "] " + text)
    elif type == 'w':
        print("[" + Fore.YELLOW + "WARN" + Style.RESET_ALL + "] " + text)


version = 'v1.8.0'

config_file = '''[output]

#设置歌单输出路径，如果为空则默认为程序所在目录（路径无需引号包裹）
path = 

#0->歌名-歌手 1->歌手-歌名 2->歌名（暂时无效）
filename = 0

#是否下载歌词 1 -> 下载LRC歌词文件  2 -> 内嵌歌词  0 -> False
lrc = 0

[settings]

#是否检查更新，如果出现问题可尝试将其改为0禁用自动更新
detect-update = 1
'''

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
print(f"当前版本：{version}")


if not os.path.exists('config.ini'):
    with open("config.ini", "w", encoding="utf-8") as config:
        config.write(config_file)
    formatted_print('i', "首次运行，已自动创建config.ini文件")
if not os.path.exists('cookie.txt'):
    with open("cookie.txt", "w", encoding="utf-8") as cookie_value:
        cookie_value.write("")
    formatted_print('i', "首次运行，已自动创建cookie.txt文件")


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
        cookie = cookie_file.read()

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
    print("读取配置文件失败")
    time.sleep(3)
    sys.exit(1)

if detect_update == "1":
    formatted_print('i', "正在检查更新...")
    try:
        release_info = get_latest_release("xxynet", "NCM-Downloader")
        latest_version = release_info["tag_name"]
        release_url = release_info["html_url"]
        if latest_version:
            if latest_version != version:
                formatted_print('i', f"发现新版本：{latest_version}\n前往更新：{release_url}")
            else:
                formatted_print('i', "已是最新版本！")
    except Exception as e:
        formatted_print('e', e)

success_num = 0


class Song:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67',
        'Cookie': cookie,
        'Origin': 'https://music.163.com/',
        'Referer': 'https://music.163.com/'
    }

    def __init__(self, track):
        self.track = track
        self.name = track['name']
        self.track_id = track['id']
        self.artists = [artist["name"] for artist in track.get("artists", [])]
        self.cover = track['album'].get('picUrl')
        self.album = track['album'].get('name')

        if bool_lrc != "0":
            try:
                lrc = requests.get(f"https://music.163.com/api/song/lyric?id={self.track_id}&lv=1&kv=1&tv=-1").json()

                self.olrc = lrc['lrc'].get('lyric')
                if 'tlyric' in lrc:
                    self.tlrc = lrc['tlyric'].get('lyric')
                else:
                    self.tlrc = None
            except Exception as e:
                formatted_print('e', e)

    def Download(self, playlist):
        name = self.name
        id = self.track_id
        artists_list = self.artists
        artists = ''
        for j in artists_list:
            artists += j + ","
        artists = artists[:-1]

        cover = self.cover
        album = self.album
        full_path = path + "/" + playlist.playlist_name + "/" + name + " - " + artists + ".mp3"
        if not os.path.exists(full_path):
            self.MusicDown(playlist, id, name, artists)
            if os.path.exists(full_path):
                metadata.MetaData(full_path, name, artists_list, album, cover)
        else:
            print(name + " - " + artists + ".mp3  " + "already exist")

    def MusicDown(self, playlist, id, name, artists):
        global success_num
        print("Downloading " + name + " - " + artists + ".mp3", end='\r')
        try:
            audio_data = requests.get('https://music.163.com/song/media/outer/url?id=' + str(id), headers=self.headers)
            content_type = audio_data.headers.get('Content-Type')

            olyric = self.olrc
            tlyric = self.tlrc

            if "text/html" not in content_type:
                with open(path + "/" + playlist.playlist_name + "/" + name + " - " + artists + ".mp3", "wb") as file:
                    file.write(audio_data.content)
                success_num += 1
                # print
                formatted_print('ok', name + " - " + artists + ".mp3")
            else:  # VIP
                # print
                formatted_print('e', name + " - " + artists + ".mp3")
        except Exception as e:
            # print
            formatted_print('e', e)
        if bool_lrc == '1':
            merged_lrc = metadata.merge_lrc(olyric, tlyric)
            with open(path + "/" + playlist.playlist_name + "/" + name + " - " + artists + ".lrc", "w",
                      encoding='utf-8') as file:
                file.write(merged_lrc)
        elif bool_lrc == '2' and (not "text/html" in content_type):
            merged_lrc = metadata.merge_lrc(olyric, tlyric)
            metadata.builtin_lyrics(path + "/" + playlist.playlist_name + "/" + name + " - " + artists + ".mp3", merged_lrc)





class Playlist:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67',
        'Cookie': cookie,
        'Origin': 'https://music.163.com/',
        'Referer': 'https://music.163.com/'
    }

    def __init__(self, playlist_id, download_path):
        self.playlist_id = playlist_id
        self.download_path = download_path
        self.playlist_name = None
        self.playlist_song_amount = None
        self.tracks = []

        self.fetch_playlist_data()
        self.create_playlist_dir()

    def fetch_playlist_data(self):

        response = requests.get("https://music.163.com/api/playlist/detail?id=" + str(self.playlist_id), headers=self.headers)

        if response.ok:
            data = response.json()
            # print(data) # DEBUG
            try:
                self.tracks = jsonpath.jsonpath(data, "$.[tracks]")[0]
                self.playlist_song_amount = len(self.tracks)
            except:
                print("获取歌曲信息异常，正在重试")
                global attempts
                attempts += 1
                time.sleep(1)
                download(self.playlist_id)

            self.playlist_name = jsonpath.jsonpath(data, "$.['name']")[0]

            print("==================下载前确认==================")
            print(f"歌单名称：{self.playlist_name}    歌单ID：{self.playlist_id}")
            print(f"歌曲数量：{self.playlist_song_amount}")
            input("按回车键继续")
        else:
            print("请求失败！")
            sys.exit(1)

    def create_playlist_dir(self):
        try:
            if not os.path.exists(self.download_path + "/" + self.playlist_name):
                os.mkdir(path + "/" + self.playlist_name)
        except:
            print("创建歌单文件夹失败!")
            time.sleep(3)
            sys.exit(1)

def download(id):
    global attempts, success_num
    if attempts <=3:
        downloader = Playlist(id, path)

        for i in range(downloader.playlist_song_amount):
            song = Song(downloader.tracks[i])

            song.Download(downloader)

        print(f"Total: {downloader.playlist_song_amount} Success: {success_num}")
        input("按回车键退出")
    else:
        print("获取失败，请重新运行本程序")
        time.sleep(3)
        sys.exit(1)

attempts = 1

def main():
    try:
        list_url = input("歌单URL或ID：")
        if list_url.isdigit():
            playlist_id = list_url
        else:
            ids = re.findall(r'[?&]id=(\d+)', list_url)
            if ids:
                playlist_id = ids[0]
            else:
                print("未识别到有效的输入！")
                time.sleep(3)
                sys.exit(1)
    except:
        print("非法输入！")
        time.sleep(3)
        sys.exit(1)

    download(playlist_id)


if __name__ == '__main__':
    main()


# name: $.[tracks][0]['name']
# ID： $.[tracks][0]['id']
# 封面：$.[tracks][0]['album']['picUrl']
# 歌手：$.[tracks][0]['artists'][0]['name']
# 专辑：$.[tracks][0][album][name]
# 歌词：https://music.163.com/api/song/lyric?id={歌曲ID}&lv=1&kv=1&tv=-1