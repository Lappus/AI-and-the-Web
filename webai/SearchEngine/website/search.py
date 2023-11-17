from flask import Blueprint

search = Blueprint('search', __name__)

@search.route('/search')
def search():
    return "hier"

