import csv
from sqlalchemy.exc import IntegrityError
from models import Movie, MovieGenre, Link, Tag, Rating, User
import re


def clean_title(title):
    return re.sub("[^a-zA-Z0-9 ]", "", title)

def check_and_read_data(db_session):
    # check if we have movies in the database
    # read data if database is empty

    if Movie.query.count() == 0:
        # read movies from csv
        with open('data/movies.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    try:
                        id = row[0]
                        title = row[1]
                        movie = Movie(id=id, title=title)
                        # movie = Movie(id=id, title=title, clean_title=clean_title(title))
                        db_session.add(movie)
                        genres = row[2].split('|')  # genres is a list of genres
                        for genre in genres:  # add each genre to the movie_genre table
                            movie_genre = MovieGenre(movie_id=id, genre=genre)
                            db_session.add(movie_genre)
                        db_session.commit()  # save data to database
                    except IntegrityError:
                        print("Ignoring duplicate movie: " + title)
                        db_session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, " movies read")
                # read only first 500 entries for testing
                if count == 100:
                    break

    if Link.query.count() == 0:
        # read movies from csv
        with open('data/links.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    try:
                        movie_id = row[0]
                        imdb_id = row[1]
                        tmdb_id = row[2]
                        link = Link(movie_id = movie_id, imdb_id= imdb_id, tmdb_id =tmdb_id)
                        db_session.add(link)
                        db_session.commit()
                    except IntegrityError:
                        print("Ignoring duplicate link: " + movie_id)
                        db_session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, " links read")
                # read only first 500 entries for testing
                if count == 100:
                    break

    if Tag.query.count() == 0:
        # read movies from csv
        with open('data/tags.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    try:
                        user_id = row[0]
                        movie_id = row[1]
                        tag = row[2]
                        timestamp = row[3]
                        tag = Tag(user_id = user_id, movie_id= movie_id, tag= tag, timestamp=timestamp)
                        db_session.add(tag)
                        db_session.commit()
                    except IntegrityError:
                        print("Ignoring duplicate tag: " + user_id + " " + movie_id)
                        db_session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, " tags read")
                # read only first 500 entries for testing
                if count == 100:
                    break
    
    if Rating.query.count() == 0:
        # read Ratings from csv
        with open('data/ratings.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    try:
                        user_id = row[0]
                        movie_id = row[1]
                        rating = row[2]
                        timestamp = row[3]
                        rating= Rating(user_id=user_id, movie_id=movie_id, rating=rating)
                        db_session.add(rating)
                        db_session.commit()
                    except IntegrityError as e:
                        print("Error inserting rating:", e)
                        db_session.rollback()
                        pass
                count += 1
                if count % 5000 == 0:
                    print(count, " Ratings read")
                # read only first 1000 entries for testing
                if count == 5000:
                    break

      
    if User.query.count() == 0:
        # read users from csv
        with open('data/ratings.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    try:
                        user_id = row[0]
                        # Check if the user with the given ID already exists
                        existing_user = User.query.filter_by(id=user_id).first()

                        if not existing_user:
                            user = User(active=False, id=user_id, password="n.a.", username=f"User_{user_id}")
                            db_session.add(user)
                            db_session.commit()
                    except IntegrityError as e:
                        print("Error inserting user:", e)
                        db_session.rollback()
                        pass
                count += 1
                if count % 5000 == 0:
                    print(count, "user read")
                # read only first 5000 entries for testing
                if count == 5000:
                    break


