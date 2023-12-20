# Contains parts from: https://flask-user.readthedocs.io/en/latest/quickstart_app.html

from flask import Flask, render_template, redirect, url_for, request
from flask_user import login_required, UserManager, current_user
from surprise import Dataset
from surprise import Reader
from surprise.model_selection import train_test_split
from surprise import KNNWithMeans
import pandas as pd

from models import db, User, Movie, Tag, Link, MovieGenre, Rating
from read_data import check_and_read_data
from search import recommended

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
    check_and_read_data(db_session = db.session)
    print('Initialized the database.')

# The Home page is accessible to anyone
@app.route('/')
def home_page():
    # render home.html template
    return render_template("home.html")

@app.route('/movies', methods=['GET', 'POST'])
@login_required  # User must be authenticated
def movies_page():
    # String-based templates
    movies = Movie.query.limit(10).all()
    tags = {}
    for movie in movies:
        tags.update({movie.id: Tag.query.filter_by(movie_id=movie.id).limit(10).all()})
    links = {}
    for movie in movies:
        links.update({movie.id: Link.query.filter_by(movie_id=movie.id).limit(10).all()})


    if request.method == 'POST':
        # Handle rating submission
        movie_id = request.form.get('movie_id')
        rating_value = request.form.get('rating')
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
        
        title = db.session.query(Movie.title).join(Rating).\
            filter(Rating.movie_id == movie_id).first()

        db.session.commit()
        return render_template('rating.html', rating_value=rating_value, title=title[0])

    return render_template("movies.html", movies=movies, tags=tags, links=links)

@app.route('/recommendations', methods=['GET', 'POST'])
#@login_required  # User must be authenticated
def recommendations():

    # NOTE_ this is currently done with a set user ID = 1 for testing purposes
    your_user_id = 1  # later on current_user would be used 

    ratings = Rating.query.all()

    # Create a pandas DataFrame from the list of tuples
    df = pd.DataFrame([(r.user_id, r.movie_id, r.rating) for r in ratings], columns=['user_id', 'movie_id', 'rating'])

    # Create a Surprise Reader
    reader = Reader(rating_scale=(1, 5))

    # Load the dataset from SQLAlchemy models
    data = Dataset.load_from_df(df[["user_id", "movie_id", "rating"]], reader)

    # Get the movies that the current user has rated (only needd so we can get unrated_movies afterwards)
    rated_movies = [row[0] for row in db.session.query(Rating.movie_id).filter_by(user_id=current_user.id).all()]
    # Get all movies excluding the ones the user has rated
    unrated_movies = db.session.query(Movie).filter(~Movie.id.in_(rated_movies)).all()

    similar_users, predictions = recommended(data, unrated_movies, your_user_id)

    # Get the top 3 movies with the best predictions
    top_movies = sorted(predictions.items(), key=lambda x: x[1], reverse=True)[:3]

    return render_template("recommendations.html", your_user_id=your_user_id, similar_users=similar_users, top_movies=top_movies)



# Start development web server
if __name__ == '__main__':
    app.run(port=5000, debug=True)
