import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    username = sql.Column(sql.String(255), unique=True)
    password = sql.Column(sql.String(255))
    permissions = sql.Column(sql.Integer)

class Album(Base):
    __tablename__ = 'albums'

    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    name = sql.Column(sql.String(255), unique=True)
    virtual = sql.Column(sql.Boolean)

    def __repr__(self):
        return "<Album(name='%s', virtual='%d')>" % (
            self.name, self.virtual)

class Image(Base):
    __tablename__ = 'images'

    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    path = sql.Column(sql.String(4096))  # unique=True
    name = sql.Column(sql.String(255))
    creation = sql.Column(sql.DateTime)
    mtime = sql.Column(sql.DateTime)
    width = sql.Column(sql.Integer)
    height = sql.Column(sql.Integer)
    size = sql.Column(sql.BigInteger)
    geo_east = sql.Column(sql.Float(precision='15,10'), nullable=True)
    geo_west = sql.Column(sql.Float(precision='15,10'), nullable=True)
    format = sql.Column(sql.String(64))
    album_id = sql.Column(sql.Integer, sql.ForeignKey("albums.id"), nullable=True, index=True)
    album = relationship(Album, primaryjoin=album_id == Album.id)

    def __repr__(self):
        return "<Image(path='%s', format='%s', album=%s)>" % (
            self.path, self.format, self.album)

class LastUpdated(Base):
    __tablename__ = 'last_updated'
    key = sql.Column(sql.String(32), primary_key=True)
    date = sql.Column(sql.DateTime)
