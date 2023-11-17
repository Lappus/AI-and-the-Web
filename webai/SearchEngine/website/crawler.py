import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin 
from flask import Flask, request, render_template, Blueprint
import os
import whoosh   
from whoosh.index import create_in 
from whoosh.fields import *
from whoosh.qparser import QueryParser

# Crawler 
dictionary = {}

def spider(index_path, website):
    #Schema for index creation
    schema = Schema(title=TEXT(stored=True), content=TEXT)

    # Create a folder for the index to be saved
    # Check if an index exists and open if possible
    if not os.path.exists(index_path):
        os.mkdir(index_path)
        ix = whoosh.index.create_in(index_path, schema)
    else:
        ix = whoosh.index.create_in(index_path, schema)

    # Create the writer for adding docs to the index
    writer = ix.writer()
    queue = [website]
    visited_links = []

    while queue:
        # Getting the next URL to search through
        current_url = queue.pop(0)
        
        # But only the ones we haven't searched yet
        if current_url not in visited_links: 
                request = requests.get(current_url, timeout=4).text
                soup = BeautifulSoup(request, 'html.parser')
                words = soup.get_text().split()

                visited_links.append(current_url)

                # Add the URL and all included words to the dictionary
                writer.add_document(title = str(soup.title), content = words)
                writer.commit()
                
                for link in soup.find_all('a'):
                    href = link.get('href')

                    # fusing the main URL with the new href part of the link
                    if href:
                        absolute_url = urljoin(current_url, href)

                        if absolute_url.startswith("https://vm009.rz.uos.de/crawl/") and absolute_url not in visited_links:
                            queue.append(absolute_url)
                    
spider("indexdir","https://vm009.rz.uos.de/crawl/")

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
            print('Words found in: '+ key) 
        if matching_keys:
            return matching_keys
        else:
            return None       


#home = Blueprint('home', __name__)

#@home.route('/')
#def home():
#   return render_template("start.html")

#search = Blueprint('search', __name__)

#@search.route('/search')
#def search():
#    return "hier"
