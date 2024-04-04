from mutagen.mp3 import EasyMP3
from mutagen.id3 import APIC, ID3
import requests

# filepath, name, artists, album, cover_url
def MetaData(path, name, artists, album, cover):

    audio = EasyMP3(path)

    audio["title"] = name
    audio["artist"] = artists
    audio["album"] = album

    audio.save()


    audio = ID3(path)

    response = requests.get(cover)
    image_data = response.content

    audio['APIC'] = APIC(
        encoding=0,
        mime='image/jpeg',
        type=3,
        desc=u'Cover',
        data=image_data
    )

    audio.save()
