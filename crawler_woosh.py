import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin 
import whoosh 
import os, os.path




# Crawler 
queue = ["https://vm009.rz.uos.de/crawl/"]
visited_links = set()
dictionary = {}

# Create a folder for the index to be saved
# Check if an index exists and open if possible

try:
    ix = index.open_dir("indexdir")
except:
    if not os.path.exists("indexdir"):
        os.mkdir("indexdir")
        ix = index.create_in("indexdir", whoosh.fields.text)

# Create the writer for adding docs to the index
writer = ix.writer()

def spider():
    while queue:
        # Getting the next URL to search through
        current_url = queue.pop(0)
        
        # But only the ones we haven't searched yet
        if current_url not in visited_links:

            request = requests.get(current_url).text
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
def search(index = dictionary, words = []):
    # List of all matching keys (optional)
    matching_keys = []
    for key in index:
        # Bool variable if all words were found on the site 
        all_words_found = all(word in index[key] for word in words)
        if all_words_found:
            # optional
            matching_keys.append(key)
            # Results
            print('Words found in: '+ key)       

search(['platypus', 'mammal', 'endemic', 'eastern'])
