from flask_sqlalchemy import SQLAlchemy
from flask_user import UserMixin
from sqlalchemy import Sequence

db = SQLAlchemy()

# Define the User data-model.
# NB: Make sure to add flask_user UserMixin as this adds additional fields and properties required by Flask-User

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id_seq = Sequence('user_id_seq', start=620)
    id = db.Column(db.Integer, id_seq, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')

    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    username = db.Column(db.String(100, collation='NOCASE'), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    email_confirmed_at = db.Column(db.DateTime())

    # User information
    first_name = db.Column(db.String(100, collation='NOCASE'), server_default='')
    last_name = db.Column(db.String(100, collation='NOCASE'), server_default='')

    # For debugging
    #def __repr__(self):
    #    return f'<User: {self.username}> <ID: {self.id}> <password: {self.password}>'

class Rating(db.Model):
    __tablename__ = 'ratings'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True, nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), primary_key=True, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    # allows to navigate between User and Ratings Model
    user = db.relationship('User', backref='ratings')
    #timestamp = db.Column(db.Integer, primary_key=True, nullable=False)

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100, collation='NOCASE'), nullable=False, unique=True)
    # clean_title = db.Column(db.String(100, collation='NOCASE'), nullable=False, unique=True)
    genres = db.relationship('MovieGenre', backref='movie', lazy=True)

class MovieGenre(db.Model):
    __tablename__ = 'movie_genres'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    genre = db.Column(db.String(255), nullable=False, server_default='')

class Link(db.Model):
    __tablename__ = 'links'
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), primary_key=True, nullable=False)
    imdb_id = db.Column(db.Integer,  nullable=False)
    tmdb_id = db.Column(db.Integer,  nullable=False)
    
class Tag(db.Model):
    __tablename__ = 'tags'
    user_id = db.Column(db.Integer, db.ForeignKey('movies.id'), primary_key=True,  nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True,  nullable=False)
    tag = db.Column(db.String(255), primary_key=True,  nullable=False)
    timestamp = db.Column(db.Integer, primary_key=True,  nullable=False)

class AverageRating(db.Model):
    __tablename__ = 'average_rating'
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), primary_key=True, nullable=False)
    rating = db.Column(db.Float, primary_key=True, nullable=False)
