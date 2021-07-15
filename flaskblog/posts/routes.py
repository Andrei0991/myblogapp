from flask import render_template, url_for, redirect, request, session, Blueprint
from flaskblog import db
import MySQLdb.cursors


postings = Blueprint('postings', __name__)


@postings.route('/posts', methods=['GET', 'POST'])
def posts():
	if 'loggedin' in session:
		cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
		cur.execute(f"SELECT * FROM posts LEFT JOIN users ON users.idUser = posts.idUser WHERE statusPost = 1 AND statusUser = 1 ORDER BY posts.datePosted DESC")
		post_details = cur.fetchall()
		cur.execute(f"SELECT * FROM comments LEFT JOIN users ON users.idUser = comments.idUser WHERE statusUser = 1 AND statusComment = 1 ORDER BY comments.dateComment ASC")
		comments = cur.fetchall()
		commentsAdded = {}
		for post in post_details:
			commentsAdded[post['idPost']] = []
		for comment in comments:
			commentsAdded[comment['idPost']].append(comment)
	return render_template('posts.html', post_details = post_details, username = session['username'], commentsAdded = commentsAdded)


@postings.route('/delete/<id_post>', methods=['GET', 'POST'])
def delete(id_post):
	cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
	cur.execute(f'DELETE FROM posts WHERE idPost = {id_post} AND statusPost = 1')
	db.connection.commit()
	return redirect (url_for('postings.posts'))


@postings.route('/update/<id_post>', methods=['GET', 'POST'])
def update(id_post):
	if request.method == "POST" and 'loggedin' in session:
		title = request.form['title']
		content = request.form['content']
		cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
		cur.execute(f'UPDATE posts SET title = %s, content = %s WHERE idPost = %s AND statusPost = 1', (title, content, id_post))
		db.connection.commit()
		return redirect(url_for('postings.posts'))
	cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute(f'SELECT * FROM posts WHERE idPost = %s', (id_post,))
	post = cursor.fetchone()
	return render_template('update.html', post = post)


@postings.route('/posts/<id_post>/comments', methods = ['GET', 'POST'])
def comments(id_post):
	if request.method == "POST":
		idPost = request.form['idPost']
		context = request.form['context']
		cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute("INSERT INTO comments (idPost, idUser, context) VALUES ('{0}', '{1}', '{2}')".format(idPost, session['id'], context, id_post))
		db.connection.commit()
		cursor.close()
		return redirect(url_for('postings.posts'))



@postings.route('/deleteComments/<id_post>', methods=['GET', 'POST'])
def deleteComments(id_post):
	cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
	cur.execute(f'DELETE FROM comments WHERE idComment = {id_post} AND statusComment = 1')
	db.connection.commit()
	return redirect (url_for('postings.posts'))




