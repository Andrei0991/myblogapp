from flask import render_template, url_for, redirect, request, session, Blueprint
from flaskblog import db
import re


main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home', methods=['GET', 'POST'])
def home():
	errors = {}
	values = {}
	if 'loggedin' in session:
		if request.method == 'POST':
			idUser = request.form['idUser']
			title = request.form['title']
			content = request.form['content']
			if len(title) > 0:
				values['title'] = request.form['title']
			else:
				errors['title'] = "Va rugam completati campul 'Title'."
			if re.match(r'^[a-zA-Z0-9\+\:\@\#\$\%\&\*\{\}\]\/\.\-\_\,\(\)\?\!\"\s]+$', request.form['content']):
				values['content'] = request.form['content']
			else:
				errors['content'] = "Va rugam completati campul 'Content'."
			if len(errors) == 0:
				db.insert("INSERT INTO posts (idUser, title, content) VALUES ('{0}', '{1}', '{2}')".format(idUser, title, content))
				return redirect (url_for('postings.posts'))
		return render_template('home.html', username = session['username'], idUser = session['id'], errors = errors, form = request.form if request.method == 'POST' else None)
	return redirect(url_for('users.login'))

			