from flask import Flask, render_template
from crawler_mit_whoosh import request, search_index

app = Flask(__name__)
@app.route('/')

def home():
    return render_template('home.html')

@app.route("/search", methods=['GET', 'POST'])
def search_flask():
    if request.method =='GET':
        query = request.args.get('q')
        if query:
            matches = search_index(query.split())
            return render_template("search.html", matches=matches, query=query)
        else:
            return "Please enter a query"
    
    return render_template('search.html')
    
if __name__ == "__main__":
    app.run(debug=True)