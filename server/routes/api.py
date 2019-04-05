from server import app
from flask import request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import json

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

    db_users.insert({ **user })
    
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
        access_token = create_access_token(identity=email)

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
    db_movies = mongo.db.movies
    movie = db_movies.find_one({ '_id': ObjectId(movie_id) }, { '_id': False })

    return jsonify({ 'item': movie }), 200

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

    db_movies.insert(movie)

    created_movie = db_movies.find_one({ 'title': title })
    created_movie['_id'] = str(created_movie['_id'])
    
    return jsonify({
        'message': 'Movie created',
        'item': created_movie
    }), 201

@app.route('/api/movies/<movie_id>/update', methods=['PUT'])
@jwt_required
def update(movie_id):
    db_movies = mongo.db.movies
    title = request.json.get('title', None)
    
    if title:
        movies_with_title = db_movies.find({ 'title': title }).count()

        if movies_with_title > 0:
            return jsonify({
                'message': 'Duplicate title \'' + title + '\'',
            }), 409
    
    data = request.get_json()
    movie = {}

    for prop in ['title', 'brazilian_title', 'year_of_production', 'director', 'genre', 'cast']:
        if prop in data:
            movie[prop] = data[prop]

    db_movies.update_one({ '_id': ObjectId(movie_id) }, { '$set': movie })

    updated_movie = db_movies.find_one({ '_id': ObjectId(movie_id) })
    updated_movie['_id'] = str(updated_movie['_id'])

    return jsonify({
        'message': 'Movie updated',
        'item': updated_movie
    }), 200

@app.route('/api/movies/<movie_id>/delete', methods=['DELETE'])
@jwt_required
def delete(movie_id):
    db_movies = mongo.db.movies
    deleted_movie = db_movies.find_one({ '_id': ObjectId(movie_id) })
    deleted_movie['_id'] = str(deleted_movie['_id'])

    db_movies.delete_one({ '_id': ObjectId(movie_id) })

    return jsonify({
        'message': 'Movie deleted',
        'item': deleted_movie
    })