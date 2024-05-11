# NCM-Downloader
A powerful NCM Downloader that supports built-in metadata (title, artists, album, cover)

一个强大的网易云下载工具，支持内嵌元信息（歌曲名，歌手，专辑，歌曲封面），暂时只支持下载歌单

## ScreenShots
![](./Screenshot01.png)

![](./Screenshot02.png)

![](./Screenshot03.png)

![](./Screenshot04.png)

v1.1.0及以上支持下载歌词，使用支持读取歌词文件的播放器打开即可（图为Dopamine）：

![](./Screenshot05.png)

![](./Screenshot06.png)

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

#是否下载歌词 1 -> True  0 -> False
lrc = 1
```

Run ```main.py``` and input your playlist ID


For executable files, please access to [Releases](https://github.com/xxynet/NCM-Downloader/releases)

## Q&A
> Q: 提示“获取歌曲信息异常，请重新运行本程序”

A: 网易云服务器繁忙，可以再试几次，若仍然无法下载，请等待一会儿再试

> Q: 如何获取歌单ID？

A: 使用网页版打开想要下载的歌单（必须是公开的歌单），复制链接中```?id=```后面的数字

```
https://music.163.com/#/playlist?id=歌单ID
```

> Q: 运行后提示“Windows 已保护你的电脑”？

A: 本程序使用pyinstaller打包，请点击“更多信息” -> “仍要运行”