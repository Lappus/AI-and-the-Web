from flask import Flask, request, render_template, Blueprint
# creates the first view, a start page where user can input query

app = Flask(__name__)
@app.route('/')

def create_app():
    app = Flask(__name__)
    # Secret Key for encrypting the code
    app.config['SECRET_KEY'] = 'ultimativ geheim'

    import home, search

    app.register_blueprint(home)
    app.register_blueprint(search)

    return app

if __name__ == "__main__":
    app.run(debug=True)
