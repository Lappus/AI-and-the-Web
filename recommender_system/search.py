
from surprise import Dataset
from surprise import Reader
from surprise.model_selection import train_test_split
from surprise import KNNWithMeans
from models import db, User, Movie, Tag, Link, MovieGenre, Rating

# Assuming you have a User model with a relationship named 'ratings'
# and a Rating model with columns 'user_id', 'movie_id', and 'rating'

# Load your SQLAlchemy models
users = User.query.all()
ratings = Rating.query.all()

# Create a Surprise Reader
reader = Reader(rating_scale=(1, 5))

# Load the dataset from SQLAlchemy models
data = Dataset.load_from_df([(r.user_id, r.movie_id, r.rating) for r in ratings], reader)

# Split the data into training and testing sets
trainset, testset = train_test_split(data, test_size=0.25)

# Use user-based collaborative filtering with KNNWithMeans
sim_options = {
    "name": "cosine",
    "user_based": True,  # User-based similarity
}
algo = KNNWithMeans(sim_options=sim_options)

# Train the algorithm on the training set
algo.fit(trainset)

# Replace 'your_user_id' with the ID of the user for whom you want to find similar users
your_user_id = 1  # Example user ID
similar_users = algo.get_neighbors(your_user_id, k=3)  # Get 5 similar users

print(f"Users similar to User {your_user_id}: {similar_users}")