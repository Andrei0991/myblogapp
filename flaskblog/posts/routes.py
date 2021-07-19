from flask import render_template, url_for, redirect, request, session, Blueprint
from flaskblog import db
# import MySQLdb.cursors
import re


postings = Blueprint('postings', __name__)


@postings.route('/posts', methods=['GET', 'POST'])
def posts():
	if 'loggedin' in session:
		post_details = db.select( """
									SELECT * 
									FROM posts 
									LEFT JOIN users ON users.idUser = posts.idUser 
									WHERE statusPost = 1 
									AND statusUser = 1 
									ORDER BY posts.datePosted DESC
								  """, False )
		comments = db.select( """
									SELECT * 
									FROM comments 
									LEFT JOIN users ON users.idUser = comments.idUser 
									WHERE statusUser = 1 
									AND statusComment = 1 
									ORDER BY comments.dateComment ASC
								  """, False )
		commentsAdded = {}
		db.query("""SET session sql_mode='NO_ENGINE_SUBSTITUTION'""")
		for post in post_details:
			commentsAdded[post['idPost']] = []
		for comment in comments:
			commentsAdded[comment['idPost']].append(comment)
		return render_template('posts.html', post_details = post_details, username = session['username'], commentsAdded = commentsAdded)
	return redirect (url_for('users.login'))


@postings.route('/delete/<id_post>', methods=['GET', 'POST'])
def delete(id_post):
	if session['id'] == True:
		# cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
		# cur.execute(f'DELETE FROM posts WHERE idPost = {id_post} AND statusPost = 1')
		# db.connection.commit()
		db.select("SELECT * FROM posts LEFT JOIN users ON users.idUser = posts.idUser")
		db.delete( f'DELETE FROM posts WHERE idPost = {id_post} AND statusPost = 1' )
	return redirect (url_for('postings.posts'))


@postings.route('/update/<id_post>', methods=['GET', 'POST'])
def update(id_post):
	if request.method == "POST" and session['id'] == True:
		title = request.form['title']
		content = request.form['content']
		# cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
		# cur.execute()
		# db.connection.commit()
		db.select("SELECT * FROM posts LEFT JOIN users ON users.idUser = posts.idUser")
		db.update( "UPDATE posts SET title = '{0}', content = '{1}' WHERE idPost = '{2}' AND statusPost = 1".format(title, content, id_post) )
		return redirect(url_for('postings.posts'))
	# cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
	# cursor.execute()
	post = db.select( "SELECT * FROM posts WHERE idPost = '{0}'".format(id_post) )
	return render_template('update.html', post = post)


@postings.route('/posts/<id_post>/comments', methods = ['GET', 'POST'])
def comments(id_post):
	errors = {}
	values = {}
	if request.method == "POST":
		if 'idPost' in request.form:
			if request.form['idPost'].isdigit():
				values['idPost'] = request.form['idPost']
			else:
				errors['idPost'] = "//////"
		else:
			errors['idPost'] = "...."

		if 'context' in request.form:
			if re.match( '^[a-zA-Z0-9\+\:\@\#\$\%\&\*\{\}\]\/\.\-\_\,\(\)\?\!\"\s]+$', request.form['context'] ):
				values['context'] = request.form['context']
			else:
				errors['context'] = "//////"
		else:
			errors['context'] = "...."

		if len( errors.keys() ) > 0:
			print(errors)
			return

		# db.insert("INSERT INTO comments (idPost, idUser, context) VALUES ('{0}', '{1}', '{2}')".format( values['idPost'], session['id'], values['context'], id_post))
		db.insert("INSERT INTO comments (idPost, idUser, context) VALUES ('{0}', '{1}', '{2}')".format( values['idPost'], session['id'], values['context'] ))
		# if not comment:
		# 	pass

		return redirect(url_for('postings.posts'))




@postings.route('/deleteComments/<id_post>', methods=['GET', 'POST'])
def deleteComments(id_post):
	if session['id'] == True:
		# cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
		db.select("SELECT * FROM comments LEFT JOIN users ON users.idUser = comments.idUser")
		db.delete(f'DELETE FROM comments WHERE idComment = {id_post} AND statusComment = 1')
		# db.connection.commit()
	return redirect (url_for('postings.posts'))


@postings.route('/edit/<id_comment>', methods = ['GET', 'POST'])
def edit(id_comment):
	if request.method == "POST" and session['id'] == True:
		context = request.form['context']
		# cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
		db.select("SELECT * FROM comments LEFT JOIN users ON users.idUser = comments.idUser")
		db.update("UPDATE comments SET context = '{0}' WHERE idComment = '{1}' AND statusComment = 1".format(context, id_comment))
		# db.connection.commit()
		return redirect(url_for('postings.posts'))
	# cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
	edit = db.select("SELECT * FROM comments WHERE idComment = '{0}'".format(id_comment,))
	# edit = cursor.fetchone()
	return render_template('edit_comment.html', edit = edit)

