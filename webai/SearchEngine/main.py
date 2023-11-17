from website import create_app

app = create_app()

#only if we run and not just import the file, it s gonna run
if __name__ == '__main__':
    #debug=True  --> automatically reruns the server once we made changes 
    app.run(debug=True)