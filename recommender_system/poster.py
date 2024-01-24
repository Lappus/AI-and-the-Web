import requests
from bs4 import BeautifulSoup

def get_poster_url(imdb_url):
    """
    Get the URL of the poster image from the IMDb page.

    Parameters
    ----------
    imdb_url : str
        The IMDb URL of the movie
    """
    response = requests.get(imdb_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the tag and class containing the poster image URL
    # The specifics of this will depend on IMDb's current page structure
    poster_tag = soup.find('div', class_="ipc-media--poster-27x40")
    if poster_tag:
        print("yay")
        #poster_url = poster_tag.img['src']
        #return poster_url
    else:
        return None  # or a default poster image URL

# Example usage
imdb_url = 'https://www.imdb.com/title/tt0113277/'
poster_url = get_poster_url(imdb_url)
print(poster_url)