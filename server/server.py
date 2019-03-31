from flask import Flask, request, jsonify
# from pymongo import MongoClient
from flask_mongoalchemy import MongoAlchemy

app = Flask(__name__)

# client = MongoClient('mongodb://root:root@172.17.0.1:3012/')

# db = client.movies_api

app.config['MONGOALCHEMY_DATABASE'] = 'movies_api'
app.config['MONGOALCHEMY_SERVER'] = '172.17.0.1'
app.config['MONGOALCHEMY_PORT'] = '3012'
app.config['MONGOALCHEMY_USER'] = 'root'
app.config['MONGOALCHEMY_PASSWORD'] = 'root'

db = MongoAlchemy(app)

class Example(db.Document):
    name = db.StringField()

@app.route('/', methods=['GET'])
def home():
    return jsonify({ 'message': 'Hello World' })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')