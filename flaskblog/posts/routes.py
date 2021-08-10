from flask import render_template, url_for, redirect, request, session, Blueprint, abort
from flaskblog import db
import re, math, base64, json

postings = Blueprint('postings', __name__)

def checker( function ):
	def wrapper( **kwargs ):
		if 'loggedin' not in session:
			return redirect( url_for( 'users.login' ) )
		return function( **kwargs )

	wrapper.__name__ = function.__name__
	return wrapper


@checker
@postings.route('/posts', defaults={'page': 1}, methods=['GET', 'POST'])
@postings.route('/posts/page/<int:page>')
def posts(page):
	db.query("""SET session sql_mode='NO_ENGINE_SUBSTITUTION'""")
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
		post_IDS.append( str( post['idPost'] ) )
		
	comments = db.select( """
							SELECT * 
							FROM comments 
							LEFT JOIN users ON users.idUser = comments.idUser
							WHERE statusComment = 1  
							AND statusUser = 1
							AND idPost IN ( {0} )
							ORDER BY comments.dateComment DESC
							""".format( ", ".join( post_IDS ) ), False )
	
	commentsAdded = {}
	if post_details:
		for post in post_details:
			commentsAdded[post['idPost']] = []
		if comments:
			for comment in comments:
				commentsAdded[comment['idPost']].append(comment)
	return render_template('posts.html', post_details = post_details, username = session['username'], commentsAdded = commentsAdded, next = next, prev = prev, pages = pages)


@checker
@postings.route('/delete/<id_post>', methods=['GET', 'POST'])
def delete(id_post):
	if id_post is None or not isinstance( id_post, str ): 
		return base64.b64encode( json.dumps( { "error": 2, "message": "A avut loc o eroare, va rugam incercati din nou !" } ).encode('utf8') )

	db.delete(f'DELETE FROM posts WHERE idPost = {id_post} AND statusPost = 1')
	return base64.b64encode( json.dumps( { "error":0, "message":"Datele postului au fost modificate cu succes !" } ).encode('utf8') )


@checker
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
	 

@checker
@postings.route('/add-comment', methods = [ 'POST' ] )
def comments():

	errors = {}
	values = {}
	data = json.loads( request.get_data().decode('utf-8') )
	
	if not data:
		return base64.b64encode( json.dumps( { "error":2, "errors": "O eroare a avut loc in zona postarilor trimise." } ) )

	if 'context' in data:
		if re.match( '^[a-zA-Z0-9\s@#?!$*%.,()\[\]\{\}" *"]+$', data['context'] ):
			values['context'] = data['context'].strip()
		else:
			errors['context'] = "Campul 'Comments' contine caractere interzise."
	if data['context'] == "":
		errors['context'] = "Campul 'Comments' nu a fost completat. Va rugam sa introduceti date in acest camp."
	
	if 'idPost' in data:
		if re.match( '^[0-9]+$', data['idPost'] ):
			values['idPost'] = data['idPost']
		else:
			errors['idPost'] = "O eroare a avut loc in zona datelor trimise."
	else:
		errors['idPost'] = "O eroare a avut loc in zona datelor trimise."
	
	if len( errors.keys() ) > 0:
		return base64.b64encode( json.dumps( { "error":2, "fields" : errors } ).encode('utf8') )

	db.insert("INSERT INTO comments (idPost, idUser, context) VALUES ('{0}', '{1}', '{2}')".format( values['idPost'], session['id'], values['context'] ))
	return base64.b64encode( json.dumps( { "error":0, "message":"Datele au fost salvate cu success." } ).encode('utf8') )



@checker
@postings.route('/deleteComments/<id_post>', methods=['GET', 'POST'])
def deleteComments( id_post ):
	if id_post is None or not isinstance( id_post, str ): 
		return base64.b64encode( json.dumps( { "error": 2, "message": "O eroare a avut loc in zona de date necesare!" } ).encode('utf8') )

	db.delete(f'DELETE FROM comments WHERE idComment = {id_post} AND statusComment = 1')
	return base64.b64encode( json.dumps( { "error":0, "message":"Datele au fost modificate cu success!" } ).encode('utf8') )
		
	
@checker
@postings.route('/edit/<id_comment>', methods = ['GET', 'POST'])
def edit(id_comment):
	
	errors = {}
	values = {}
	data = json.loads( request.get_data().decode('utf-8') )
	print(type(data))
	print(data)
	
	if not data:
		return base64.b64encode( json.dumps( { "error":2, "errors": "O eroare a avut loc in zona postarilor trimise." } ) )
	
	if id_comment is None or not isinstance( id_comment, str ): 
		return base64.b64encode( json.dumps( { "error": 2, "message": "O eroare a avut loc in zona de date necesare!" } ).encode('utf8') )
	
	if 'context' in data:
		db.select("SELECT * FROM comments WHERE idComment = '{0}'".format(id_comment,))
		if re.match( '^[a-zA-Z0-9\s@#?!$*%.,()\[\]\{\}" *"]+$', data['context'] ):
			values['context'] = data['context'].strip()
		else:
			errors['context'] = "Campul 'Edit Comments' contine caractere interzise."
	if data['context'] == "":
		errors['context'] = "Campul 'Edit Comments' nu a fost completat. Va rugam sa introduceti date in acest camp."
	
	if 'idComment' in data:
		if re.match( '^[0-9]+$', data['idComment'] ):
			values['idComment'] = data['idComment']
		else:
			errors['idComment'] = "O eroare a avut loc in zona datelor trimise."
	else:
		errors['idComment'] = "O eroare a avut loc in zona datelor trimise."
	if len( errors.keys() ) > 0:
		return base64.b64encode( json.dumps( { "error":2, "fields" : errors } ).encode('utf8') )

	db.update("UPDATE comments SET context = '{0}' WHERE idComment = '{1}' AND statusComment = 1".format(context, id_comment))
	return base64.b64encode( json.dumps( { "error":0, "message":"Datele au fost modificate cu success!" } ).encode('utf8') )
	
	
	# if request.method == "POST":
	# 	context = request.form['context']
	# 	if not id_comment or not id_comment.isdigit():
	# 			return abort(404)
	# 	user = db.select("SELECT * FROM comments WHERE idComment = '{0}'".format(id_comment,))
	# 	if user and user['idUser'] is not None:
	# 		if session['id'] != user['idUser']:
	# 			return abort(404)
	# 	if 'context' in request.form:
	# 		if re.match( '^[a-zA-Z0-9\+\:\@\#\$\%\&\*\{\}\]\/\.\-\_\,\(\)\?\!\"\s]+$', request.form['context'] ):
	# 			values['context'] = request.form['context']
	# 		else:
	# 			errors['context'] = "Campul 'Context' contine caractere interzise."
	# 	else:
	# 		errors['context'] = "Context OK"
	# 	if len(errors) == 0:				
	# 		db.update("UPDATE comments SET context = '{0}' WHERE idComment = '{1}' AND statusComment = 1".format(context, id_comment))
	# 		return redirect(url_for('postings.posts'))
	# edit = db.select("SELECT * FROM comments WHERE idComment = '{0}'".format(id_comment,))
	# return render_template('edit_comment.html', edit = edit, errors = errors)
	

