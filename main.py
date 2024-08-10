# NCM Downloader
# Author: Caleb@xxynet

# 请打开config.ini配置文件配置相应信息

# pyinstaller -F main.py -i music.ico

import requests
import jsonpath
import os
import sys
import time
import configparser
from colorama import init, Fore, Style
import metadata

config_file = '''[output]

#设置歌单输出路径，如果为空则默认为程序所在目录（路径无需引号包裹）
path = 

#0->歌名-歌手 1->歌手-歌名 2->歌名（暂时无效）
filename = 0

#是否下载歌词 1 -> 下载LRC歌词文件  2 -> 内嵌歌词  0 -> False
lrc = 0
'''

init() # colorma


if not os.path.exists('config.ini'):
    with open("config.ini", "w", encoding="utf-8") as config:
        config.write(config_file)
    print("首次运行，已自动创建config.in文件")
if not os.path.exists('cookie.txt'):
    with open("cookie.txt", "w", encoding="utf-8") as cookie_value:
        cookie_value.write("")
    print("首次运行，已自动创建cookie.txt文件")

try:
    config = configparser.RawConfigParser()
    config.read('config.ini',encoding='utf-8')
    path = config.get('output','path')
    if path == '':
        path = os.getcwd()
    filename = config.get('output','filename')

    bool_lrc = config.get('output','lrc')

    with open("cookie.txt", "r") as cookie_file:
        cookie = cookie_file.read()

except Exception as e:
    print(e)
    print("读取配置文件失败")
    time.sleep(3)
    sys.exit(1)


# class Song:
#     def __init__(self, name, id, artists, url, cover, album, lyrics=None):
#         self.name = name
#         self.track_id = id
#         self.artists = artists
#         self.url = url
#         self.cover = cover
#         self.album = album
#         self.lyrics = lyrics


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

    def fetch_playlist_data(self):

        response = requests.get("https://music.163.com/api/playlist/detail?id=" + str(self.playlist_id), headers=self.headers)

        if response.ok:
            data = response.json()
            try:
                self.tracks = jsonpath.jsonpath(data, "$.[tracks]")[0]
                self.playlist_song_amount = len(self.tracks)
            except:
                print("获取歌曲信息异常，请重新运行本程序")
                time.sleep(3)
                sys.exit(1)

            try:
                self.playlist_name = jsonpath.jsonpath(data, "$.['name']")[0]
            except:
                print("获取歌单名称失败！")
                time.sleep(3)
                sys.exit(1)
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

    def MusicDown(self, id, name, artists):
        global olyric, tlyric, content_type
        print("Downloading " + name + " - " + artists + ".mp3", end='\r')
        try:
            audio_data = requests.get('https://music.163.com/song/media/outer/url?id=' + str(id), headers=self.headers)
            content_type = audio_data.headers.get('Content-Type')
            lrc = requests.get('https://music.163.com/api/song/lyric?id=' + str(id) + '&lv=1&kv=1&tv=-1')
            olyric = jsonpath.jsonpath(lrc.json(), "$.lrc.lyric")[0]
            tlyric = jsonpath.jsonpath(lrc.json(), "$.tlyric.lyric")[0]
        except Exception as e:
            print("出现异常：" + str(e))

        if "text/html" not in content_type:
            with open(path + "/" + self.playlist_name + "/" + name + " - " + artists + ".mp3", "wb") as file:
                file.write(audio_data.content)
            print("[" + Fore.GREEN + "OK" + Style.RESET_ALL + "] " + name + " - " + artists + ".mp3")
        else:  # VIP
            print("[" + Fore.RED + "E" + Style.RESET_ALL + "] " + name + " - " + artists + ".mp3")
        if bool_lrc == '1':
            merged_lrc = metadata.merge_lrc(olyric, tlyric)
            with open(path + "/" + self.playlist_name + "/" + name + " - " + artists + ".lrc", "w",
                      encoding='utf-8') as file:
                file.write(merged_lrc)
        elif bool_lrc == '2' and (not "text/html" in content_type):
            merged_lrc = metadata.merge_lrc(olyric, tlyric)
            metadata.builtin_lyrics(path + "/" + self.playlist_name + "/" + name + " - " + artists + ".mp3", merged_lrc)

    def download_music(self, index):
        name = jsonpath.jsonpath(self.tracks[index], "$['name']")[0]
        id = jsonpath.jsonpath(self.tracks[index], "$['id']")[0]
        artists_info = jsonpath.jsonpath(self.tracks[index], "$['artists']")[0]
        artists_num = len(artists_info)
        artists_list = []
        artists = ''
        for j in range(artists_num):
            artist_name = jsonpath.jsonpath(self.tracks[index], "$['artists'][" + str(j) + "]['name']")[0]
            artists_list.append(artist_name)
            artists += artist_name + ","
        artists = artists[:-1]

        cover = jsonpath.jsonpath(self.tracks[index], "$['album']['picUrl']")[0]
        album = jsonpath.jsonpath(self.tracks[index], "$[album][name]")[0]
        full_path = path + "/" + self.playlist_name + "/" + name + " - " + artists + ".mp3"
        if not os.path.exists(full_path):
            self.MusicDown(id, name, artists)
            if os.path.exists(full_path):
                metadata.MetaData(full_path, name, artists_list, album, cover)
        else:
            print(name + " - " + artists + ".mp3  " + "already exist")



def main():
    try:
        Playlist_id = int(input("歌单id："))
    except:
        print("非法输入！")
        time.sleep(3)
        sys.exit(1)

    downloader = Playlist(Playlist_id, path)
    downloader.fetch_playlist_data()
    downloader.create_playlist_dir()

    for i in range(downloader.playlist_song_amount):
        downloader.download_music(i)


if __name__ == '__main__':
    main()


# name: $.[tracks][0]['name']
# ID： $.[tracks][0]['id']
# 封面：$.[tracks][0]['album']['picUrl']
# 歌手：$.[tracks][0]['artists'][0]['name']
# 专辑：$.[tracks][0][album][name]
# 歌词：https://music.163.com/api/song/lyric?id={歌曲ID}&lv=1&kv=1&tv=-1