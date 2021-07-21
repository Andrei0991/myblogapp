from flask import render_template, url_for, redirect, request, session, Blueprint, abort
from flaskblog import db
import re, math

postings = Blueprint('postings', __name__)


@postings.route('/posts', defaults={'page': 1}, methods=['GET', 'POST'])
@postings.route('/posts/page/<int:page>')
def posts(page):
	if 'loggedin' in session:
		limit = 3
		offset = page*limit - limit
		next = page+1
		prev = page-1
		post_IDS = []

		count = db.select(""" SELECT count(*) AS count FROM posts """)
		count = count['count']
		pages = math.ceil(count / limit)
		post_details = db.select( """
									SELECT * 
									FROM posts 
									LEFT JOIN users ON users.idUser = posts.idUser 
									WHERE statusPost = 1 
									AND statusUser = 1 
									ORDER BY posts.datePosted DESC LIMIT {0} OFFSET {1}
								  """.format(limit, offset), False )
		for post in post_details:
			post_IDS.append(post['idPost'])
		
		comments = db.select( """
									SELECT * 
									FROM comments 
									LEFT JOIN users ON users.idUser = comments.idUser 
									WHERE statusUser = 1 
									AND statusComment = 1 AND idPost IN {0}
									ORDER BY comments.dateComment ASC
								  """.format(tuple(post_IDS)), False )
		
		commentsAdded = {}
		db.query("""SET session sql_mode='NO_ENGINE_SUBSTITUTION'""")
		if post_details:
			for post in post_details:
				commentsAdded[post['idPost']] = []
			if comments:
				for comment in comments:
					commentsAdded[comment['idPost']].append(comment)
		return render_template('posts.html', post_details = post_details, username = session['username'], commentsAdded = commentsAdded, next = next, prev = prev, pages = pages)
	return redirect (url_for('users.login'))


@postings.route('/delete/<id_post>', methods=['GET', 'POST'])
def delete(id_post):
	if session['id'] == True:
		db.delete( f'DELETE FROM posts WHERE idPost = {id_post} AND statusPost = 1' )
	return redirect (url_for('postings.posts'))


@postings.route('/update/<id_post>', methods=['GET', 'POST'])
def update(id_post):
	if request.method == "POST":
		title = request.form['title']
		content = request.form['content']
		if not id_post or not id_post.isdigit():
			return abort(404)
		user = db.select("SELECT idUser FROM posts WHERE statusPost = 1 AND idPost = {0}".format(id_post))
		if user and user['idUser'] is not None:
			if session['id'] != user['idUser']:
				return abort(404)
		db.update( "UPDATE posts INNER JOIN users ON posts.idUser = users.idUser SET title = '{0}', content = '{1}' WHERE idPost = '{2}' AND statusPost = 1".format(title, content, id_post) )
		return redirect( url_for('postings.posts') )
	post = db.select( "SELECT * FROM posts WHERE idPost = '{0}'".format(id_post) )
	return render_template( 'update.html', post = post )
	 


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
			errors['idPost'] = "..."

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

		db.insert("INSERT INTO comments (idPost, idUser, context) VALUES ('{0}', '{1}', '{2}')".format( values['idPost'], session['id'], values['context'] ))

	return redirect(url_for('postings.posts'))




@postings.route('/deleteComments/<id_post>', methods=['GET', 'POST'])
def deleteComments(id_post):
	if session['id'] == True:
		db.delete(f'DELETE FROM comments WHERE idComment = {id_post} AND statusComment = 1')
	return redirect (url_for('postings.posts'))
		
	


@postings.route('/edit/<id_comment>', methods = ['GET', 'POST'])
def edit(id_comment):
	if request.method == "POST":
		context = request.form['context']
		db.update("UPDATE comments SET context = '{0}' WHERE idComment = '{1}' AND statusComment = 1".format(context, id_comment))
		return redirect(url_for('postings.posts'))
	edit = db.select("SELECT * FROM comments WHERE idComment = '{0}'".format(id_comment,))
	return render_template('edit_comment.html', edit = edit)
	



