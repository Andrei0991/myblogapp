from flask import render_template, url_for, redirect, request, session, Blueprint
from flaskblog import db
import MySQLdb.cursors


main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home', methods=['GET', 'POST'])
def home():
	if request.method == 'POST':
		idUser = request.form['idUser']
		title = request.form['title']
		content = request.form['content']
		cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
		cur.execute("INSERT INTO posts (idUser, title, content) VALUES (%s, %s, %s)", (idUser, title, content))
		db.connection.commit()
		return redirect (url_for('postings.posts'))
	if 'loggedin' in session:
		return render_template('home.html', username=session['username'], idUser=session['id'])
	return redirect(url_for('users.login'))