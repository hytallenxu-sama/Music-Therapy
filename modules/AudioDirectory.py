from modules.Song import Song
from modules.tools import *
from modules.Database import Database
from modules.Tables import *

class AudioDirectory(object):
    db_handler = Database('sqlite:///SQLite/database.db')
    lines=db_handler.query_data(Songs)
    playlist:list=[]
    for line in lines:
        playlist.append(Song(song_id=line.song_id,song_name=line.song_name,artist=line.artist,audio_path=line.audio_path,img_src=line.img_src))

    def refresh(self):
        self.db_handler = Database('sqlite:///SQLite/database.db')
        lines = db_handler.query_data(Songs)
        self.playlist.clear()
        for line in lines:
            self.playlist.append(
                Song(song_id=line.song_id, song_name=line.song_name, artist=line.artist, audio_path=line.audio_path,
                     img_src=line.img_src))