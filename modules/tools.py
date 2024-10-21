import sqlite3
def connectDatabase():
    try:
        conn = sqlite3.connect('modules/database.db')
        return conn
    except Exception as e:
        print(e)
    return None

def getSong(self, id: int):
    for i in self.playlist:
        if (i.song_id == id):
            return i


def getCounts(self, id: int) -> int:
    cursor=connectDatabase().cursor()
    cursor.execute(f"SELECT counts FROM songs WHERE song_id={id}")
    count = cursor.fetchone()
    if count:
        cursor.close()
        return count[0]
    return -1


def getSongStats(self) -> list:
    cursor=connectDatabase().cursor()
    cursor.execute("SELECT song_id, counts FROM songs")
    lines = cursor.fetchall()
    # Extract song statistics and prepare a list of tuples (count, song_id)
    song_stats = []
    for line in lines:
        if(len(line)==2):
            song_stats.append((line[1],line[0]))
    cursor.close()
    # Sort song statistics by count in descending order
    song_stats.sort(reverse=True, key=lambda x: x[0])

    # Retrieve song objects based on sorted statistics
    top_songs = [getSong(self,song_id) for _, song_id in song_stats]

    return top_songs
