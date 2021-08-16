from flask import render_template, url_for, redirect, request, session, Blueprint, abort
from flaskblog import db
import re, math, base64, json

posts_ajax = Blueprint('posts_ajax', __name__)


def checker( function ):
	def wrapper( **kwargs ):
		if 'loggedin' not in session:
			return redirect( url_for( 'users.login' ) )
		return function( **kwargs )

	wrapper.__name__ = function.__name__
	return wrapper

	
@checker
@posts_ajax.route('/edit/<id_comment>', methods = ['POST'])
def edit(id_comment):
	
	errors = {}
	values = {}
	data = json.loads( request.get_data().decode('utf-8') )
	
	if not data:
		return base64.b64encode( json.dumps( { "error":2, "errors": "O eroare a avut loc in zona postarilor trimise." } ) )
	
	if id_comment is None or not isinstance( id_comment, str ): 
		return base64.b64encode( json.dumps( { "error": 2, "message": "O eroare a avut loc in zona de date necesare!" } ).encode('utf8') )
	
	if 'context' in data:
		db.select("SELECT * FROM comments WHERE idComment = '{0}'".format(id_comment,))
		if re.match( '^[a-zA-Z0-9\s@#?!$*%.,()\[\]\{\}" *"-+]+$', data['context'] ):
			values['context'] = data['context'].strip()
		else:
			errors['context'] = "Campul 'New comment context' contine caractere interzise."
	if data['context'] == "":
		errors['context'] = "Campul 'New comment context' nu a fost completat. Va rugam sa introduceti date in acest camp."
	
	if 'idComment' in data:
		if re.match( '^[0-9]+$', data['idComment'] ):
			values['idComment'] = data['idComment']
		else:
			errors['idComment'] = "O eroare a avut loc in zona datelor trimise."
	else:
		errors['idComment'] = "O eroare a avut loc in zona datelor trimise."
	if len( errors.keys() ) > 0:
		return base64.b64encode( json.dumps( { "error":2, "fields" : errors } ).encode('utf8') )

	db.update("UPDATE comments SET context = '{0}' WHERE idComment = '{1}' AND statusComment = 1".format(values['context'], id_comment))
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
	

