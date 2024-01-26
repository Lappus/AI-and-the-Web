# Our awesome CineMatch

**recommender.py:**

- routes, manages and renders the views of the movie recommender#
- checks if users are logged in

**average_rating**

- calculate the average rating for each movie and store it in the AverageRating table.

**models.py**

- contains the various db models for user, movie, link, tag, movie genre etc.

**poster.py**

- retrieves movie posters from the imdb page to use them in CineMatch

**read_data.py**

- reads the stored data from csv files into the SQLAlchemy db

**Extras:**

- it is very pretty, see for yourself :)
- search function
- recommendation filtered by genre
- movie overview ordering via ranking and alphabetically
- average ratings
