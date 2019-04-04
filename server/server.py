from flask import Flask

app = Flask(__name__)

app.config.from_pyfile('config/app.py')

from routes.api import *

if __name__ == '__main__':
    app.run(debug=True)