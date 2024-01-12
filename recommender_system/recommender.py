# Contains parts from: https://flask-user.readthedocs.io/en/latest/quickstart_app.html

from flask import Flask, render_template, redirect, url_for, request, make_response
from flask_user import login_required, UserManager, current_user
from surprise import Dataset
from surprise import Reader
from surprise.model_selection import train_test_split
from surprise import KNNWithMeans
import pandas as pd
import re

from average_rating import calc_average_rating
from models import db, User, Movie, Tag, Link, MovieGenre, Rating, AverageRating
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
    USER_APP_NAME = "CineMatch"  # Shown in and email templates and page footers
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

@app.route('/', methods=['GET', 'POST'])
def home_page():
    search_performed = False
    movie_found = True
    movies = None
    links = {}
    average_ratings = {}

    #print("search contents:", request.form['search'].strip())

    # Handle search submission
    if request.method == 'POST' and 'search' in request.form and request.form['search'].strip():
        search_performed = True
        search_query = request.form.get('search')
        search_query = re.sub('[^A-Za-z0-9]+', '', search_query)
        movies = Movie.query.filter(Movie.title.like(f'%{search_query}%')).all()
        movie_found = bool(movies)

    # If there's no search or if search returns no results, display top movies
    if not movies:
        top_movies = db.session.query(AverageRating).order_by(AverageRating.rating.desc()).limit(10).all()
        extracted_ids = [ar.movie_id for ar in top_movies]
        movies = [Movie.query.filter_by(id=id).first() for id in extracted_ids if Movie.query.filter_by(id=id).first()]

    # Collect additional information for each movie
    for m in movies:
        links[m.id] = Link.query.filter_by(movie_id=m.id).limit(10).all()
        average_ratings[m.id] = AverageRating.query.filter_by(movie_id=m.id).first()

    response = make_response(render_template("home.html", display_movies=movies, 
                                        movie_found=movie_found,
                                        search_performed=search_performed, 
                                        links=links, 
                                        average_ratings=average_ratings))

    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/movies', methods=['GET', 'POST'])
@login_required
def movies_page():
    user_id = current_user.id
    movies = None
    selected_tab = None  # No default tab
    genres = set([genre.genre for genre in MovieGenre.query.all()])  # Retrieve all genres

    # Check for tab selection
    if request.method == 'GET':
        sort_arg = request.args.get('sort')
        genre_arg = request.args.get('genre')
        print("sort_arg:", sort_arg)
        print("genre_arg:", genre_arg)

        if sort_arg == "genre":
            movies = Movie.query.join(MovieGenre).filter(MovieGenre.genre == genre_arg).all()
            selected_tab = 'genre'
        elif sort_arg == 'a_to_z':
            movies = Movie.query.order_by(Movie.title).all()
            selected_tab = 'a_to_z'
        elif sort_arg == 'ratings':
            movies = Movie.query.join(AverageRating).order_by(AverageRating.rating.desc()).all()
            selected_tab = 'ratings'

    # Handle rating submission
    if request.method == 'POST' and 'movie_id' in request.form:
        submit_rating(request, user_id)

    # If no movies or tab is selected, no movies will be displayed
    additional_data = retrieve_additional_movie_data(movies, user_id) if movies else {}
    print("movies outside:", movies)
    print("genres outside:", genres)
    print("selected-tab:", selected_tab)

    return render_template("movies.html", movies=movies, user_id=user_id, genres=genres, 
                            selected_tab=selected_tab, **additional_data)

