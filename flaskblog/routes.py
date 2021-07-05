from flask import render_template, url_for, redirect, request, session
from flaskblog import app, db, bcrypt
# from flaskblog.forms import RegistrationForm, LoginForm
import MySQLdb.cursors
import re


# @app.route("/")
# @app.route("/home", methods=['GET', 'POST'])
# def home():
#     if request.method == 'POST':
#         # user_id = request.form['username']
#         # email = request.form['email']
#         title = request.form['title']
#         content = request.form['content']
#         # date_posted = request.form['date_posted']
#         cur = db.connection.cursor()
#         cur.execute("INSERT INTO posts (title, content) VALUES (%s, %s)", (title, content))
#         db.connection.commit()
#         cur.close()
	  
#     return render_template('home.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
	if request.method == 'POST':
		title = request.form['title']
		content = request.form['content']
		user_id = request.form['user_id']
		cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
		cur.execute("INSERT INTO posts (title, content, user_id) VALUES (%s, %s, %s)", (title, content, user_id))
		db.connection.commit()
		return redirect (url_for('posts'))
	if 'loggedin' in session:
		return render_template('home.html', username=session['username'], user_id=session['id'])
	return redirect(url_for('login'))

@app.route('/posts', methods=['GET', 'POST'])
def posts():
	if 'loggedin' in session:
		cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
		cur.execute(f"SELECT * FROM posts LEFT JOIN users ON users.id = posts.user_id WHERE user_id = {session['id']} ORDER BY posts.date_posted DESC")
		post_details = cur.fetchall()
	return render_template('posts.html', post_details=post_details)


@app.route('/login', methods=['GET', 'POST'])
def login():
	msg = ''
	if 'loggedin' in session:
		return redirect(url_for('home'))
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
		cur.execute("SELECT * FROM users WHERE username = '{0}'".format(username))
		account = cur.fetchone()
		cur.close()
		if account:
			if bcrypt.check_password_hash(account['password'], password):
				session['loggedin'] = True
				session['id'] = account['id']
				session['username'] = account['username']
				return redirect(url_for('home'))
			else:
				msg = 'An error has occured !'
		else:
			msg = 'Incorrect username/password!'
	return render_template('index.html', msg=msg)


@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))
   

@app.route('/register', methods=['GET', 'POST'])
def register():
	msg = ''
	if 'loggedin' in session:
		return redirect(url_for('home'))
	if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form:
		username = request.form['username']
		email = request.form['email']
		password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
		cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists!'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address!'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers!'
		elif not username or not password or not email:
			msg = 'Please fill out the form!'
		else:
			cursor.execute("INSERT INTO users (username,email,password) VALUES ('{0}', '{1}', '{2}')".format(username, email, password))
			db.connection.commit()
			msg = 'You have successfully registered!'
			cursor.close()
			return redirect(url_for('login'))
	elif request.method == 'POST':
		msg = 'Please fill out the form!'
	return render_template('register.html', msg=msg)
		

@app.route('/profile')
def profile():
	if 'loggedin' in session:
		cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
		account = cursor.fetchone()
		cursor.close()
		return render_template('profile.html', account=account)
	return redirect(url_for('login'))



@app.route('/delete/<id_post>', methods=['GET', 'POST'])
def delete(id_post):
	cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
	cur.execute(f'DELETE FROM posts WHERE id = {id_post}')
	db.connection.commit()
	return redirect (url_for('posts'))

@app.route('/update/<id_post>', methods=['GET', 'POST'])
def update(id_post):
	if request.method == "POST":
		title = request.form['title']
		content = request.form['content']
		cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
		cur.execute(f'UPDATE posts SET title = %s, content = %s WHERE id = %s', (title, content, id_post))
		db.connection.commit()
		return redirect(url_for('posts'))
	cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT * FROM posts WHERE id = %s', (id_post,))
	post = cursor.fetchone()
	return render_template('update.html', post = post)