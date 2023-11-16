import os
import whoosh
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin 
from flask import Flask, request, render_template

# Create a folder for the index to be saved
# Check if an index exists and open if possible

# -----------------------------------------  whoosh index  -----------------------------------------

def spider(index_path, website):
    """
    Crawls the given website and sub-pages for html content
    Creates an index at the given path

    Params:
    index_path: path of the directory where the index will be saved
    website: string http-link of the searched website
    """
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
    visited_links = set()

    while queue:
        # Getting the next URL to search through
        current_url = queue.pop(0)
        
        # But only the ones we haven't searched yet
        if current_url not in visited_links:

            request = requests.get(current_url, timeout=4).text
            soup = BeautifulSoup(request, 'html.parser')
            # We don't need the meta data of the html, only content related text
            words = soup.get_text()
            # Update already visited list
            visited_links.add(current_url)

            # Add the URL and all included words to the writer of the index
            writer.add_document(title = current_url, content = words)
            # added a print statement to follow code and it seems that "Home page" is called twice
            # even though it should be excluded due to "visited_links" check, right?
            # why does that not work?
            print(str(soup.title))
            

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
    writer.commit()

# -----------------------------------------  Search function   -----------------------------------------

def search_function(index_path, query):
    """
    Searches the given whoosh index for the given words

    Params:
    index_path: path where the whoosh index is saved
    query: words string that will be searched

    """
   
    ix = whoosh.index.open_dir(index_path)
    # join the list of words into a string
    query = "".join(query)

    with ix.searcher() as searcher: 
        # find entries with the words in query
        query = QueryParser("content", ix.schema).parse(query)
        results = searcher.search(query)
        hits = [hit.fields() for hit in results]

    return hits