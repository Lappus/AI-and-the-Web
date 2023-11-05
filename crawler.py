import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin 
from flask import Flask, request, render_template


# Crawler 
queue = ["https://vm009.rz.uos.de/crawl/"]
visited_links = set()
dictionary = {}

def spider():
    while queue:
        # Getting the next URL to search through
        current_url = queue.pop(0)
        
        # But only the ones we haven't searched yet
        if current_url not in visited_links:

            request = requests.get(current_url, timeout=4).text
            soup = BeautifulSoup(request, 'html.parser')
            # We don't need the meta data of the html, only content related text
            words = soup.get_text().split()
            # Update already visited list
            visited_links.add(current_url)

            # Add the URL and all included words to the dictionary
            dictionary[current_url] = words
            
            # Update our stack of URLS
            # find the anchor elements in the html used to create hyperlinks
            for link in soup.find_all('a'):
                # retrieving the URL that the anchor points to
                href = link.get('href')

                # fusing the main URL with the new href part of the link
                if href:
                    absolute_url = urljoin(current_url, href)

                    if absolute_url.startswith("https://vm009.rz.uos.de/crawl/") and absolute_url not in visited_links:
                        queue.append(absolute_url)

spider()

# Search function
def search2(words = []):
    # List of all matching keys (optional)
    matching_keys = []
    for key in dictionary:
        # Bool variable if all words were found on the site 
        all_words_found = all(word in dictionary[key] for word in words)
        if all_words_found:
            # optional
            matching_keys.append(key)
            # Results
            #print('Words found in: '+ key)
    if matching_keys:
        return matching_keys
    else:
        return None       

#search(['platypus', 'mammal', 'endemic', 'eastern'])

#-------------------------------------------- FLASK PART ------------------------------------------

# WHat does this do exactly? 
app = Flask(__name__)

# creates the first view, a start page where user can input query
@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")

# creates the second view, a result page with the corresponding matches to query
@app.route("/search", methods=["GET"])
def search():
    # safe the query from start view
    query = request.args.get('q')
    if query:
        # get the matching websites to the query 
        matches = search2(query.split())
        return render_template("search.html", matches=matches, query=query)
    else:
        return "Please enter a query."
