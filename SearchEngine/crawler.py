import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin 


# Crawler 
queue = ["https://vm009.rz.uos.de/crawl/"]
visited_links = []
dictionary = {}

def spider():
    while queue:
        # Getting the next URL to search through
        current_url = queue.pop(0)
        
        # But only the ones we haven't searched yet
        if current_url not in visited_links:
            request = requests.get(current_url)
            plain_text = request.text
            soup = BeautifulSoup(plain_text, 'html.parser')
            words = soup.get_text().split()

            visited_links.append(current_url)

            # Add the URL and all included words to the dictionary
            dictionary[current_url] = []
            dictionary[current_url].extend(words)
            
            for link in soup.find_all('a'):
                href = link.get('href')

                # fusing the main URL with the new href part of the link
                if href:
                    absolute_url = urljoin(current_url, href)

                    if absolute_url.startswith("https://vm009.rz.uos.de/crawl/") and absolute_url not in visited_links:
                        queue.append(absolute_url)

spider()

# Search function
def search(words = []):
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

search(['platypus', 'mammal', 'endemic', 'eastern'])
