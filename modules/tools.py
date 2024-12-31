import sqlite3
import matplotlib.pyplot as plt
import io
import base64
from hashlib import sha256
import time
from modules.Database import Database
from modules.Tables import *

db_handler = Database('sqlite:///SQLite/database.db')
logger_handler = Database('sqlite:///SQLite/logs.db')

def logger(type, message):
    new_log = logger_handler.insert_data(Log, INFO_TYPE=type, CONTENT=message, TIMESTAMP=int(time.time()))
    if new_log:
        return True
    return False

def connectDatabase():
    try:
        conn = sqlite3.connect('SQLite/database.db')
        return conn
    except Exception as e:
        print(e)
    return None

def getSong(self, id: int):
    for i in self.playlist:
        if (i.song_id == id):
            return i

def getCounts(self, id: int) -> int:
    res = db_handler.query_data(Songs, song_id=id)
    for i in res:
        return i.counts


def getSongStats(self) -> list:
    lines = db_handler.query_data(Songs)
    song_stats = []
    for line in lines:
        song_stats.append([line.counts,line.song_id])
    song_stats.sort(reverse=True, key=lambda x: x[0])
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

from datetime import datetime

# Function to convert Unix timestamp to human-readable date
def unix_to_human(unix_timestamp):
    # Convert Unix timestamp to datetime object
    normal_time = datetime.fromtimestamp(unix_timestamp)
    # Format as a readable string
    return normal_time.strftime('%Y-%m-%d %H:%M:%S')

def insertTokens(token:int):
    conn = connectDatabase()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO AutoReply (TOKENS) VALUES (?)', (token,))
    conn.commit()
    conn.close()