"""# Movies view
@app.route('/movies', methods=['GET', 'POST'])
@login_required  # User must be authenticated
def movies_page():
    # String-based templates
    your_user_id = current_user
    user_id = current_user.id 
    movies = Movie.query.limit(10).all()
    tags = {}
    links = {}
    average_ratings = {} 
    user_ratings = Rating.query.filter_by(user_id=current_user.id).all()
    for movie in movies:
        tags.update({movie.id: Tag.query.filter_by(movie_id=movie.id).limit(10).all()})
        links.update({movie.id: Link.query.filter_by(movie_id=movie.id).limit(10).all()})
        average_ratings.update({movie.id: AverageRating.query.filter_by(movie_id=movie.id).first()})

    if request.method == 'POST':
        if 'movie_id' in request.form:
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
    

    return render_template("movies.html", movies=movies, tags=tags, links=links, average_ratings=average_ratings, user_id=user_id, user_ratings = user_ratings)
"""
@app.route('/recommendations', methods=['GET', 'POST'])
@login_required  # User must be authenticated
def recommendations():

    # NOTE_ this is currently done with a set user ID = 1 for testing purposes
    your_user_id = current_user  # later on current_user would be used 
    wanted_genre = None
    ratings = Rating.query.all()

    # Create a pandas DataFrame from the list of tuples
    df = pd.DataFrame([(r.user_id, r.movie_id, r.rating) for r in ratings], columns=['user_id', 'movie_id', 'rating'])

    # Create a Surprise Reader
    reader = Reader(rating_scale=(1, 5))

    # Load the dataset from SQLAlchemy models
    data = Dataset.load_from_df(df[["user_id", "movie_id", "rating"]], reader)

    # Get the movies that the current user has rated (only needd so we can get unrated_movies afterwards)
    rated_movies = [row[0] for row in db.session.query(Rating.movie_id).filter_by(user_id=current_user.id).all()]
    print(type(rated_movies))
    print(rated_movies.__len__())

    if rated_movies.__len__() >= 20:
        if request.method == 'POST':
            # get the genre from the html Code
            wanted_genre = request.form.get('genre')
            # get the movies in our db that have the wished genre 
            movies_with_genre = db.session.query(Movie).join(MovieGenre).\
                filter(MovieGenre.genre == wanted_genre).all()
            # get the repective movie ids
            movie_ids_with_genre = [movie.id for movie in movies_with_genre]

            # get all movies that the user hasn't rated and also that have the wanted genre
            unrated_movies_with_genre = db.session.query(Movie).filter(~Movie.id.in_(rated_movies)).\
                filter(Movie.id.in_(movie_ids_with_genre)).all()
        
            similar_users, predictions = recommended(data, unrated_movies_with_genre, your_user_id)

        else:

            # Get all movies excluding the ones the user has rated
            unrated_movies = db.session.query(Movie).filter(~Movie.id.in_(rated_movies)).all()
            similar_users, predictions = recommended(data, unrated_movies, your_user_id)

        # Get the top 3 movies with the best predictions
        top_movies = sorted(predictions.items(), key=lambda x: x[1], reverse=True)[:3]
         # extract the number of the sorted predictions since we get a tuple (Movie.id and rating)
        extracted_ids = [item[0] for item in top_movies]

    # If the user has less than 20 ratings we recommend the top 10 movies on average instead of personalized  recommendations
    else:
        #if genre is selected we recommend the top 10 movies with the selected genre
        if request.method == 'POST':
            # get the genre from the html Code
            wanted_genre = request.form.get('genre')
            # get the movies in our db that have the wished genre 
            top_movies = db.session.query(Movie).\
                            join(MovieGenre).\
                            filter(MovieGenre.genre == wanted_genre).\
                            outerjoin(AverageRating, Movie.id == AverageRating.movie_id).\
                            order_by(AverageRating.rating.desc()).\
                            limit(10).all()
            print("Not enough ratings to make recommendations")
            print("Top movies: ", top_movies)
            print("Top movies type: ", type(top_movies))
            print("Top movies length: ", top_movies.__len__())
            extracted_ids = [movie.id for movie in top_movies]
            print(extracted_ids)

        #else its just the top 10 movies on average regardless of genre 
        else:
            top_movies = db.session.query(AverageRating).order_by(AverageRating.rating.desc()).limit(10).all()
            print("Not enough ratings to make recommendations")
            print("Top movies: ", top_movies)
            print("Top movies type: ", type(top_movies))
            print("Top movies length: ", top_movies.__len__())
            extracted_ids = [movie.movie_id for movie in top_movies]
            print(extracted_ids)
            wanted_genre=None

        similar_users = None

    # use the function below to get the names
    top_movie_names = get_movie_names(extracted_ids)
    
    recommended_movies = []
    tags = {}
    links = {}
    average_ratings = {}
    # as for the Movie page: Collect the movies with the repective ids
    for id in extracted_ids:
        recommended_movie = Movie.query.filter_by(id = id).first()
        if recommended_movie:
            recommended_movies.append(recommended_movie)
    # get the tags and the links for the recommended movies
    for movie in recommended_movies:
        tags[movie.id] = Tag.query.filter_by(movie_id=movie.id).all()
        links[movie.id] = Link.query.filter_by(movie_id=movie.id).all()
        average_ratings.update({movie.id: AverageRating.query.filter_by(movie_id=movie.id).first()})
    # use the template to display the results 

    return render_template("recommendations.html", 
                           your_user_id=your_user_id, 
                           similar_users=similar_users, 
                           top_movies=top_movie_names, 
                           movies=recommended_movies, 
                           tags=tags, 
                           links=links,
                           average_ratings=average_ratings,
                           wanted_genre=wanted_genre)

# this function provides the movie names for the repective movie ids out of our db
def get_movie_names(movie_ids):
    movie_names=[]
    for movie_id in movie_ids:
        movie = Movie.query.filter_by(id=movie_id).first()
        if movie:
            movie_names.append(movie.title)
    return movie_names 

def submit_rating(request, user_id):
    movie_id = request.form.get('movie_id')
    rating_value = request.form.get('rating')

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

    # Fetch the movie title for the response
    #title = db.session.query(Movie.title).filter(Movie.id == movie_id).first()[0]
    #return render_template('rating.html', rating_value=rating_value, title=title)
    return redirect(url_for('movies_page'))

def retrieve_additional_movie_data(movies, user_id):
    """
    Retrieves additional data for a list of movies, such as tags, links, average ratings,
    and user-specific ratings.

    :param movies: List of Movie objects.
    :param user_id: ID of the current user (can be None if user is not logged in).
    :return: Dictionary containing tags, links, average ratings, and user ratings for each movie.
    """
    tags = {}
    links = {}
    average_ratings = {}
    user_ratings = {}

    for movie in movies:
        movie_id = movie.id
        tags[movie_id] = Tag.query.filter_by(movie_id=movie_id).all()
        links[movie_id] = Link.query.filter_by(movie_id=movie_id).all()
        average_ratings[movie_id] = AverageRating.query.filter_by(movie_id=movie_id).first()

        if user_id is not None:
            user_rating = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()
            user_ratings[movie_id] = user_rating.rating if user_rating else None

    return {
        'tags': tags,
        'links': links,
        'average_ratings': average_ratings,
        'user_ratings': user_ratings
    }


#calc_average_rating()
#initdb_command()

# Start development web server
if __name__ == '__main__':
    app.run(port=5000, debug=True)
