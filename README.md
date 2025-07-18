# NCM-Downloader
A powerful NCM Downloader that supports built-in metadata (title, artists, album, cover)

一个强大的网易云下载工具，支持内嵌元信息（歌曲名，歌手，专辑，歌曲封面），暂时只支持下载歌单

Try the latest [Docker version](https://github.com/xxynet/ncm-dl-docker) as well
 尝试最新的[Docker版本](https://github.com/xxynet/ncm-dl-docker)

![](./Screenshots/Screenshot12.png)

<div align="center">

[Docs](http://docs.xuxiny.top/ncm/)

<a href="https://github.com/xxynet/NCM-Downloader/releases">
    <img src="https://img.shields.io/github/v/release/xxynet/NCM-Downloader" alt="latest version" />
  </a>

<a href="https://github.com/xxynet/NCM-Downloader/releases">
    <img src="https://img.shields.io/github/downloads/xxynet/NCM-Downloader/total" alt="downloads" />
  </a>

<a href="https://github.com/xxynet/NCM-Downloader/issues">
    <img src="https://img.shields.io/github/issues/xxynet/NCM-Downloader" alt="issues" />
  </a>

</div>

## 开发背景
本项目由一名高中生在业余时间开发，最初是想要下载带有元信息和歌曲封面的音乐文件，方便搭建音乐服务器（如Navidrome）时展示美观的海报墙。由于网上现成的工具都无法获取歌曲元信息，遂决定自己开发。想着应该也有人和我有相同的需求，同时也学习一下做开源项目的大致流程，所以就有了这个项目

## 📷 ScreenShots

| Navidrome  | 音流 |
| ------------- | ------------- |
| ![](./Screenshots/Screenshot09.png)  | ![](./Screenshots/Screenshot10.png)  |



![](./Screenshots/Screenshot02.png)

![](./Screenshots/Screenshot12.png)

| ![](./Screenshots/Screenshot03.png) | ![](./Screenshots/Screenshot04.png) |
|--|--|

v1.1.0及以上支持下载歌词，使用支持读取歌词文件的播放器打开即可（图为Dopamine）：

| ![](./Screenshots/Screenshot05.png) | ![](./Screenshots/Screenshot06.png) |
|--|--|

v1.5.0及以上支持同时获取原始歌词和翻译歌词，并且支持内嵌歌词和歌词文件两种模式

| ![](./Screenshots/Screenshot07.png) | ![](./Screenshots/Screenshot08.png) |
|--|--|

## 🔨 Usage
Clone this project

```
git clone https://github.com/xxynet/NCM-Downloader.git
```

Install requirements

```
pip install -r requirements.txt
```

Edit `config.ini`

```
[output]

#设置歌单输出路径，如果为空则默认为程序所在目录（路径无需引号包裹）
path = 

#0->歌名-歌手 1->歌手-歌名 2->歌名（暂时无效）
filename = 0

#是否下载歌词 1 -> 下载LRC歌词文件  2 -> 内嵌歌词  0 -> False
lrc = 0

[settings]

#是否检查更新，如果出现问题可尝试将其改为0禁用自动更新
detect-update = 1
```

Copy your cookie into `cookie.txt`

Run `main.py` and input your playlist ID


For executables, please access to [Releases](https://github.com/xxynet/NCM-Downloader/releases)

## 💬 Q&A

<details>

<summary>Q: 为什么要配置Cookie，如何配置Cookie？</summary>

> A: 由于网易云API调整，未登录用户只能获取歌单前10首歌曲，配置Cookie后可以获取完整歌单信息。
> 
> 首先访问[网易云官网](https://music.163.com/)，按键盘上的F12，打开DevTools，切换到Network（网络）选项卡，按键盘上的Ctrl+R刷新，随便点一个项目（如music.163.com），在Headers（标头）中下拉，找到Request Headers（请求标头）中的Cookie，复制右侧的值，填入配置文件即可。

</details>

<details>

<summary>Q: 提示“获取歌曲信息异常，请重新运行本程序”</summary>

> A: 网易云服务器繁忙，可以再试几次，若仍然无法下载，请等待一会儿再试

</details>

<details>

<summary>Q: 如何获取歌单ID？</summary>

> A: 使用网页版打开想要下载的歌单（必须是公开的歌单），复制链接中```?id=```后面的数字
>
> ```
> https://music.163.com/#/playlist?id=歌单ID
> ```

</details>

<details>

<summary>Q: 运行后提示“Windows 已保护你的电脑”？</summary>

> A: 本程序使用pyinstaller打包，请点击“更多信息” -> “仍要运行”

</details>

<details>

<summary>Q: 为什么会提示红色的E：歌曲名称</summary>

> A: 该歌曲需要VIP才能收听，并且没有设置具有VIP的cookie

</details>

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=xxynet/NCM-Downloader&type=Date)](https://star-history.com/#xxynet/NCM-Downloader&Date)