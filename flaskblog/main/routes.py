from flask import render_template, url_for, redirect, request, session, Blueprint
from flaskblog import db
import MySQLdb.cursors


main = Blueprint('main', __name__)

@main.route('/home', methods=['GET', 'POST'])
def home():
	if request.method == 'POST':
		title = request.form['title']
		content = request.form['content']
		user_id = request.form['user_id']
		cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
		cur.execute("INSERT INTO posts (title, content, user_id) VALUES (%s, %s, %s)", (title, content, user_id))
		db.connection.commit()
		return redirect (url_for('postings.posts'))
	if 'loggedin' in session:
		return render_template('home.html', username=session['username'], user_id=session['id'])
	return redirect(url_for('users.login'))