from modules.Song import Song
from modules.tools import *
class AudioDirectory(object):
    # read lines
    cursor=connectDatabase().cursor()
    cursor.execute("SELECT * FROM songs")
    lines=cursor.fetchall()
    playlist:list=[]
    for i in lines:
        playlist.append(Song(song_id=i[0],song_name=i[1],artist=i[2],audio_path=i[3],img_src=i[4]))
    cursor.close()

    def refresh(self):
        self.cursor=connectDatabase().cursor()
        self.cursor.execute("SELECT * FROM songs")
        self.lines=self.cursor.fetchall()
        self.playlist.clear()
        for i in self.lines:
            self.playlist.append(Song(song_id=i[0],song_name=i[1],artist=i[2],audio_path=i[3],img_src=i[4]))
        self.cursor.close()