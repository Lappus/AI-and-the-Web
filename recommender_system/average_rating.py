import numpy as np
from models import db, Movie, Rating, AverageRating

def calc_average_rating():
    for movie in Movie.query.all():
        movie_id = movie.id
        ratings = Rating.query.filter_by(movie_id=movie_id).all()

        if ratings:
            rating_values = [rating.rating for rating in ratings]
            average_rating = np.mean(rating_values)
            #round the rating so we only have two digits after the dot
            average_rating = round(average_rating, 2)
            new_average_rating = AverageRating(movie_id = movie_id, rating = average_rating)
            # Checking if there already exits an average rating for a movie
            existing_average_rating = AverageRating.query.filter_by(movie_id=movie_id).first()

            # We would get an error if we would always try to overwrite the average_rating
            if existing_average_rating:
                # Update the existing entry
                existing_average_rating.rating = average_rating
            else:
                # Add a new AverageRating entry
                new_average_rating = AverageRating(movie_id=movie_id, rating=average_rating)
                db.session.add(new_average_rating)
    db.session.commit()


