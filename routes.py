from flask import Flask, request, make_response, abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask import jsonify
from sqlalchemy import desc, asc, Table, insert
import os
import hashlib

app = Flask(__name__)
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/beer_manager'

@app.route('/')
def index():
	return "Hello, World!"

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(128))
	email = db.Column(db.String(128))
	password = db.Column(db.String(128))
	salt = db.Column(db.String(128))
	beer_added_today = db.Column(db.Integer)

@app.errorhandler(500)
def missing_data(error):
	return make_response(jsonify({'error': 'Missing Input Data'}), 500)

@app.route('/users/', methods=['GET', 'POST'])
def users():
	if request.method == 'GET':

		sort = request.args.get('sort', 'asc')
		limit = request.args.get('limit', 100)

		if sort == 'desc':
			results = User.query.order_by(desc('users.username')).limit(limit).all()
		elif sort == 'asc':
			results = User.query.order_by(asc('users.username')).limit(limit).all()

		#results = User.query.from_statement("SELECT * FROM `users`")

		json_results = []
		for result in results:
			d = {	'id': result.id,
					'username': result.username,
					'email': result.email,
					'beer_added_today': result.beer_added_today }
			json_results.append(d)

		return jsonify(items=json_results)

	if request.method == 'POST':

		username = request.get_json().get('username')
		email = request.get_json().get('email')
		password = request.get_json().get('password')

		salt = os.urandom(16)
		salt = str(salt).encode('utf-8')
		password = password.encode('utf-8')
		passhash = hashlib.sha256()
		passhash.update(salt+password)


		if username == "" or username == None:
			abort(500)
		if email == "" or email == None:
			abort(500)
		if password == "" or password == None:
			abort(500)

		newUser = User(
			username = username,
			email = email,
			password = passhash.hexdigest(),
			salt = salt,
			beer_added_today = 0)

		dbsession = db.session()
		dbsession.add(newUser)
		# dbsession.merge(newUser)
		# dbsession.query(User).filter_by(id = uid).delete()
		dbsession.commit()

		success = "User Created"
		return jsonify(response = success)


@app.route('/users/<int:uid>/', methods=['GET', 'PUT', 'DELETE'])
def user(uid):
	if request.method == 'GET':

		result = User.query.filter_by(id = uid).first()

		d = {	'id': result.id,
				'username': result.username,
				'email': result.email,
				'beer_added_today': result.beer_added_today,
				'password' : result.password,
				'salt' : result.salt }

		return jsonify(user = d)




if __name__ == '__main__':
  app.run(debug=True)