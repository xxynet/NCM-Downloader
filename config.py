import configparser

VERSION = 'v2.2.1'

config_file = '''[output]

#设置歌单输出路径，如果为空则默认为程序所在目录（路径无需引号包裹）
path = 

#0->歌名-歌手 1->歌手-歌名 2->歌名（暂时无效）
filename = 0

#是否下载歌词 1 -> 下载LRC歌词文件  2 -> 内嵌歌词  0 -> False
lrc = 0

[settings]

#是否检查更新，如果出现问题可尝试将其改为0禁用自动更新
detect-update = 1
'''