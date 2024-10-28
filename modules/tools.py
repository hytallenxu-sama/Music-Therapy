import sqlite3
import matplotlib.pyplot as plt
import io
import base64
from hashlib import sha256

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


def returnBase64(self,data:dict):
    plt.switch_backend('Agg')
    sorted_data = sorted(data.items())
    dates = [item[0] for item in sorted_data]
    times = [int(item[1]) for item in sorted_data]

        # Create the plot
    fig, ax = plt.subplots()
    ax.plot(dates, times, marker='o')

        # Set labels
    ax.set_xlabel("Date")
    ax.set_ylabel("Times")
    ax.set_title("Times vs. Date")

        # Save the plot to a BytesIO object
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)

        # Convert the plot to a base64 string for Flet Image
    img_data = buffer.getvalue()
    plt.close(fig)  # Close the figure after saving to free resources

        # Convert BytesIO object to a base64-encoded image
    img_data = base64.b64encode(img_data).decode("utf-8")
    return img_data

def getDailyData(self):
    cursor=connectDatabase().cursor()
    cursor.execute("SELECT * FROM daily_stats")
    lines = cursor.fetchall()
    res = {}
    for line in lines:
        if len(line) == 2:
            res[str(line[0])] = line[1]
    cursor.close()
    return res

def hash(password:str):
    return sha256(password.encode('utf-8')).hexdigest()