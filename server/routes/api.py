from server import app
from flask import request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import json
import datetime
import requests

jwt = JWTManager(app)
mongo = PyMongo(app)

@app.route('/api', methods=['GET'])
def api():
    return jsonify({ 'message': 'Welcome to Movies APIs' })

@app.route('/api/signin', methods=['POST'])
def signIn():
    name = request.json.get('name', None)
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    if not name or not email or not password:
        return jsonify({ 'message': 'Invalid parameters' }), 422

    db_users = mongo.db.users

    user = {
        'name': request.json['name'],
        'email': request.json['email'],
        'password': generate_password_hash(request.json['password']),
    }

    db_users.insert_one({ **user })
    
    return jsonify({
        'message': 'User created',
        'item': {
            'name': user['name'],
            'email': user['email'],
        }
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    if not email or not password:
        return jsonify({ 'message': 'Invalid parameters' }), 422

    db_users = mongo.db.users

    user = db_users.find_one({ 'email': email })

    if not user:
        return jsonify({ 'message': 'Invalid credentials' }), 401

    if check_password_hash(user['password'], password):
        access_token = create_access_token(identity=email, expires_delta=datetime.timedelta(hours=1))

        return jsonify({
            'access_token': access_token
        }), 200
    
    return jsonify({ 'message': 'Invalid credentials' }), 401

@app.route('/api/movies', methods=['GET'])
@jwt_required
def list():
    db_movies = mongo.db.movies
    movies = []
    
    for movie in db_movies.find({}, { '_id': False }):
        movies.append({
            'item': movie
        })
    
    return jsonify({ 'movies': movies }), 200

@app.route('/api/movies/<movie_id>', methods=['GET'])
@jwt_required
def show(movie_id):
    if not ObjectId.is_valid(movie_id):
        return jsonify({ 'message': 'Invalid parameters' }), 422

    db_movies = mongo.db.movies
    movie = db_movies.find_one({ '_id': ObjectId(movie_id) })
    
    if movie:
        movie['_id'] = str(movie['_id'])

        return jsonify({ 'item': movie }), 200

    return jsonify({ 'message': "Movie not found" }), 404

@app.route('/api/movies', methods=['POST'])
@jwt_required
def create():
    db_movies = mongo.db.movies
    movie = {}

    for prop in ['title', 'brazilian_title', 'year_of_production', 'director', 'genre', 'cast']:
        if not request.json.get(prop, None):
            return jsonify({ 'message': 'Invalid parameters' }), 422

        movie[prop] = request.json[prop]
    
    title = request.json.get('title', None)
    movies_with_title = db_movies.find({ 'title': title }).count()

    if movies_with_title > 0:
        return jsonify({
            'message': 'Duplicate title \'' + title + '\'',
        }), 409

    db_movies.insert_one(movie)

    created_movie = db_movies.find_one({ 'title': title })
    created_movie['_id'] = str(created_movie['_id'])
    
    return jsonify({
        'message': 'Movie created',
        'item': created_movie
    }), 201

@app.route('/api/movies/<movie_id>/update', methods=['PUT'])
@jwt_required
def update(movie_id):
    if not ObjectId.is_valid(movie_id):
        return jsonify({ 'message': 'Invalid parameters' }), 422

    if not request.data:
        return jsonify({ 'message': 'Invalid parameters' }), 422

    data = request.get_json()

    if len(data) == 0:
        return jsonify({ 'message': 'Invalid parameters' }), 422

    db_movies = mongo.db.movies
    title = request.json.get('title', None)

    if db_movies.find({ '_id': ObjectId(movie_id) }).count() == 0:
        return jsonify({
            'message': 'Movie not found',
        }), 404
    
    if title:
        movies_with_title = db_movies.find({ 'title': title }).count()

        if movies_with_title > 0:
            return jsonify({
                'message': 'Duplicate title \'' + title + '\'',
            }), 409

    movie = {}

    for prop in ['title', 'brazilian_title', 'year_of_production', 'director', 'genre', 'cast']:
        if prop in data:
            movie[prop] = data[prop]

    db_movies.update_one({ '_id': ObjectId(movie_id) }, { '$set': movie })

    updated_movie = db_movies.find_one({ '_id': ObjectId(movie_id) }, { '_id': False })

    return jsonify({
        'message': 'Movie updated',
        'item': updated_movie
    }), 200

@app.route('/api/movies/<movie_id>/delete', methods=['DELETE'])
@jwt_required
def delete(movie_id):
    if not ObjectId.is_valid(movie_id):
        return jsonify({ 'message': 'Invalid parameters' }), 422

    db_movies = mongo.db.movies
    deleted_movie = db_movies.find_one({ '_id': ObjectId(movie_id) })

    if deleted_movie:
        deleted_movie['_id'] = str(deleted_movie['_id'])

        db_movies.delete_one({ '_id': ObjectId(movie_id) })

        return jsonify({
            'message': 'Movie deleted',
            'item': deleted_movie
        }), 200
    
    return jsonify({
        'message': 'Movie not found',
    }), 404

@app.route('/api/movies/import-from-omdb', methods=['POST'])
@jwt_required
def import_from_omdb():
    movie_id = request.json.get('movie_id', None)

    if not movie_id:
        return jsonify({ 'message': 'Invalid parameters' }), 422

    # res = requests.get('http://www.omdbapi.com/?apikey=c39ccf6a&t=city+of+god')
    res = requests.get('http://www.omdbapi.com/?apikey=c39ccf6a&i=' + movie_id)

    if not res.ok:
        return jsonify({
            'message': 'An error occurred',
        }), 500
    
    db_movies = mongo.db.movies
    data = res.json()
    title = data['Title']

    movies_with_title = db_movies.find({ 'title': title }).count()

    if movies_with_title > 0:
        return jsonify({
            'message': 'Duplicate title \'' + title + '\'',
        }), 409

    movie = {}

    movie['title'] = data['Title']
    movie['brazilian_title'] = 'undefined'
    movie['year_of_production'] = data['Year']
    movie['director'] = data['Director']
    movie['genre'] = data['Genre']
    movie['cast'] = []

    for actor in data['Actors'].split(', '):
        actor_item = {
            "role": "undefined",
            "name": actor
        }

        movie['cast'].append(actor_item)

    db_movies.insert_one(movie)

    created_movie = db_movies.find_one({ 'title': title })
    created_movie['_id'] = str(created_movie['_id'])
    
    return jsonify({
        'message': 'Movie created',
        'item': created_movie
    }), 201

