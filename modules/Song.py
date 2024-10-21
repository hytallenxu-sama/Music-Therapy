import flet as ft
# define a song class
class Song(object):
    def __init__(self, song_name: str, artist: str, audio_path: str, img_src:str, song_id:int):
        super(Song, self).__init__()
        self.song_name = song_name
        self.artist_name = artist
        self.audio_path = audio_path
        self.img_src=img_src
        self.song_id=song_id

    @property
    def src(self):
        return self.img_src

    @property
    def id(self):
        return self.song_id

    @property
    def name(self):
        return self.song_name

    @property
    def artist(self):
        return self.artist_name

    @property
    def path(self):
        return self.audio_path