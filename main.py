from flask import Flask, request, render_template
import crawler
from spellchecker import SpellChecker
import re

# ------------------------------------------- Initialize whoosh Index with first URL --------------------------------

crawler.spider("index_dir","https://vm009.rz.uos.de/crawl/")

# -------------------------------------------- FLASK PART ------------------------------------------
#Initialize the flask frame
app = Flask(__name__)

# Initialize the spellchecker
spell = SpellChecker()

# List for future search history 
search_history = []

# creates the first view, a start page where user can input query
@app.route("/", methods=["GET"])
def home():
    return render_template("home.html", text_field="Search anything")

# creates the second view, a result page with the corresponding matches to query
@app.route("/search", methods=["GET"])
def search():
    # safe the query from start view
    query = request.args.get('q').lower()

    # first check if there is actually user input
    if query:
        search_history.append(query)

        # Check for potential typos and get suggestions
        suggestions = {}
        misspelled = spell.unknown(re.split(r', |\s', query))
        correctly_spelled = spell.known(re.split(r', |\s', query))
        #print("misspelled:",misspelled, type(misspelled))
        #print("coorect:",correctly_spelled, type(correctly_spelled))
        if misspelled:
            suggestions = {spell.correction(word) for word in misspelled}
            #print("suggest",type(suggestions))
            
            query = list(suggestions.union(correctly_spelled))
            #print("n.q", query, type(query))
            # get the matching websites to the query 
            # if there are misspelled words, we pass the corrected suggestions
            matches = crawler.search_function(query=list(query))
            #return render_template("search.html", matches=matches, query=query, suggestions=suggestions)
        else:
            # if there are no misspelled words, we just pass the original query
            matches = crawler.search_function(query=re.split(r', |\s', query))
        print("match:", matches)
        return render_template("search.html", matches=matches, query=str(query).replace('[\'', '').replace('\']', ''), suggestions=suggestions, misspelled=misspelled)
     # if there is no query at all
    else:
        return render_template("home.html", text_field="No query detected :(" )

# creates a third view, that shows the search history if there is one
@app.route("/history", methods=["GET"])
def search_h():
    if search_history:
        return render_template("search_history.html", search_history=search_history[-10:], empty=False)
    else:
        return render_template("search_history.html", search_history=search_history, empty=True)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

import traceback
@app.errorhandler(500)
def internal_error(exception):
   return "<pre>"+traceback.format_exc()+"</pre>"