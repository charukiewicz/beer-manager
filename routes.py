from flask import Flask, request, make_response, abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask import jsonify
from sqlalchemy import desc, asc, Table, insert
#import models

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

		if username == "" or username == None:
			abort(500)

		userdata = [username, email, password]

		users = Table('users', meta)

		ins = User.insert().values(username = username, email = email, password = password)

		conn = engine.connect

		conn.execute(ins)

		success = "User Created"
		return jsonify(response = success)


if __name__ == '__main__':
  app.run(debug=True)