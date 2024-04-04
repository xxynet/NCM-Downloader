# NCM-Downloader
A powerful NCM Downloader that supports built-in metadata (title, artists, album, cover)

一个强大的网易云下载工具，支持内嵌元信息（歌曲名，歌手，专辑，歌曲封面），暂时只支持下载歌单

## Usage
Clone this project

```
git clone https://github.com/xxynet/NCM-Downloader.git
```

Edit ```config.ini```

```
[output]

#设置歌单输出路径，如果为空则默认为程序所在目录（路径无需引号包裹）
path = 

#0->歌名-歌手 1->歌手-歌名 2->歌名（暂时无效）
filename = 0
```

Run ```main.py``` and input your playlist ID
