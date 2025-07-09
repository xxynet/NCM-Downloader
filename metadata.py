from mutagen.mp3 import EasyMP3
from mutagen.id3 import APIC, ID3, USLT, error
import requests
import re


# filepath, name, artists, album, cover_url
def meta_data(path, name, artists, album, cover):

    audio = EasyMP3(path)

    audio["title"] = name
    audio["artist"] = artists
    audio["album"] = album

    audio.save()

    audio = ID3(path)

    audio.delall('APIC') # clear the image data

    response = requests.get(cover)
    image_data = response.content

    # audio['APIC'] = APIC(
    #     encoding=0,
    #     mime='image/jpeg',
    #     type=3,
    #     desc=u'Cover',
    #     data=image_data
    # )

    audio.add(APIC(
        encoding=0,
        mime='image/jpeg',  # Change this if you know it's a different image type
        type=3,  # 3 is for cover image
        desc=u'Cover',
        data=image_data
    ))

    audio.save()


def parse_lrc(lrc):
    # 使用正则表达式解析LRC歌词
    pattern = re.compile(r'\[(\d{2}:\d{2}\.\d{2,3})\](.*)')
    lrc_dict = {}
    for line in lrc.split('\n'):
        match = pattern.match(line)
        if match:
            time = match.group(1)
            text = match.group(2).strip()
            if time in lrc_dict:
                lrc_dict[time].append(text)
            else:
                lrc_dict[time] = [text]
    return lrc_dict


def merge_lrc(olrc, tlrc):
    if tlrc:
        # 解析原始歌词和翻译歌词
        original_dict = parse_lrc(olrc)
        translated_dict = parse_lrc(tlrc)

        # 合并歌词
        merged_dict = {}
        all_times = set(original_dict.keys()).union(translated_dict.keys())
        for time in all_times:
            original_text = '\n'.join(original_dict.get(time, []))
            translated_text = '\n'.join(f'[{time}]{line}' for line in translated_dict.get(time, []))
            merged_text = original_text + '\n' + translated_text if original_text and translated_text else original_text + translated_text
            merged_dict[time] = merged_text.strip()

        # 生成合并后的LRC格式歌词
        merged_lrc = ''
        for time in sorted(merged_dict.keys()):
            merged_lrc += f'[{time}]{merged_dict[time]}\n'

        return merged_lrc
    else:
        return olrc


def builtin_lyrics(file_path, lrc):

    audio = ID3(file_path)

    audio["USLT::'und'"] = USLT(encoding=3, lang='und', desc='lyrics', text=lrc)

    audio.save()
