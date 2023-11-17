from flask import Flask, request, render_template
import crawler
from spellchecker import SpellChecker 

# ------------------------------------------- Initialize whoosh Index with first URL --------------------------------

#crawler.spider("indexdir","https://vm009.rz.uos.de/crawl//crawl/")

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

    # first check if there is actually user input
    if query:
        print("query:",query)
        # Check for potential typos and get suggestions
        suggestions = {}
        misspelled = spell.unknown(query.split(", "))
        correctly_spelled = spell.known(query.split(", "))
        print("misspelled:",misspelled, type(misspelled))
        print("coorect:",correctly_spelled, type(correctly_spelled))
        if misspelled:
            suggestions = {spell.correction(word) for word in misspelled}
            print("suggest",type(suggestions))
            
            query = list(suggestions.union(correctly_spelled))
            print("n.q", query, type(query))
            # get the matching websites to the query 
            # if there are misspelled words, we pass the corrected suggestions
            matches = crawler.search_function(index_path="indexdir", query=list(query))
            #return render_template("search.html", matches=matches, query=query, suggestions=suggestions)
        else:
            print("q.v", query.split(), type(query.split()))
            # if there are no misspelled words, we just pass the original query
            matches = crawler.search_function(index_path="indexdir", query=query.split(", "))
        return render_template("search.html", matches=matches, query=query, suggestions=suggestions, misspelled=misspelled)
    
    else:
        return "Please enter a query."

if __name__ == "__main__":
    app.run(debug=True)