from flask import Flask, request, render_template
import crawler
from spellchecker import SpellChecker
import re

# ------------------------------------------- Initialize whoosh Index with first URL --------------------------------

crawler.spider("index_dir","https://vm009.rz.uos.de/crawl/")

# -------------------------------------------- FLASK PART ------------------------------------------

# What does this do exactly? 
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
        print("query:",query)
        # Check for potential typos and get suggestions
        suggestions = {}
        misspelled = spell.unknown(re.split(', |\s', query))
        correctly_spelled = spell.known(re.split(', |\s', query))
        print("misspelled:",misspelled, type(misspelled))
        print("coorect:",correctly_spelled, type(correctly_spelled))
        if misspelled:
            suggestions = {spell.correction(word) for word in misspelled}
            print("suggest")
            print(suggestions)
            
            if correctly_spelled and (not bool(suggestions)):
                print("1")
                query = list(suggestions.union(correctly_spelled))
                print(query)
            elif (bool(suggestions)):
                print("2")
                print(suggestions)
                query = " ".join(suggestions)+" " + " ".join(correctly_spelled)
            elif correctly_spelled:
                print("3")
                print(correctly_spelled)
                query = " ".join(correctly_spelled)
                print(query)
            #print("n.q", query, type(query))
            # get the matching websites to the query 
            # if there are misspelled words, we pass the corrected suggestions
            print("matches query:", query)
            matches = crawler.search_function(query=re.split(', |\s', query))
            print("match1:", matches)
            #return render_template("search.html", matches=matches, query=query, suggestions=suggestions)
        else:
            #print("q.v", query.split(), type(query.split()))
            # if there are no misspelled words, we just pass the original query
            matches = crawler.search_function(query=re.split(', |\s', query))
            print("match2:", matches)
        return render_template("search.html", matches=matches, query=query, suggestions=suggestions, misspelled=misspelled)
    
    else:
        return render_template("home.html", text_field="No query detected :(" )

# creates a third view, that shows the search history    
@app.route("/history", methods=["GET"])
def search_h():
    if search_history:
        print("search history:", search_history[-10:])
        return render_template("search_history.html", search_history=search_history[-10:], empty=False)
    else:
        return render_template("search_history.html", search_history=search_history, empty=True)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

import traceback
@app.errorhandler(500)
def internal_error(exception):
   return "<pre>"+traceback.format_exc()+"</pre>"