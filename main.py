# NCM Downloader
# Author: Caleb@xxynet

# 请打开config.ini配置文件配置相应信息

# pyinstaller -F main.py -i music.ico

import metadata

from utils import *
from api import NCMApi
from ncmdump import ncm_dump

proj_logo = Fore.GREEN + """  _   _  _____ __  __   _____   ______          ___   _ _      ____          _____  ______ _____  
 | \ | |/ ____|  \/  | |  __ \ / __ \ \        / / \ | | |    / __ \   /\   |  __ \|  ____|  __ \ 
 |  \| | |    | \  / | | |  | | |  | \ \  /\  / /|  \| | |   | |  | | /  \  | |  | | |__  | |__) |
 | . ` | |    | |\/| | | |  | | |  | |\ \/  \/ / | . ` | |   | |  | |/ /\ \ | |  | |  __| |  _  / 
 | |\  | |____| |  | | | |__| | |__| | \  /\  /  | |\  | |___| |__| / ____ \| |__| | |____| | \ \ 
 |_| \_|\_____|_|  |_| |_____/ \____/   \/  \/   |_| \_|______\____/_/    \_\_____/|______|_|  \_\\
""" + Style.RESET_ALL


class Song:

    def __init__(self, song_id):
        self.song_id: int = song_id
        self.name: str
        self.artists = None
        self.cover: str  # PicUrl
        self.album: str  # album name
        self.olrc = None
        self.tlrc = None
        self.is_succeed: bool = False
        self._get_song_info()

    def _get_song_info(self):
        song_info = api.get_song_info(self.song_id)
        if song_info['status'] == "success":
            self.name = song_info['name']
            self.artists = song_info['artists']
            self.cover = song_info['picUrl']
            self.album = song_info['album_name']  # album name
            if global_config.lrc_enabled != "0":
                try:
                    self.olrc, self.tlrc = api.get_lyrics(self.song_id)
                except Exception as e:
                    formatted_print('e', e)
        else:
            formatted_print('e', "获取歌曲信息失败！")

    def download_song(self, playlist_name):
        name = safe_name(self.name) # illegal_chars = r'[\\/*?:"<>|]'
        id = self.song_id
        artists_list = self.artists
        artists = ''
        for artist in artists_list:
            artists += safe_name(artist) + ","
        artists = artists[:-1]

        cover = self.cover
        album = self.album
        full_path = generate_file_path(global_config.music_path, name, artists, playlist_name) + ".mp3"
        if not os.path.exists(full_path):
            self.music_down(playlist_name, id, name, artists)
            if os.path.exists(full_path):
                metadata.meta_data(full_path, name, artists_list, album, cover)
        else:
            self.is_succeed = True
            formatted_print('ok', f"{generate_file_name(name, artists)}.mp3  already exists")

    def music_down(self, playlist_name, id, name, artists):

        full_path = generate_file_path(global_config.music_path, name, artists, playlist_name)

        print(f"Downloading {generate_file_name(name, artists)}.mp3", end='\r')
        try:
            is_api_succeed, audio_data = api.get_mp3_data(id)

            if is_api_succeed:
                with open(f"{full_path}.mp3", "wb") as file:
                    file.write(audio_data.content)
                self.is_succeed = True
                formatted_print('ok', f"{generate_file_name(name, artists)}.mp3")

                # download lyrics
                if global_config.lrc_enabled == '1':
                    merged_lrc = metadata.merge_lrc(self.olrc, self.tlrc)
                    with open(f"{full_path}.lrc", "w",
                              encoding='utf-8') as file:
                        file.write(merged_lrc)
                elif global_config.lrc_enabled == '2' and is_api_succeed:
                    merged_lrc = metadata.merge_lrc(self.olrc, self.tlrc)
                    metadata.builtin_lyrics(f"{full_path}.mp3", merged_lrc)
            else:  # VIP
                formatted_print('e', f"{generate_file_name(name, artists)}.mp3")
        except Exception as e:
            formatted_print('e', e)


