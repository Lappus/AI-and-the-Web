# Contains parts from: https://flask-user.readthedocs.io/en/latest/quickstart_app.html

from flask import Flask, render_template, redirect, url_for, request
from flask_user import login_required, UserManager, current_user

from models import db, User, Movie, Tag, Link, MovieGenre, Rating
from read_data import check_and_read_data

# Class-based application configuration
class ConfigClass(object):
    """ Flask application config 
        Defines the configuration settings for the flask application.
        It sets the Database URI to a SQLite database file names movie_recommender.sqlite
    """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///movie_recommender.sqlite'  # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids SQLAlchemy warning

    # Flask-User settings
    USER_APP_NAME = "Movie Recommender"  # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False  # Disable email authentication
    USER_ENABLE_USERNAME = True  # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = True  # Simplify register form

# Create Flask app
app = Flask(__name__)
app.config.from_object(__name__ + '.ConfigClass')  # configuration of flask app using ConfigClass
app.app_context().push()  # create an app context before initializing db
db.init_app(app)  # initialize database
db.create_all()  # create database if necessary
user_manager = UserManager(app, db, User)  # initialize Flask-User management


@app.cli.command('initdb')
# when executed it intializes the database via the check and read data function
def initdb_command():
    global db
    """Creates the database tables."""
    check_and_read_data(db)
    print('Initialized the database.')

# The Home page is accessible to anyone
@app.route('/')
def home_page():
    # render home.html template
    return render_template("home.html")

"""
# The Members page is only accessible to authenticated users via the @login_required decorator
@app.route('/movies')
#@login_required  # User must be authenticated
def movies_page():
    # String-based templates

    # first 10 movies
    movies = Movie.query.limit(10).all()
    # only Romance movies
    # movies = Movie.query.filter(Movie.genres.any(MovieGenre.genre == 'Romance')).limit(10).all()
    tags = {}
    for movie in movies:
        tags.update({movie.id : Tag.query.filter_by(movie_id=movie.id).limit(10).all()})
    #print(tags)

    links = {}
    for movie in movies:
        links.update({movie.id : Link.query.filter_by(movie_id=movie.id).limit(10).all()})
    # only Romance AND Horror movies
    # movies = Movie.query\
    #     .filter(Movie.genres.any(MovieGenre.genre == 'Romance')) \
    #     .filter(Movie.genres.any(MovieGenre.genre == 'Horror')) \
    #     .limit(10).all()

   # ratings = {}
    #for movie in movies:
     #   ratings.update({movie.id : Rating.query.filter_by(movie_id=movie.id).all()})


    return render_template("movies.html", movies=movies, tags=tags, links=links)
"""
@app.route('/movies', methods=['GET', 'POST'])
@login_required  # User must be authenticated
def movies_page():
    # String-based templates
    rating_value=0
    movies = Movie.query.limit(10).all()
    tags = {}
    for movie in movies:
        tags.update({movie.id: Tag.query.filter_by(movie_id=movie.id).limit(10).all()})
    links = {}
    for movie in movies:
        links.update({movie.id: Link.query.filter_by(movie_id=movie.id).limit(10).all()})

    if request.method == 'POST':
        # rating submissions
        movie_id = int(request.form.get('movie_id'))
        rating_value = int(request.form.get('rating'))
        print(type(rating_value))
        user_id = current_user.id  

        # Check if the user has already rated the movie
        existing_rating = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()

        if existing_rating:
            # Update the existing rating
            existing_rating.rating = rating_value
        else:
            # Insert a new rating
            new_rating = Rating(user_id=user_id, movie_id=movie_id, rating=rating_value)
            db.session.add(new_rating)

        db.session.commit()
        return render_template('rating.html')

    return render_template("movies.html", movies=movies, tags=tags, links=links, rating=rating_value)

# Start development web server
if __name__ == '__main__':
    app.run(port=5000, debug=True)
