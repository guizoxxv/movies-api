from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId

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
    
    for movie in db_movies.find({}, { '_id': False }):
        movies.append({
            'item': movie
        })
    
    return jsonify({ 'movies': movies }), 200

@app.route('/api/movies/<movie_id>', methods=['GET'])
def show(movie_id):
    db_movies = mongo.db.movies
    
    movie = db_movies.find_one({ '_id': ObjectId(movie_id) }, { '_id': False })

    return jsonify({ 'item': movie }), 200

@app.route('/api/movies', methods=['POST'])
def create():
    db_movies = mongo.db.movies

    movie = {
        'title': request.json['title'],
        'brazilian_title': request.json['brazilian_title'],
        'year_of_production': request.json['year_of_production'],
        'director': request.json['director'],
        'genre': request.json['genre'],
        'cast': request.json['cast']
    }

    db_movies.insert({ **movie })
    
    return jsonify({
        'message': 'Movie created',
        'item': movie
    }), 201

@app.route('/api/movies/<movie_id>/update', methods=['PUT'])
def update(movie_id):
    db_movies = mongo.db.movies

    data = request.get_json()
    
    new_movie = { }

    if 'title' in data:
        new_movie['title'] = data['title']
    if 'brazilian_title' in data:
        new_movie['brazilian_title'] = data['brazilian_title']
    if 'year_of_production' in data:
        new_movie['year_of_production'] = data['year_of_production']
    if 'director' in data:
        new_movie['director'] = data['director']
    if 'genre' in data:
        new_movie['genre'] = data['genre']
    if 'cast' in data:
        new_movie['cast'] = data['cast']

    db_movies.update_one({ '_id': ObjectId(movie_id) }, { '$set': { **new_movie } })
    
    return jsonify({
        'message': 'Movie updated',
        'item': new_movie
    }), 200

@app.route('/api/movies/<movie_id>/delete', methods=['DELETE'])
def delete(movie_id):
    db_movies = mongo.db.movies

    movie = db_movies.find_one({ '_id': ObjectId(movie_id) }, { '_id': False })
    db_movies.delete_one({ '_id': ObjectId(movie_id) })

    return jsonify({
        'message': 'Movie deleted',
        'item': movie
    })

if __name__ == '__main__':
    app.run(debug=True)