from surprise import Dataset
from surprise import Reader
from surprise.model_selection import train_test_split
from surprise import KNNWithMeans
import pandas as pd

from models import db, User, Movie, Tag, Link, MovieGenre, Rating    

def recommended(data, unrated_movies, your_user_id):
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
    
    return similar_users, predictions