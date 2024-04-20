# NCM Downloader
#请打开config.ini配置文件配置相应信息

#pyinstaller -F main.py -i music.ico

import requests
import jsonpath
import os
import sys
import time
import configparser
import metadata

config_file = '''[output]

#设置歌单输出路径，如果为空则默认为程序所在目录（路径无需引号包裹）
path = 

#0->歌名-歌手 1->歌手-歌名 2->歌名（暂时无效）
filename = 0

#是否下载歌词 1 -> True  0 -> False
lrc = 0
'''

if not os.path.exists('config.ini'):
    with open("config.ini", "w", encoding="utf-8") as config:
        config.write(config_file)
    print("首次运行，已自动创建config.in文件")

try:
    config = configparser.ConfigParser()
    config.read('config.ini',encoding='utf-8')
    path = config.get('output', 'path')
    if path == '':
        path = os.getcwd()
    filename = config.get('output','filename')

    bool_lrc = config.get('output', 'lrc')
except:
    print("读取config.ini文件失败")
    time.sleep(3)
    sys.exit(1)

try:
    Playlist_id = int(input("歌单id："))
except:
    print("非法输入！")
    time.sleep(3)
    sys.exit(1)

headers = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67'
}

def MusicDown(Playlist_name,id,name,artists):
    try:
        data = requests.get('https://music.163.com/song/media/outer/url?id=' + str(id), headers=headers)
        lrc = requests.get('https://music.163.com/api/song/lyric?id='+str(id)+'&lv=1&kv=1&tv=-1')
        lrc = jsonpath.jsonpath(lrc.json(), "$.lrc.lyric")[0]
    except:
        print("获取歌曲音频失败！")

    try:
        with open(path + "\\" + Playlist_name + "\\" + name + " - " + artists + ".mp3", "wb") as file:
            file.write(data.content)

        if bool_lrc == '1':
            with open(path + "\\" + Playlist_name + "\\" + name + " - " + artists + ".lrc", "w") as file:
                file.write(lrc)

        print(name + " - " + artists + ".mp3  " + "download completed")
    except:
        print(name+" - "+artists+".mp3  "+"download failed")



response = requests.get("https://music.163.com/api/playlist/detail?id="+str(Playlist_id),headers=headers)

if response.status_code == 200:
    data = response.json()
    try:
        amount = len(jsonpath.jsonpath(data, "$.[tracks]")[0])
    except:
        print("获取歌曲信息异常，请重新运行本程序")
        print(data)
        time.sleep(3)
        sys.exit(1)

    try:
        Playlist_name = jsonpath.jsonpath(data, "$.['name']")[0]
    except:
        print("获取歌单名称失败！")
        time.sleep(3)
        sys.exit(1)
    try:
        if not os.path.exists(path + "\\" + Playlist_name):
            os.mkdir(path + "\\" + Playlist_name)
    except:
        print("创建歌单文件夹失败!")
        time.sleep(3)
        sys.exit(1)

    for i in range(amount):
        name = jsonpath.jsonpath(data, "$.[tracks]["+str(i)+"]['name']")[0]
        id = jsonpath.jsonpath(data, "$.[tracks]["+str(i)+"]['id']")[0]
        artists_info = jsonpath.jsonpath(data, "$.[tracks]["+str(i)+"]['artists']")[0]
        artists_num = len(artists_info)
        artists_list = []
        artists = ''
        for j in range(artists_num):
            artist_name = jsonpath.jsonpath(data, "$.[tracks]["+str(i)+"]['artists']["+str(j)+"]['name']")[0]
            artists_list.append(artist_name)
            artists+=artist_name+","
        artists = artists[:-1]

        cover = jsonpath.jsonpath(data, "$.[tracks]["+str(i)+"]['album']['picUrl']")[0]
        album = jsonpath.jsonpath(data, "$.[tracks]["+str(i)+"][album][name]")[0]
        full_path = path + "\\" + Playlist_name + "\\" + name + " - " + artists + ".mp3"
        if not os.path.exists(full_path):
            MusicDown(Playlist_name,id, name, artists)
            metadata.MetaData(full_path, name, artists_list, album, cover)
        else:
            print(name+" - "+artists+".mp3  "+"already exist")

    time.sleep(3)

else:
    print("请求失败！")

# name: $.[tracks][0]['name']
# ID： $.[tracks][0]['id']
# 封面：$.[tracks][0]['album']['picUrl']
# 歌手：$.[tracks][0]['artists'][0]['name']
# 专辑：$.[tracks][0][album][name]
# 歌词：https://music.163.com/api/song/lyric?id={歌曲ID}&lv=1&kv=1&tv=-1