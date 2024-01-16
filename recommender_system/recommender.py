# Contains parts from: https://flask-user.readthedocs.io/en/latest/quickstart_app.html

from flask import Flask, render_template, redirect, url_for, request, make_response, session
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

################################################################ HOME PAGE ################################################################
    
@app.route('/', methods=['GET', 'POST'])
def home_page():
    """
    Route for the home page of the application. 

    This route handles both GET and POST requests. It serves two primary functions: 
    1. Search: When a search query is posted, it filters the movies based on the search criteria. 
    2. Display: In the absence of a search query or when the search returns no results, 
       it displays the top 10 movies based on average ratings.

    On POST requests, this route also handles movie rating submissions made by authenticated users.

    The function retrieves additional data for each movie, such as tags, links, and ratings. 
    It also ensures that the home page does not cache the content to reflect real-time data.

    Returns:
        Response: A response object that renders the 'home.html' template with the necessary context, 
                  including movies, search flags, additional movie data, and the ID of the recently rated movie.
    """
    search_performed = False  
    movie_found = True  
    movies = None  

    # Handle search submission
    if request.method == 'POST' and 'search' in request.form and request.form['search'].strip():
        search_performed = True
        search_query = request.form.get('search')
        search_query = re.sub('[^A-Za-z0-9]+', '', search_query)  # Sanitize search query
        movies = Movie.query.filter(Movie.title.like(f'%{search_query}%')).all()
        movie_found = bool(movies)  # Check if any movie is found

    # Display top movies if no search or search returns no results
    if not movies:
        top_movies = db.session.query(AverageRating).order_by(AverageRating.rating.desc()).limit(10).all()
        extracted_ids = [ar.movie_id for ar in top_movies]
        movies = [Movie.query.filter_by(id=id).first() for id in extracted_ids]

    # Collect additional information for each movie
    user_id = current_user.id if current_user.is_authenticated else None
    additional_data = retrieve_additional_movie_data(movies, user_id) if movies else {}

    # Handle movie rating submission
    if request.method == 'POST' and 'movie_id' in request.form and user_id:
        submit_rating(request, user_id)

    # Retrieve the ID of the rated movie, if any, and clear it from session
    rated_movie_id = session.pop('rated_movie_id', None)

    # Render the home page template with the necessary data
    response = make_response(render_template("home.html", movies=movies, 
                                        movie_found=movie_found,
                                        search_performed=search_performed, 
                                        **additional_data,
                                        rated_movie_id=rated_movie_id))

    # Set cache control headers to prevent caching
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

################################################################ MOVIES OVERVIEW ################################################################

@app.route('/movies', methods=['GET', 'POST'])
@login_required
def movies_page():
    """
    Route for the movies page of the application, accessible only to logged-in users.

    This route handles both GET and POST requests. It serves the following primary functions:
    1. Display Movies: Based on the selected tab ('genre', 'a_to_z', or 'ratings'), it displays movies accordingly.
    2. Genre Filtering: If a specific genre is selected, only movies of that genre are displayed.
    3. Movie Ratings: Handles movie rating submissions by the user.

    The function retrieves additional data for each movie, such as tags, links, and ratings. 
    It maintains the state of the selected tab using session storage.

    Returns:
        Response: A response object that renders the 'movies.html' template with the necessary context, 
                  including movies, genre data, selected tab, and additional movie data.
    """
    user_id = current_user.id
    movies = None
    selected_tab = "genre"  # Initialize with a default tab

    # Retrieve all genres from the database
    genres = set([genre.genre for genre in MovieGenre.query.all()])

    # Get the sorting argument from URL or session
    sort_arg = request.args.get('sort') or session.get('sort_arg')
    genre_arg = request.args.get('genre')

    # Store the current sorting argument in session for persistence
    if sort_arg:
        session['sort_arg'] = sort_arg

    # Display movies based on selected tab and genre
    if sort_arg == "genre":
        selected_tab = 'genre'
        # Filter movies by selected genre, if any
        movies = Movie.query.join(MovieGenre).filter(MovieGenre.genre == genre_arg).all() if genre_arg else Movie.query.join(MovieGenre).all()
    elif sort_arg == 'a_to_z':
        # Sort movies alphabetically
        movies = Movie.query.order_by(Movie.title).all()
        selected_tab = 'a_to_z'
    elif sort_arg == 'ratings':
        # Sort movies by ratings
        movies = Movie.query.join(AverageRating).order_by(AverageRating.rating.desc()).all()
        selected_tab = 'ratings'

    # Handle movie rating submission by the user
    if request.method == 'POST' and 'movie_id' in request.form:
        submit_rating(request, user_id)

    # Retrieve additional data for movies such as tags, links, and user-specific ratings
    additional_data = retrieve_additional_movie_data(movies, user_id) if movies else {}
    
    # Render the movies page with the required data
    return render_template("movies.html", movies=movies, 
                           user_id=user_id, genres=genres, 
                           selected_tab=selected_tab, rating = False, **additional_data)

################################################################ RECOMMENDATIONS ################################################################

@app.route('/recommendations', methods=['GET', 'POST'])
@login_required  # User must be authenticated
def recommendations():

    your_user_id = current_user  # later on current_user would be used 
    wanted_genre = None
    ratings = Rating.query.all()

    # Create a pandas DataFrame from the list of tuples
    df = pd.DataFrame([(r.user_id, r.movie_id, r.rating) for r in ratings], columns=['user_id', 'movie_id', 'rating'])
    print(df)
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
            print("Unrated movies with genre: ", unrated_movies_with_genre)
            print(data)
            print("Rated movies: ", rated_movies)
            print("your user id: ", your_user_id)
            similar_users, predictions = recommended(data, unrated_movies_with_genre,current_user)

        else:
            print(data)
            print("Rated movies: ", rated_movies)
            print("your user id: ", your_user_id)
            # Get all movies excluding the ones the user has rated
            unrated_movies = db.session.query(Movie).filter(~Movie.id.in_(rated_movies)).all()
            similar_users, predictions = recommended(data, unrated_movies, current_user)
            print("Similar users: ", similar_users)
            print("Predictions: ", predictions)

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
                           your_user_id=current_user.id, 
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

    # Set session variable to indicate the rated movie
    session['rated_movie_id'] = movie_id
    
    db.session.commit()

    # Fetch the movie title for the response
    #title = db.session.query(Movie.title).filter(Movie.id == movie_id).first()[0]
    print("Rating submitted successfully")
    return render_template("movies.html", movies=None, 
                           user_id=user_id, genres=None, 
                           selected_tab=None, rating=True,)
    # Redirect to the referring page
    #return redirect(url_for('movies_page'))
    return
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
