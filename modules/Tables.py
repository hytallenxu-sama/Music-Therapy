from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()

class Log(Base):
    __tablename__ = 'LOGS'  # Table name in the database
    id = Column(Integer, primary_key=True, autoincrement=True)  # Optional unique ID (if not in the schema, remove it)
    INFO_TYPE = Column(String, nullable=False)  # 'type' column (TEXT in your table)
    CONTENT = Column(String, nullable=False)  # 'info' column (TEXT in your table)
    TIMESTAMP = Column(Integer, nullable=False)  # 'time' column (INTEGER in your table)

class Songs(Base):
    __tablename__ = 'songs'
    song_id = Column(Integer, primary_key=True, autoincrement=True)
    song_name = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    audio_path = Column(String, nullable=False)
    img_src = Column(String, nullable=False)
    counts = Column(Integer, nullable=False)

class Comment(Base):
    __tablename__ = 'comments'
    comment_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    song_id = Column(Integer, nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(Integer, nullable=False)

class Secrets(Base):
    __tablename__ = 'secrets'
    ENDPOINT = Column(String, primary_key=True, nullable=False)
    API_KEY = Column(String, nullable=False)

class Daily(Base):
    __tablename__ = 'daily_stats'
    date = Column(String, primary_key=True, nullable=False)
    counts = Column(Integer, nullable=False)

class UserData(Base):
    __tablename__ = 'users'
    username = Column(String, primary_key=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    LoginTime = Column(Integer, nullable=False)