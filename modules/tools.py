import sqlite3
import matplotlib.pyplot as plt
import io
import base64
from hashlib import sha256
import time
import datetime
import matplotlib.dates as mdates
from modules.Database import Database
from modules.Tables import *

db_handler = Database('sqlite:///SQLite/database.db')
logger_handler = Database('sqlite:///SQLite/logs.db')

def logger(type, message):
    new_log = logger_handler.insert_data(Log, INFO_TYPE=type, CONTENT=message, TIMESTAMP=int(time.time()))
    if new_log:
        return True
    return False


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


def returnBase64(self, data: dict) -> str:
    # Use a non-interactive backend
    plt.switch_backend('Agg')

    # Sort the data by date
    sorted_data = sorted(data.items())
    date_strings = [str(item[0]) for item in sorted_data]
    times = [item[1] for item in sorted_data]
    # Convert date strings to datetime objects
    dates = [datetime.strptime(date, '%Y%m%d') for date in date_strings]
    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(dates, times, marker='o', linestyle='-')

    # Set labels and title
    ax.set_xlabel("Date")
    ax.set_ylabel("Times")
    ax.set_title("Times vs. Date")

    # Format the x-axis to show dates properly
    locator = mdates.AutoDateLocator()
    formatter = mdates.DateFormatter('%Y-%m-%d')
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    # Rotate date labels for better readability
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    # Adjust layout to prevent clipping of tick-labels
    plt.tight_layout()

    # Save the plot to a BytesIO object
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)

    # Convert the plot to a base64 string
    img_data = buffer.getvalue()
    buffer.close()
    plt.close(fig)  # Close the figure to free resources

    # Encode the image to Base64
    base64_img = base64.b64encode(img_data).decode('utf-8')

    return base64_img

def getDailyData(self):
    lines = db_handler.query_data(Daily)
    res = {}
    for line in lines:
        res[line.date]=line.counts
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