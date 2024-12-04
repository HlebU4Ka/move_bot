from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from sqlalchemy.orm import relationship


Base = declarative_base()
movie_genres = Table(
    "movie_genres",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id")),
    Column('genre_id', Integer, ForeignKey("genres.id")),
)

class Movie(Base):

    __tablename__ = 'movies'


    id = Column(Integer,primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    year = Column(Integer)
    rating = Column(Float)
    trailer_url = Column(String)

    genres = relationship("Genre", secondary=movie_genres,back_populates="movies")
    watched_by = relationship("WatchedMovie",back_populates="movies")


class Genre(Base):
    __tablename__="genres"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    movies = relationship("Movie", secondary=movie_genres, back_populates="genres")


class WatchedMovies(Base):
    __tablename__ ="watched_movies"

    id= Column(Integer,primary_key=True)
    user_id = Column(Integer, nullable=False)
    movie_id = Column(Integer,ForeignKey("movies.id"))
    watched_date=Column(DateTime,default=datetime.now)

    movie = relationship("Movie", back_populates="watched_by")
