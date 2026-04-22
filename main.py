# NCM Downloader
# Author: Caleb@xxynet

# 请打开config.ini配置文件配置相应信息

# pyinstaller -F main.py -i music.ico

from rich.panel import Panel
from rich.table import Table
from rich import box

import metadata

from utils import *
from api import NCMApi, VKeyApi
from ncmdump import dump as dump_ncm

proj_logo = r"""
  _   _  _____ __  __   _____   ______          ___   _ _      ____          _____  ______ _____  
 | \ | |/ ____|  \/  | |  __ \ / __ \ \        / / \ | | |    / __ \   /\   |  __ \|  ____|  __ \ 
 |  \| | |    | \  / | | |  | | |  | \ \  /\  / /|  \| | |   | |  | | /  \  | |  | | |__  | |__) |
 | . ` | |    | |\/| | | |  | | |  | |\ \/  \/ / | . ` | |   | |  | |/ /\ \ | |  | |  __| |  _  / 
 | |\  | |____| |  | | | |__| | |__| | \  /\  /  | |\  | |___| |__| / ____ \| |__| | |____| | \ \ 
 |_| \_|\_____|_|  |_| |_____/ \____/   \/  \/   |_| \_|______\____/_/    \_\_____/|______|_|  \_\\
"""


class Song:

    def __init__(self, playlist_name, song_id):
        self.playlist_name: str = playlist_name
        self.song_id: int = song_id
        self.name: str
        self.safe_name: str
        self.artists: list = []
        self.artists_str: str = ""
        self.cover: str  # PicUrl
        self.album: str  # album name
        self.olrc: str  # original lyrics
        self.tlrc: str  # translation lyrics
        self.full_path: str  # full path w/o extension
        self.success: bool = False
        self._get_song_info()

    def _get_song_info(self):
        song_info = api.get_song_info(self.song_id)
        if song_info['status'] == "success":
            self.name = song_info['name']
            self.safe_name = safe_name(self.name)  # illegal_chars = r'[\\/*?:"<>|]'

            self.artists = song_info['artists']

            for artist in self.artists:
                self.artists_str += safe_name(artist) + ","
            self.artists_str = self.artists_str[:-1]

            self.cover = song_info['picUrl']
            self.album = song_info['album_name']  # album name
            self.full_path = generate_file_path(global_config.music_path, self.safe_name, self.artists_str, self.playlist_name)
            if global_config.lrc_enabled != "0":
                try:
                    self.olrc, self.tlrc = api.get_lyrics(self.song_id)
                except Exception as e:
                    formatted_print('e', f"获取歌词时出错：{str(e)}")
        else:
            formatted_print('e', "获取歌曲信息失败！")

    def _download_audio(self):
        api_success, audio_data = api.get_mp3_data(self.song_id)

        if api_success:
            with open(f"{self.full_path}.mp3", "wb") as file:
                file.write(audio_data.content)
            self.success = True
            # download lyrics
            self._download_lyrics()
        else:  # VIP
            self.success = False

            # vkey api
            if global_config.v_key_enabled:
                formatted_print('i', "尝试使用第三方API解析...")
                song_info = v_key_api.get_song_info(self.song_id)
                if song_info:
                    audio_url = song_info.get('url')
                    audio_response = requests.get(audio_url)

                    with open(f"{self.full_path}.mp3", "wb") as file:
                        file.write(audio_response.content)
                    self.success = True
                    # download lyrics
                    self._download_lyrics()

    def _download_lyrics(self):
        if global_config.lrc_enabled == '1':
            merged_lrc = metadata.merge_lrc(self.olrc, self.tlrc)
            with open(f"{self.full_path}.lrc", "w",
                      encoding='utf-8') as file:
                file.write(merged_lrc)
        elif global_config.lrc_enabled == '2':
            merged_lrc = metadata.merge_lrc(self.olrc, self.tlrc)
            metadata.builtin_lyrics(f"{self.full_path}.mp3", merged_lrc)

    def download(self):
        file_name = generate_file_name(self.name, self.artists_str)
        if not os.path.exists(f"{self.full_path}.mp3"):
            with console.status(f"[cyan]Downloading {file_name}.mp3[/cyan]"):
                self._download_audio()
            if self.success:
                formatted_print('ok', f"{file_name}.mp3")
            else:
                formatted_print('e', f"{file_name}.mp3")
            if os.path.exists(f"{self.full_path}.mp3"):
                metadata.meta_data(f"{self.full_path}.mp3", self.name, self.artists, self.album, self.cover)
        else:
            self.success = True
            formatted_print('ok', f"{file_name}.mp3  already exists")


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
        table = Table(title="[bold green]下载前确认[/bold green]", box=box.ROUNDED, show_header=False, border_style="green")
        table.add_column("属性", style="cyan")
        table.add_column("值", style="green")
        table.add_row("歌单名称", self.playlist_name)
        table.add_row("歌单ID", str(self.playlist_id))
        table.add_row("歌曲数量", str(self.playlist_song_amount))
        table.add_row("创建者", self.creator)
        console.print(table)
        console.input("按回车键继续")

        formatted_print('i', "开始下载")

        for i in range(self.playlist_song_amount):
            song_id = self.song_ids[i]
            song = Song(self.playlist_name, song_id)
            song.download()
            if song.success:
                self.success_num += 1

        console.print(Panel(f"总计：[bold]{self.playlist_song_amount}[/bold] 首 | 成功：[bold green]{self.success_num}[/bold green] 首", title="[bold]下载结果[/bold]", border_style="green"))
        formatted_print('i', "下载结束")
        time.sleep(0.5)


