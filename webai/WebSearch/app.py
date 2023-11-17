from flask import Flask, render_template
from crawler import request, search2

app = Flask(__name__)
@app.route('/')

def home():
    return render_template('home.html')

@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method =='GET':
        query = request.args.get('q')
        if query:
            matches = search2(query.split())
            return render_template("search.html", matches=matches, query=query)
        else:
            return "Please enter a query"
    
    return render_template('search.html')
    
if __name__ == "__main__":
    app.run(debug=True)