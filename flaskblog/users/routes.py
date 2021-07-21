from flask import render_template, url_for, redirect, request, session, Blueprint
from flaskblog import db, bcrypt
import re

users = Blueprint('users', __name__)


@users.route('/login', methods=['GET', 'POST'])
def login():
	msg = ''
	if 'loggedin' in session:
		return redirect(url_for('main.home'))
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		# cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
		account = db.select("SELECT * FROM users WHERE username = '{0}'".format(username))
		# account = cur.fetchone()
		# cur.close()
		if account:
			if bcrypt.check_password_hash(account['password'], password):
				session['loggedin'] = True
				session['id'] = account['idUser']
				session['username'] = account['username']
				return redirect(url_for('main.home'))
			else:
				msg = 'An error has occured !'
		else:
			msg = 'Incorrect username/password!'
	return render_template('index.html', msg=msg)


@users.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('users.login'))
   

@users.route('/register', methods=['GET', 'POST'])
def register():
	msg = ''
	if 'loggedin' in session:
		return redirect(url_for('main.home'))
	if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form:
		username = request.form['username']
		email = request.form['email']
		password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
		# cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
		account = db.select("SELECT * FROM users WHERE username = '{0}'".format(username))
		# account = cursor.fetchone()
		if account:
			msg = 'Account already exists!'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address!'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers!'
		elif not username or not password or not email:
			msg = 'Please fill out the form!'
		else:
			db.insert("INSERT INTO users (username,email,password) VALUES ('{0}', '{1}', '{2}')".format(username, email, password))
			# db.connection.commit()
			msg = 'You have successfully registered!'
			# cursor.close()
			return redirect(url_for('users.login'))
	elif request.method == 'POST':
		msg = 'Please fill out the form!'
	return render_template('register.html', msg=msg)
		

@users.route('/profile')
def profile():
	if 'loggedin' in session:
		# cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
		account = db.select("SELECT * FROM users WHERE idUser = '{0}'".format(session['id']))
		# account = cursor.fetchone()
		# cursor.close()
		return render_template('profile.html', account = account)
	return redirect(url_for('users.login'))