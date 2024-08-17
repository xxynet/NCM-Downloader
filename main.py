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

        lrc = requests.get(f"https://music.163.com/api/song/lyric?id={self.track_id}&lv=1&kv=1&tv=-1").json()

        self.olrc = lrc['lrc'].get('lyric')
        self.tlrc = lrc['tlyric'].get('lyric')

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
        audio_data = requests.get('https://music.163.com/song/media/outer/url?id=' + str(id), headers=self.headers)
        content_type = audio_data.headers.get('Content-Type')

        olyric = self.olrc
        tlyric = self.tlrc

        if "text/html" not in content_type:
            with open(path + "/" + playlist.playlist_name + "/" + name + " - " + artists + ".mp3", "wb") as file:
                file.write(audio_data.content)
            success_num += 1
            print("[" + Fore.GREEN + "OK" + Style.RESET_ALL + "] " + name + " - " + artists + ".mp3")
        else:  # VIP
            print("[" + Fore.RED + "E" + Style.RESET_ALL + "] " + name + " - " + artists + ".mp3")
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
    else:
        print("获取失败，请重新运行本程序")
        time.sleep(3)
        sys.exit(1)

attempts = 1

def main():
    try:
        Playlist_id = int(input("歌单id："))
    except:
        print("非法输入！")
        time.sleep(3)
        sys.exit(1)

    download(Playlist_id)


if __name__ == '__main__':
    main()


# name: $.[tracks][0]['name']
# ID： $.[tracks][0]['id']
# 封面：$.[tracks][0]['album']['picUrl']
# 歌手：$.[tracks][0]['artists'][0]['name']
# 专辑：$.[tracks][0][album][name]
# 歌词：https://music.163.com/api/song/lyric?id={歌曲ID}&lv=1&kv=1&tv=-1