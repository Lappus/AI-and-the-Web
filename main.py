from flask import Flask, request, render_template
import crawler
from spellchecker import SpellChecker

# ------------------------------------------- Initialize whoosh Index with first URL --------------------------------

crawler.spider("indexdir","https://vm009.rz.uos.de/crawl/")

# -------------------------------------------- FLASK PART ------------------------------------------

# What does this do exactly? 
app = Flask(__name__)

# Initialize the spellchecker
spell = SpellChecker()

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

        # Check for potential typos and get suggestions
        misspelled = spell.unknown(query.split())
        suggestions = {word: spell.correction(word) for word in misspelled}

        # get the matching websites to the query 
        matches = crawler.search_function(index_path="indexdir", query=suggestions.values())
        return render_template("search.html", matches=matches, query=query, suggestions=suggestions)
    else:
        return "Please enter a query."