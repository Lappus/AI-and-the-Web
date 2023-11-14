from flask import Flask, request, render_template

#-------------------------------------------- FLASK PART ------------------------------------------

# What does this do exactly? 
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
        matches = search(index_path="indexdir", query=query.split())
        return render_template("search.html", matches=matches, query=query)
    else:
        return "Please enter a query."
