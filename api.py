import requests
import jsonpath


class NCMApi:
    def __init__(self, cookie=""):
        self.cookie = cookie
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67',
            'Cookie': self.cookie,
            'Origin': 'https://music.163.com/',
            'Referer': 'https://music.163.com/'
        }

    def get_playlist_info(self, playlist_id):
        playlist_api_url = f"http://music.163.com/api/v6/playlist/detail?id={playlist_id}"
        resp = requests.get(playlist_api_url, headers=self.headers)
        if resp.ok:
            resp_json = resp.json()
            playlist_info = {
                'status': 'success',
                'name': jsonpath.jsonpath(resp_json,"$.playlist.name")[0],
                'id': jsonpath.jsonpath(resp_json,"$.playlist.id")[0],
                'creator': jsonpath.jsonpath(resp_json, "$.playlist.creator.nickname")[0],
                'trackIds': jsonpath.jsonpath(resp_json, "$.playlist.trackIds[*][id]"),
                'song_num': len(jsonpath.jsonpath(resp_json, "$.playlist.trackIds[*][id]"))
            }
        else:
            playlist_info = {
                'status': str(resp.status_code)
            }

        return playlist_info

    def get_song_info(self, song_id):
        song_api_url = f"http://music.163.com/api/song/detail/?ids=[{song_id}]"
        resp = requests.get(song_api_url, headers=self.headers)
        if resp.ok:
            resp_json = resp.json()
            song_info = {
                'status': 'success',
                'name': jsonpath.jsonpath(resp_json,"$.songs[0].name")[0],
                'artists': jsonpath.jsonpath(resp_json, "$.songs[0].artists[*].name"),
                'album_name': jsonpath.jsonpath(resp_json, "$.songs[0].album.name")[0],
                'picUrl': jsonpath.jsonpath(resp_json, "$.songs[0].album.picUrl")[0],
            }
        else:
            song_info = {
                'status': str(resp.status_code)
            }

        return song_info

    def get_song_info_by_keyword(self, keyword):
        try:
            api_url = f"https://163api.qijieya.cn/search?keywords={keyword}"
            resp = requests.get(api_url)
            resp.raise_for_status()
            resp_json = resp.json()
            songs = jsonpath.jsonpath(resp_json, "$.result.songs")
            if not songs:
                return {'status': 'error'}
            songs = songs[0]
            length = len(songs)
            for i in range(length):
                song_name = jsonpath.jsonpath(resp_json, f"$.result.songs[{i}].name")[0]
                song_artists = jsonpath.jsonpath(resp_json, f"$.result.songs[{i}].artists[*].name")
                album_name = jsonpath.jsonpath(resp_json, f"$.result.songs[{i}].album.name")[0]
                song_id = jsonpath.jsonpath(resp_json, f"$.result.songs[{i}].id")[0]
                flag = True
                if song_name in keyword:
                    for artist in song_artists:
                        if artist not in keyword:
                            flag = False
                else:
                    flag = False
                if flag:
                    return self.get_song_info(song_id)
            else:
                return {'status': 'error'}
        except Exception:
            return {'status': 'error'}

    def get_lyrics(self, song_id):
        lrc = requests.get(f"https://music.163.com/api/song/lyric?id={song_id}&lv=1&kv=1&tv=-1").json()

        olrc = lrc['lrc'].get('lyric')
        if 'tlyric' in lrc:
            tlrc = lrc['tlyric'].get('lyric')
        else:
            tlrc = None
        return olrc, tlrc

    def get_mp3_data(self, song_id):
        audio_data = requests.get(f'https://music.163.com/song/media/outer/url?id={song_id}', headers=self.headers)
        content_type = audio_data.headers.get('Content-Type')
        if "text/html" not in content_type:
            is_succeed = True
        else:
            is_succeed = False
        return is_succeed, audio_data


class VKeyApi:
    def __init__(self):
        self.desc = "落月API"

    def get_song_info(self, song_id, quality=4):
        """
        可选值	音质
        1	标准（64k）
        2	标准（128k）
        3	HQ极高（192k）
        4	HQ极高（320k）
        5	SQ无损
        6	高解析度无损（Hi-Res）
        7	高清臻音（Spatial Autio）
        8	沉浸环绕声（Surround Autio）
        9	超清母带（Master）
        """
        api_url = f"https://api.vkeys.cn/v2/music/netease?id={song_id}&quality={quality}"

        try:
            response = requests.get(api_url, timeout=15)
            response.raise_for_status()

            data = response.json()

            # 检查响应状态
            if data.get('code') != 200:
                print(f"API错误: {data}")
                return None

                # 检查是否有有效的URL
            if not data.get('data') or not data['data'].get('url'):
                print("未获取到有效的音频URL")
                return None

            return data['data']

        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return None


class XcvtsApi:
    """小尘API - 波点音乐点歌接口，作为备用音源"""

    def __init__(self):
        self.desc = "小尘API(波点音乐)"
        self.base_url = "https://api.xcvts.cn/api/music/bdyy"
        self.default_quality = "320kmp3"

    def search_and_get_url(self, keyword, quality=None):
        """
        通过关键词搜索歌曲并获取音频URL

        参数:
            keyword: 搜索关键词（歌名/歌手名）
            quality: 音质，可选值: 20201kmflac, 2000kflac, 320kmp3, 128kmp3, 48kaac, 192kogg, 100kogg
        返回:
            dict: {'name', 'artist', 'cover', 'play_url', 'lrc'} 或 None
        """
        params = {
            'msg': keyword,
            'n': 1,
            'type': 'json',
        }
        if quality:
            params['br'] = quality
        else:
            params['br'] = self.default_quality

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if data.get('code') != 200:
                print(f"小尘API错误: {data}")
                return None

            song_data = data.get('data')
            if not song_data or not song_data.get('play_url'):
                print("小尘API: 未获取到有效的音频URL")
                return None

            return song_data

        except requests.exceptions.RequestException as e:
            print(f"小尘API请求失败: {e}")
            return None

    def get_lyrics(self, keyword):
        """
        通过关键词获取歌词

        参数:
            keyword: 搜索关键词
        返回:
            str: 歌词文本，失败返回 None
        """
        params = {
            'msg': keyword,
            'n': 1,
            'type': 'lyric',
        }
        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"小尘API歌词请求失败: {e}")
            return None

    def get_mp3_data(self, keyword, quality=None):
        """
        通过关键词搜索并下载音频数据

        参数:
            keyword: 搜索关键词
            quality: 音质
        返回:
            tuple: (is_success, audio_response, song_data_or_none)
        """
        song_data = self.search_and_get_url(keyword, quality)
        if not song_data:
            return False, None, None

        audio_url = song_data.get('play_url')
        try:
            audio_response = requests.get(audio_url, timeout=30)
            content_type = audio_response.headers.get('Content-Type', '')
            if 'text/html' in content_type or audio_response.status_code != 200:
                return False, None, None
            return True, audio_response, song_data
        except requests.exceptions.RequestException as e:
            print(f"小尘API下载失败: {e}")
            return False, None, None


if __name__ == '__main__':
    api = NCMApi()
    # playlist_id = input("Playlist id: ")
    # playlist = api.get_playlist_info(playlist_id)
    # playlist_name = playlist['name']
    # playlist_id = playlist['id']
    # playlist_creator = playlist['creator']
    # playlist_trackIds = playlist['trackIds']
    # print(playlist)
    res = api.get_song_info_by_keyword("勿忘 - Awesome City Club")
    print(res)