def choice_download_playlist():
    try:
        list_url = console.input("[bold cyan]歌单URL或ID：[/bold cyan]")
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
    ncm_file_path = console.input("[bold cyan]请输入ncm文件所在文件夹路径（留空则使用配置文件中的默认路径）：[/bold cyan]")
    if not ncm_file_path:
        ncm_file_path = global_config.ncm_path
    ncm_files = [f for f in os.listdir(ncm_file_path) if f.endswith(".ncm")]
    if not ncm_files:
        formatted_print('i', "未找到ncm文件")
        return
    for file in ncm_files:
        filepath = f"{ncm_file_path}/{file}"
        with console.status(f"[cyan]Converting {file}[/cyan]"):
            try:
                dump_ncm(filepath)
                ok = True
            except Exception as e:
                ok = False
                error_msg = str(e)
        if ok:
            formatted_print('ok', file)
        else:
            formatted_print('e', file)
            console.print(f"[bold red]转换时发生错误：{error_msg}[/bold red]")
    formatted_print('i', "转换结束")
    time.sleep(0.5)


def choice_music_metadata():
    music_file_path = console.input("[bold cyan]请输需要刮削的音乐文件夹路径：[/bold cyan]")
    if music_file_path:
        mp3_files = [f for f in os.listdir(music_file_path) if f.endswith(".mp3")]
        if not mp3_files:
            formatted_print('i', "未找到mp3文件")
            return
        for mp3_file in mp3_files:
            with console.status(f"[cyan]Scraping {mp3_file}[/cyan]"):
                try:
                    song_info = api.get_song_info_by_keyword(mp3_file[:-4])
                    api_success = song_info['status']
                    if api_success == "success":
                        ok = metadata.meta_data(music_file_path + "/" + mp3_file, song_info["name"], song_info["artists"],
                                           song_info["album_name"], song_info["picUrl"])
                    else:
                        ok = False
                        err = "未匹配到歌曲"
                except Exception as e:
                    ok = False
                    err = str(e)
            if ok:
                formatted_print('ok', mp3_file)
            else:
                formatted_print('e', f"{mp3_file} ({err})")
        formatted_print('i', "刮削结束")
        time.sleep(0.5)
    else:
        formatted_print('e', "请输入有效的路径")
        time.sleep(3)
        sys.exit(1)


def main():
    while True:
        table = Table(title="[bold blue]模式选择[/bold blue]", box=box.ROUNDED, show_header=False, border_style="blue")
        table.add_column("选项", style="cyan", justify="center")
        table.add_column("功能", style="green")
        table.add_row("1", "下载歌单")
        table.add_row("2", "ncm文件转mp3文件")
        table.add_row("3", "音乐刮削")
        console.print(table)
        choice = console.input("[bold cyan]请输入选项：[/bold cyan]")
        if choice == "1":
            choice_download_playlist()
        elif choice == "2":
            choice_ncm_to_mp3()
        elif choice == "3":
            choice_music_metadata()


if __name__ == '__main__':
    # print project logo
    console.print(Panel(f"[bold green]{proj_logo}[/bold green]", border_style="green"))

    # print project info
    info_text = f"""[link=https://github.com/xxynet/NCM-Downloader]GitHub: https://github.com/xxynet/NCM-Downloader[/link]
[link=https://docs.xuxiny.top/ncm/]Docs: https://docs.xuxiny.top/ncm/[/link]
Made by Caleb XXY with [red]❤[/red]
当前版本：[bold cyan]{VERSION}[/bold cyan]"""
    console.print(Panel(info_text, title="[bold]关于[/bold]", border_style="cyan"))

    # global_config = Config()

    # update
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
            formatted_print('e', str(e))

    # cookie
    if global_config.cookie:
        if is_cookie_format_valid(global_config.cookie):
            formatted_print('ok', "Cookie已注入")
        else:
            formatted_print('e', "不合法的Cookie")
            time.sleep(3)
            sys.exit(1)
    else:
        formatted_print('w', "未注入Cookie")

    api = NCMApi(global_config.cookie)
    v_key_api = VKeyApi()

    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]用户中断，程序退出[/bold yellow]")
        sys.exit(0)
