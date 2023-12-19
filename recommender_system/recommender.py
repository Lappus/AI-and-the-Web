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
        
        title = db.session.query(Movie.title).join(Rating).\
            filter(Rating.movie_id == movie_id).first()

        db.session.commit()
        return render_template('rating.html', rating_value=rating_value, title=title[0])

    return render_template("movies.html", movies=movies, tags=tags, links=links, rating=rating_value)

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

    # Split the data into training and testing sets - right now I only work with the training set
    trainset, testset = train_test_split(data, test_size=0.05)

    # Use user-based collaborative filtering with KNNWithMeans
    sim_options = {
        "name": "cosine",
        "user_based": True,  #User-based similarity
        "random_state": 42       #specific random seed for reproducibility
    }
    algo = KNNWithMeans(sim_options=sim_options)

    # Train the algorithm on the training set
    algo.fit(trainset)

    similar_users = algo.get_neighbors(your_user_id, k=3)  # Get 3 similar users

    # Get the similarity scores between the target user and other users
    similarity_scores = algo.sim[:, your_user_id]

    # Get the movies that the current user has rated
    rated_movies = [row[0] for row in db.session.query(Rating.movie_id).filter_by(user_id=current_user.id).all()]

    # Get all movies excluding the ones the user has rated
    unrated_movies = db.session.query(Movie).filter(~Movie.id.in_(rated_movies)).all()

    predictions = {}
    for movie in unrated_movies:
        # Calculate the weighted average prediction for the movie
        weighted_sum = 0
        similarity_sum = 0

        for similar_user, similarity in zip(similar_users, similarity_scores):
            # Get the rating of the similar user for the movie
            rating = algo.trainset.ur[similar_user]
            rating = next((r[1] for r in rating if r[0] == movie.id), None)

            if rating is not None:
                # Update the weighted sum and similarity sum
                weighted_sum += similarity * rating
                similarity_sum += abs(similarity)

        # Avoid division by zero
        if similarity_sum != 0:
            # Calculate the predicted rating
            predicted_rating = weighted_sum / similarity_sum
            predictions[movie.id] = predicted_rating

    # Get the top 3 movies with the best predictions
    top_movies = sorted(predictions.items(), key=lambda x: x[1], reverse=True)[:3]

    return f"Users similar to User {your_user_id}: {similar_users} Top movies with respective estimated rating: {top_movies}"



# Start development web server
if __name__ == '__main__':
    app.run(port=5000, debug=True)
