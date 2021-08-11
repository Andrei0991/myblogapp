from flask import Flask
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from .libraries import *
from .config import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'f1743f5bb049f24e69ffeee14dfc8e6f'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'andrei'
app.config['MYSQL_PASSWORD'] = 'pulamea123'
app.config['MYSQL_DB'] = 'users_db'
db = Database()
bcrypt = Bcrypt(app)

from flaskblog.users.routes import users
from flaskblog.posts.routes import postings
from flaskblog.posts.posts_ajax import posts_ajax
from flaskblog.main.routes import main

app.register_blueprint(users)
app.register_blueprint(postings)
app.register_blueprint(main)
app.register_blueprint(posts_ajax, url_prefix="/posts-ajax")
