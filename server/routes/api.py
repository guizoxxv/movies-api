from server import app, mongo
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from bson import ObjectId
import json
import datetime
import requests

jwt = JWTManager(app)

@app.errorhandler(400)
def bad_request(error):
    return jsonify({ 'message': 'Bad request' }), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({ 'message': 'Not found' }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({ 'message': 'Method not allowed' }), 405

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({ 'message': 'Internal server error' }), 500

@app.route('/api', methods=['GET'])
def api():
    return jsonify({ 'message': 'Welcome to Movies APIs' })

@app.route('/api/register', methods=['POST'])
def register():
    checkDataResult = checkData(request, ['name', 'email', 'password'])

    if checkDataResult:
        return checkDataResult

    data = request.get_json()

    db_users = mongo.db.users

    users_with_email = db_users.find({ 'email': data['email'] }).count()

    if users_with_email > 0:
        return jsonify({
            'message': 'Duplicate email \'' + data['email'] + '\'',
        }), 409

    user = {
        'name': data['name'],
        'email': data['email'],
        'password': generate_password_hash(data['password']),
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
    checkDataResult = checkData(request, ['email', 'password'])

    if checkDataResult:
        return checkDataResult

    data = request.get_json()

    db_users = mongo.db.users

    user = db_users.find_one({ 'email': data['email'] })

    if not user:
        return jsonify({ 'message': 'Invalid credentials' }), 401

    if check_password_hash(user['password'], data['password']):
        access_token = create_access_token(identity=data['email'], expires_delta=datetime.timedelta(hours=1))

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
    checkParamResult = checkParam(movie_id)

    if checkParamResult:
        return checkParamResult
    
    db_movies = mongo.db.movies
    movie = db_movies.find_one({ '_id': ObjectId(movie_id) })
    
    if movie:
        movie['_id'] = str(movie['_id'])

        return jsonify({ 'item': movie }), 200

    return jsonify({ 'message': "Movie not found" }), 404

@app.route('/api/movies', methods=['POST'])
@jwt_required
def create():
    props = ['title', 'brazilian_title', 'year_of_production', 'director', 'genre', 'cast']

    checkDataResult = checkData(request, props)
    
    if checkDataResult:
        return checkDataResult

    data = request.get_json()
    db_movies = mongo.db.movies
    movie = {}

    for prop in props:
        if prop == 'cast':
            for actor in data[prop]:
                if not 'name' in actor or not 'role' in actor:
                    return jsonify({ 'message': 'Invalid parameters' }), 422
        
        movie[prop] = data[prop]

    movies_with_title = db_movies.find({ 'title': data['title'] }).count()

    if movies_with_title > 0:
        return jsonify({
            'message': 'Duplicate title \'' + data['title'] + '\'',
        }), 409

    db_movies.insert_one(movie)

    created_movie = db_movies.find_one({ 'title': data['title'] })
    created_movie['_id'] = str(created_movie['_id'])
    
    return jsonify({
        'message': 'Movie created',
        'item': created_movie
    }), 201

@app.route('/api/movies/<movie_id>', methods=['PUT'])
@jwt_required
def update(movie_id):
    checkParamResult = checkParam(movie_id)

    if checkParamResult:
        return checkParamResult

    props = ['title', 'brazilian_title', 'year_of_production', 'director', 'genre', 'cast']

    checkDataResult = checkData(request, props, False)

    if checkDataResult:
        return checkDataResult

    data = request.get_json()
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

    for prop in data:
        movie[prop] = data[prop]

    db_movies.update_one({ '_id': ObjectId(movie_id) }, { '$set': movie })

    updated_movie = db_movies.find_one({ '_id': ObjectId(movie_id) }, { '_id': False })

    return jsonify({
        'message': 'Movie updated',
        'item': updated_movie
    }), 200

@app.route('/api/movies/<movie_id>', methods=['DELETE'])
@jwt_required
def delete(movie_id):
    checkParamResult = checkParam(movie_id)

    if checkParamResult:
        return checkParamResult

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

    res = requests.get('http://www.omdbapi.com/?apikey=' + os.getenv('OMDB_API_KEY') + '&i=' + movie_id)

    if not res.ok:
        return jsonify({
            'message': 'An error occurred',
        }), 500
    
    db_movies = mongo.db.movies
    data = res.json()

    movies_with_title = db_movies.find({ 'title': data['Title'] }).count()

    if movies_with_title > 0:
        return jsonify({
            'message': 'Duplicate title \'' + data['Title'] + '\'',
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

    created_movie = db_movies.find_one({ 'title': data['Title'] })
    created_movie['_id'] = str(created_movie['_id'])
    
    return jsonify({
        'message': 'Movie created',
        'item': created_movie
    }), 201

def checkData(request, props, required=True):
    if not request.data:
        return jsonify({ 'message': 'Invalid parameters' }), 422

    if len(request.get_json()) == 0:
        return jsonify({ 'message': 'Invalid parameters' }), 422

    if required:
        for prop in props:
            if not request.json.get(prop, None):
                return jsonify({ 'message': 'Invalid parameters' }), 422

    return None

def checkParam(param):
    if not ObjectId.is_valid(param):
        return jsonify({ 'message': 'Invalid parameters' }), 422

    return None
