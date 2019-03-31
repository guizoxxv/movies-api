from flask import Flask, request, jsonify
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:3012/movies_api"

mongo = PyMongo(app)

@app.route('/', methods=['GET'])
def home():
    return jsonify({ 'message': 'Hello World' })

@app.route('/api/movies', methods=['GET'])
def list():
    db_movies = mongo.db.movies

    movies = []
    
    for movie in db_movies.find():
        movies.append({
            'title': movie['title']
        })
    
    return jsonify(movies)

if __name__ == '__main__':
    app.run(debug=True)