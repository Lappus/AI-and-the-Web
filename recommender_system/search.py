from surprise import Dataset
from surprise import Reader
from surprise.model_selection import train_test_split
from surprise import KNNWithMeans
import pandas as pd

from models import db, User, Movie, Tag, Link, MovieGenre, Rating    

def recommended(data, unrated_movies, your_user):
    # Split the data into training and testing sets - right now we only work with the training set
    trainset, testset = train_test_split(data, test_size=0.001)
    
    # Use user-based collaborative filtering with KNNWithMeans
    sim_options = {
        "name": "cosine",
        "user_based": True,  #User-based similarity
        "random_state": 42       #specific random seed for reproducibility
    }
    algo = KNNWithMeans(sim_options=sim_options)

    # Train the algorithm on the training set
    algo.fit(trainset)

    # Convert external user ID to internal user index
    try:
        internal_user_id = trainset.to_inner_uid(your_user.id)
        print(internal_user_id)
        print("internal_user_id found in trainset")
    except ValueError:
        # Handle the case where the user ID is not in the trainset
        internal_user_id = None
        print("User ID not found in trainset")

    # Get neighbors only if the user ID was found in the trainset
    similar_users = []
    if internal_user_id is not None:
        similar_users = algo.get_neighbors(internal_user_id, k=3)
    
    # Get the similarity scores between the target user and other users
    similarity_scores = algo.sim[:, internal_user_id] if internal_user_id is not None else []

    predictions = {}
    for movie in unrated_movies:
        # Calculate the weighted average prediction for the movie
        weighted_sum = 0
        similarity_sum = 0

        for similar_user, similarity in zip(similar_users, similarity_scores):
            try:
                # Convert movie ID to internal item index
                internal_movie_id = trainset.to_inner_iid(movie.id)
                # Get the rating if it exists
                rating = 0.0
                for item in trainset.ur[similar_user]:
                    print(item)
                    if item[0] == internal_movie_id:
                        rating = item[1]
                        print("rating found in trainset")
                        break
            except ValueError:
                # Handle the case where the movie ID is not in the trainset
                rating = None

            if rating is not None:
                # Update the weighted sum and similarity sum
                weighted_sum += similarity * rating
                similarity_sum += abs(similarity)

        # Avoid division by zero
        if similarity_sum != 0:
            # Calculate the predicted rating
            predicted_rating = weighted_sum / similarity_sum
            predictions[movie.id] = predicted_rating
    
    return similar_users, predictions