class Playlist:

    def __init__(self, playlist_id, download_path):
        self.playlist_id: int = playlist_id
        self.download_path: str = download_path
        self.playlist_name: str
        self.playlist_song_amount: int
        self.song_ids: list[int] = []
        self.song_objects: list[Song] = []
        self.creator: str

        self.success_num: int = 0

        self._init_playlist()
        self._create_playlist_dir()

    def _init_playlist(self):
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                self._fetch_playlist_data()
                break
            except Exception as e:
                formatted_print('e', f"获取歌曲信息异常，错误信息：{str(e)}，正在重试")

    def _fetch_playlist_data(self):
        playlist_info = api.get_playlist_info(self.playlist_id)

        if playlist_info['status'] == "success":
            self.playlist_name = safe_name(playlist_info['name'])  # illegal_chars = r'[\\/*?:"<>|]'
            self.playlist_id = playlist_info['id']
            self.playlist_song_amount = playlist_info['song_num']
            self.creator = playlist_info['creator']
            self.song_ids = playlist_info['trackIds']
        else:
            formatted_print('e', f"请求失败！状态码：{playlist_info['status']}")

    # def _create_song_objects(self, song_id):
    #     self.song_objects.append(Song(song_id))

    def _create_playlist_dir(self):
        try:
            if not os.path.exists(self.download_path + "/" + self.playlist_name):
                os.mkdir(self.download_path + "/" + self.playlist_name)
        except Exception as e:
            formatted_print('e', f"创建歌单文件夹失败! 错误信息：{str(e)}")
            time.sleep(3)
            sys.exit(1)

    def download_playlist(self):
        print("==================下载前确认==================")
        print(f"歌单名称：{self.playlist_name}    歌单ID：{self.playlist_id}")
        print(f"歌曲数量：{self.playlist_song_amount}      创建者：{self.creator}")
        input("按回车键继续")

        for i in range(self.playlist_song_amount):
            song_id = self.song_ids[i]
            song = Song(song_id)
            song.download_song(self.playlist_name)
            if song.is_succeed:
                self.success_num += 1

        print(f"Total: {self.playlist_song_amount} Success: {self.success_num}")
        input("按回车键退出")
        time.sleep(0.5)
        sys.exit(1)


def choice_download_playlist():
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

        playlist = Playlist(playlist_id, global_config.music_path)
        playlist.download_playlist()
    except Exception as e:
        formatted_print('e', f"发生错误：{str(e)}")
        time.sleep(3)
        sys.exit(1)


def choice_ncm_to_mp3():
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


def choice_music_metadata():
    music_file_path = input("请输需要刮削的音乐文件夹路径：")
    if music_file_path:
        formatted_print('i', "开始刮削")
        mp3_files = [f for f in os.listdir(music_file_path) if f.endswith(".mp3")]
        for mp3_file in mp3_files:
            song_info = api.get_song_info_by_keyword(mp3_file[:-4])
            is_succeed = song_info['status']
            if is_succeed == "success":
                metadata.meta_data(music_file_path + "/" + mp3_file, song_info["name"], song_info["artists"],
                                   song_info["album_name"], song_info["picUrl"])
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


def main():
    print("==================模式选择==================")
    print("1.下载歌单                  2.ncm文件转mp3文件")
    print("3.音乐刮削")
    choice = input("请输入选项：")
    if choice == "1":
        choice_download_playlist()
    elif choice == "2":
        choice_ncm_to_mp3()
    elif choice == "3":
        choice_music_metadata()


if __name__ == '__main__':
    # print project logo
    print(proj_logo)

    # print project info
    print("Github: https://github.com/xxynet/NCM-Downloader")
    print("Docs: https://docs.xuxiny.top/ncm/")
    print("Made by Caleb XXY with ❤")
    print(f"当前版本：{VERSION}")

    global_config = Config()

    if global_config.detect_update:
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

    api = NCMApi(global_config.cookie)

    main()
