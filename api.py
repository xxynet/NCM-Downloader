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
        api_url = f"https://163api.qijieya.cn/search?keywords={keyword}"
        resp = requests.get(api_url).json()
        songs = jsonpath.jsonpath(resp, "$.result.songs")[0]
        length = len(songs)
        for i in range(length):
            song_name = jsonpath.jsonpath(resp, f"$.result.songs[{i}].name")[0]
            song_artists = jsonpath.jsonpath(resp, f"$.result.songs[{i}].artists[*].name")
            album_name = jsonpath.jsonpath(resp, f"$.result.songs[{i}].album.name")[0]
            song_id = jsonpath.jsonpath(resp, f"$.result.songs[{i}].id")[0]
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
            song_info = {
                'status': 'error'
            }
            return song_info

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
