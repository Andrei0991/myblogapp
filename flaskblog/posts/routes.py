from flask import render_template, url_for, redirect, request, session, Blueprint
from flaskblog import db
import MySQLdb.cursors


postings = Blueprint('postings', __name__)


@postings.route('/posts', methods=['GET', 'POST'])
def posts():
	if 'loggedin' in session:
		cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
		cur.execute(f"SELECT * FROM posts LEFT JOIN users ON users.id = posts.user_id ORDER BY posts.date_posted DESC")
		post_details = cur.fetchall()
	return render_template('posts.html', post_details=post_details, username=session['username'])

@postings.route('/delete/<id_post>', methods=['GET', 'POST'])
def delete(id_post):
	cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
	cur.execute(f'DELETE FROM posts WHERE id = {id_post}')
	db.connection.commit()
	return redirect (url_for('postings.posts'))

@postings.route('/update/<id_post>', methods=['GET', 'POST'])
def update(id_post):
	if request.method == "POST":
		title = request.form['title']
		content = request.form['content']
		cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
		cur.execute(f'UPDATE posts SET title = %s, content = %s WHERE id = %s', (title, content, id_post))
		db.connection.commit()
		return redirect(url_for('postings.posts'))
	cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT * FROM posts WHERE id = %s', (id_post,))
	post = cursor.fetchone()
	return render_template('update.html', post = post)







