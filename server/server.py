from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.config.from_object('config.' + os.getenv('APP_CONFIG'))

from routes.api import *

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])