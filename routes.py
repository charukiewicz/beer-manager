#!/usr/bin/env python
import os
import hashlib
from flask import Flask, request, make_response, abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask import jsonify
from sqlalchemy import desc, asc, Table, insert

# Author: Christian Charukiewicz
# Email: c.charukiewicz@gmail.com

app = Flask(__name__)
db = SQLAlchemy(app)

# MySQL configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/beer_manager'

# Database Models
class User(db.Model):
	__tablename__ 		= 'users'
	id 					= db.Column(db.Integer, primary_key = True)
	username 			= db.Column(db.String(128))
	email 				= db.Column(db.String(128))
	password 			= db.Column(db.String(128))
	salt 				= db.Column(db.String(128))
	beer_added_today 	= db.Column(db.Integer)

class Beer(db.Model):
	__tablename__ 		= 'beers'
	id 					= db.Column(db.Integer, primary_key = True)
	name 				= db.Column(db.String(128))
	ibu 				= db.Column(db.Integer)
	calories 			= db.Column(db.Integer)
	abv 				= db.Column(db.Float(6))
	style 				= db.Column(db.String(128))
	brewery_location 	= db.Column(db.String(128))
	glass_type 			= db.Column(db.Integer)

class Glass(db.Model):
	__tablename__ 		= 'glasses'
	id 					= db.Column(db.Integer, primary_key = True)
	name 				= db.Column(db.String(128))

class Review(db.Model):
	__tablename__ 		= 'reviews'
	id 					= db.Column(db.Integer, primary_key = True)
	created 			= db.Column(db.DateTime)
	user_id 			= db.Column(db.Integer)
	beer_id 			= db.Column(db.Integer)
	aroma 				= db.Column(db.Float(6))
	appearance 			= db.Column(db.Float(6))
	taste 				= db.Column(db.Float(6))
	palate 				= db.Column(db.Float(6))
	bottle_style 		= db.Column(db.Float(6))
	overall 			= db.Column(db.Float(6))
	posted_this_week 	= db.Column(db.Integer)

class Favorite(db.Model):
	__tablename__ 		= 'favorites'
	id 					= db.Column(db.Integer, primary_key = True)
	user_id 			= db.Column(db.Integer)
	beer_id 			= db.Column(db.Integer)

# End of Database Models

# Make the 500 error more relevant to our application
@app.errorhandler(500)
def missing_data(error):
	return make_response(jsonify({'error': 'Missing or Invalid Input Data'}), 500)

# Begin API route paths
@app.route('/')
def index():
	dbsession 	= db.session()

	users 		= dbsession.query(User.id).count()
	beers 		= dbsession.query(Beer.id).count()
	reviews 	= dbsession.query(Review.id).count()
	glasses 	= dbsession.query(Glass.id).count()
	favorites 	= dbsession.query(Favorite.id).count()

	d = {
		"total_users":	 		users,
		"total_beers":	 		beers,
		"total_reviews": 		reviews,
		"total_beer_glasses": 	glasses,
		"total_favorites": 		favorites
	}

	return jsonify(statistics = d)

	dbsession.commit()

@app.route('/users/', methods=['GET', 'POST'])
def users():
	if request.method == 'GET':

		sort = request.args.get('sort', 'asc')
		limit = request.args.get('limit')

		if sort == 'desc':
			results = User.query.order_by(desc('users.username')).limit(limit).all()
		elif sort == 'asc':
			results = User.query.order_by(asc('users.username')).limit(limit).all()

		json_results = []
		for result in results:
			d = {	'id': 				result.id,
					'username': 		result.username,
					'email': 			result.email,
					'beer_added_today': result.beer_added_today }
			json_results.append(d)

		return jsonify(users=json_results)

	if request.method == 'POST':

		username = request.get_json().get('username')
		email = request.get_json().get('email')
		password = request.get_json().get('password')

		# Create password salt and hash salt+password
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
		dbsession.commit()

		success = "User Created"
		return jsonify(response = success)


@app.route('/users/<int:uid>/', methods=['GET', 'PUT', 'DELETE'])
def user(uid):
	if request.method == 'GET':

		result = User.query.filter_by(id = uid).first()

		reviews_posted = []
		if result != None:
			review_results = Review.query.filter_by(user_id = uid).all()
			for review_result in review_results:
				r = {
					'review_id': 	review_result.id,
					'created': 		review_result.created,
					'beer_id': 		review_result.beer_id,
					'aroma': 		review_result.aroma,
					'appearance': 	review_result.appearance,
					'taste': 		review_result.taste,
					'palate': 		review_result.palate,
					'bottle_style': review_result.bottle_style,
					'overall': 		review_result.overall }
				reviews_posted.append(r)

		favorites = []
		if result != None:
			favorite_results = Review.query.filter_by(user_id = uid).all()
			for favorite_result in favorite_results:
				r = {
					'favorite_id': 	favorite_result.id,
					'beer_id': 		favorite_result.beer_id}
				favorites.append(r)

		d = {	'id': 				result.id,
				'username': 		result.username,
				'email': 			result.email,
				'beer_added_today': result.beer_added_today,
				'password': 		result.password,
				'salt': 			result.salt,
				'reviews_posted': 	reviews_posted,
				'favorite_beers': 	favorites }

		return jsonify(user = d)

	if request.method == 'PUT':

		username = request.get_json().get('username')
		email = request.get_json().get('email')
		password = request.get_json().get('password')

		if password != None:
			salt = os.urandom(16)
			salt = str(salt).encode('utf-8')
			password = password.encode('utf-8')
			passhash = hashlib.sha256()
			passhash.update(salt+password)

		dbsession = db.session()

		query = dbsession.query(User)
		query = query.filter(User.id == uid)
		record = query.one()
		if username != None:
			record.username = username
		if email != None:
			record.email = email
		if password != None:
			record.password = passhash.hexdigest()
			record.salt = salt

		dbsession.commit()

		success = "User Updated"
		return jsonify(response = success)

	if request.method == 'DELETE':

		dbsession = db.session()
		dbsession.query(User).filter_by(id = uid).delete()
		dbsession.commit()

		success = "User Deleted"
		return jsonify(response = success)

@app.route('/beers/', methods=['GET', 'POST'])
def beers():
	if request.method == 'GET':

		sort = request.args.get('sort', 'asc')
		limit = request.args.get('limit')
		stat = request.args.get('stat')

		if stat != None:
			if sort == 'desc':
				results = Beer.query.order_by(desc('beers.' + stat)).limit(limit).all()
			elif sort == 'asc':
				results = Beer.query.order_by(asc('beers.' + stat)).limit(limit).all()
		else:
			results = Beer.query.limit(limit).all()

		json_results = []
		for result in results:
			d = {	'id': 				result.id,
					'name': 			result.name,
					'ibu': 				result.ibu,
					'calories': 		result.calories,
					'abv': 				result.abv,
					'style': 			result.style,
					'brewery_location': result.brewery_location,
					'glass_type': 		result.glass_type }
			json_results.append(d)

		return jsonify(beers=json_results)

	if request.method == 'POST':

		name = 				request.get_json().get('name')
		ibu = 				request.get_json().get('ibu')
		calories = 			request.get_json().get('calories')
		abv = 				request.get_json().get('abv')
		style = 			request.get_json().get('style')
		brewery_location = 	request.get_json().get('brewery_location')
		glass_type = 		request.get_json().get('glass_type')

		user_id = request.get_json().get('user_id')

		if name == "" or name == None:
			abort(500)
		if ibu == "" or ibu == None:
			abort(500)
		if calories == "" or calories == None:
			abort(500)
		if abv == "" or abv == None:
			abort(500)
		if style == "" or style == None:
			abort(500)
		if brewery_location == "" or brewery_location == None:
			abort(500)
		if glass_type == "" or glass_type == None:
			abort(500)

		result = User.query.filter_by(id = user_id).first()

		if result.beer_added_today == 1:
			error = "This user has already added a beer today"
			return jsonify(response = error)

		glasscheck = Glass.query.filter_by(id = glass_type).first()

		if glasscheck == None:
			error = "Invalid beer glass type"
			return jsonify(response = error)

		dbsession = db.session()

		query = dbsession.query(User)
		query = query.filter(User.id == user_id)
		record = query.one()
		record.beer_added_today = 1

		dbsession.commit()

		newBeer = Beer(
			name = name,
			ibu = ibu,
			calories = calories,
			abv = abv,
			style = style,
			brewery_location = brewery_location,
			glass_type = glass_type)

		dbsession = db.session()
		dbsession.add(newBeer)
		dbsession.commit()

		success = "Beer Created"
		return jsonify(response = success)

@app.route('/beers/<int:beer_id>/', methods=['GET', 'DELETE'])
def beer(beer_id):
	if request.method == 'GET':

		result = Beer.query.filter_by(id = beer_id).first()

		# Retrieve all reviews associated with the specified beer
		all_results = []
		average_overall = []
		if result != None:
			review_results = Review.query.filter_by(beer_id = beer_id).all()
			for review_result in review_results:
				r = {
					'review_id': 	review_result.id,
					'created': 		review_result.created,
					'user_id': 		review_result.user_id,
					'beer_id': 		review_result.beer_id,
					'aroma': 		review_result.aroma,
					'appearance': 	review_result.appearance,
					'taste': 		review_result.taste,
					'palate': 		review_result.palate,
					'bottle_style': review_result.bottle_style,
					'overall': 		review_result.overall}
				average_overall.append(float(review_result.overall))
				all_results.append(r)

		# Average of overall ratings for all reviews
		overall_rating = sum(average_overall) / float(len(average_overall))

		d = {	'id': 				result.id,
				'name': 			result.name,
				'ibu': 				result.ibu,
				'calories': 		result.calories,
				'abv': 				result.abv,
				'style': 			result.style,
				'brewery_location': result.brewery_location,
				'glass_type': 		result.glass_type,
				'reviews': 			all_results,
				'overall_rating': 	overall_rating }

		return jsonify(beer = d)

	if request.method == 'DELETE':

		dbsession = db.session()
		dbsession.query(Beer).filter_by(id = beer_id).delete()
		dbsession.query(Review).filter_by(beer_id = beer_id).delete()
		dbsession.query(Favorite).filter_by(beer_id = beer_id).delete()
		dbsession.commit()

		success = "Beer Deleted"
		return jsonify(response = success)

@app.route('/glasses/', methods=['GET', 'POST'])
def glasses():
	if request.method == 'GET':

		sort = request.args.get('sort', 'asc')
		limit = request.args.get('limit')

		if sort == 'desc':
			results = Glass.query.order_by(desc('glasses.name')).limit(limit).all()
		elif sort == 'asc':
			results = Glass.query.order_by(asc('glasses.name')).limit(limit).all()

		json_results = []
		for result in results:
			d = {	'id': result.id,
					'name': result.name }
			json_results.append(d)

		return jsonify(glasses=json_results)

	if request.method == 'POST':

		name = request.get_json().get('name')

		if name == "" or name == None:
			abort(500)

		newGlass = Glass(
			name = name)

		dbsession = db.session()
		dbsession.add(newGlass)
		dbsession.commit()

		success = "Beer Glass Created"
		return jsonify(response = success)

@app.route('/glasses/<int:glass_id>/', methods=['DELETE'])
def glass(glass_id):
	if request.method == 'DELETE':

		dbsession = db.session()
		dbsession.query(Glass).filter_by(id = glass_id).delete()
		dbsession.commit()

		success = "Beer Glass Deleted"
		return jsonify(response = success)

@app.route('/reviews/', methods=['GET', 'POST'])
def reviews():
	if request.method == 'GET':

		sort = request.args.get('sort', 'asc')
		limit = request.args.get('limit')
		stat = request.args.get('stat')

		if stat != None:
			if sort == 'desc':
				results = Review.query.order_by(desc('reviews.' + stat)).limit(limit).all()
			elif sort == 'asc':
				results = Review.query.order_by(asc('reviews.' + stat)).limit(limit).all()
		else:
			results = Review.query.limit(limit).all()

		json_results = []
		for result in results:
			d = {	'id': 			result.id,
					'created': 		result.created,
					'user_id': 		result.user_id,
					'beer_id': 		result.beer_id,
					'aroma': 		result.aroma,
					'appearance': 	result.appearance,
					'taste': 		result.taste,
					'palate': 		result.palate,
					'bottle_style': result.bottle_style,
					'overall': 		result.overall }
			json_results.append(d)

		return jsonify(review=json_results)

	if request.method == 'POST':

		user_id = 		request.get_json().get('user_id')
		beer_id = 		request.get_json().get('beer_id')
		aroma = 		request.get_json().get('aroma')
		appearance = 	request.get_json().get('appearance')
		taste = 		request.get_json().get('taste')
		palate = 		request.get_json().get('palate')
		bottle_style = 	request.get_json().get('bottle_style')

		if user_id == "" or user_id == None:
			abort(500)
		if beer_id == "" or beer_id == None:
			abort(500)
		if aroma == "" or aroma == None:
			abort(500)
		if appearance == "" or appearance == None:
			abort(500)
		if taste == "" or taste == None:
			abort(500)
		if palate == "" or palate == None:
			abort(500)
		if bottle_style == "" or bottle_style == None:
			abort(500)

		errors = []
		error_flag = False
		if float(aroma) < 0 or float(aroma) > 5:
			error = { 'error' : "Aroma must be between 0.0 and 5.0" }
			errors.append(error)
		if float(appearance) < 0 or float(appearance) > 5:
			error = { 'error' : "Appearance must be between 0.0 and 5.0" }
			errors.append(error)
		if float(taste) < 0 or float(taste) > 10:
			error = { 'error' : "Taste must be between 0.0 and 10.0" }
			errors.append(error)
		if float(palate) < 0 or float(palate) > 5:
			error = { 'error' : "Palate must be between 0.0 and 5.0" }
			errors.append(error)
		if float(bottle_style) < 0 or float(bottle_style) > 5:
			error = { 'error' : "Bottle Style must be between 0.0 and 5.0" }
			errors.append(error)
		if len(errors) > 0:
			return jsonify(response = errors)

		usercheck = User.query.filter_by(id = user_id).first()

		if usercheck == None:
			error = "The user does not exist"
			return jsonify(response = error)

		beercheck = Beer.query.filter_by(id = beer_id).first()

		if beercheck == None:
			error = "The beer does not exist"
			return jsonify(response = error)

		weeklycheck = Review.query.filter_by(user_id = user_id, beer_id = beer_id, posted_this_week = 1).first()

		if weeklycheck != None:
			error = "This user has already reviewed this beer this week"
			return jsonify(response = error)

		ratings = [float(aroma), float(appearance), float(taste), float(palate), float(bottle_style)]
		overall = sum(ratings) / float(len(ratings))

		newReview = Review(
			user_id = user_id,
			beer_id = beer_id,
			aroma = aroma,
			appearance = appearance,
			taste = taste,
			palate = palate,
			bottle_style = bottle_style,
			overall = overall,
			posted_this_week = 1)

		dbsession = db.session()
		dbsession.add(newReview)
		dbsession.commit()

		success = "Review Created"
		return jsonify(response = success)

@app.route('/reviews/<int:review_id>/', methods=['GET', 'DELETE'])
def review(review_id):
	if request.method == 'GET':

		result = Review.query.filter_by(id = review_id).first()

		d = {	'id': 			result.id,
				'created': 		result.created,
				'user_id': 		result.user_id,
				'beer_id': 		result.beer_id,
				'aroma': 		result.aroma,
				'appearance': 	result.appearance,
				'taste': 		result.taste,
				'palate': 		result.palate,
				'bottle_style': result.bottle_style,
				'overall': 		result.overall }

		return jsonify(review = d)

	if request.method == 'DELETE':

		dbsession = db.session()
		dbsession.query(Review).filter_by(id = review_id).delete()
		dbsession.commit()

		success = "Review Deleted"
		return jsonify(response = success)


@app.route('/favorites/', methods=['POST'])
def favorites():
	if request.method == 'POST':

		user_id = request.get_json().get('user_id')
		beer_id = request.get_json().get('beer_id')

		if user_id == "" or user_id == None:
			abort(500)
		if beer_id == "" or beer_id == None:
			abort(500)

		usercheck = User.query.filter_by(id = user_id).first()

		if usercheck == None:
			error = "The user does not exist"
			return jsonify(response = error)

		beercheck = Beer.query.filter_by(id = beer_id).first()

		if beercheck == None:
			error = "The beer does not exist"
			return jsonify(response = error)

		newFavorite = Favorite(
			user_id = user_id,
			beer_id = beer_id)

		dbsession = db.session()
		dbsession.add(newFavorite)
		dbsession.commit()

		success = "Favorite Created"
		return jsonify(response = success)

@app.route('/favorites/<int:favorite_id>/', methods=['DELETE'])
def favorite(favorite_id):
	if request.method == 'DELETE':

		dbsession = db.session()
		dbsession.query(Favorite).filter_by(id = favorite_id).delete()
		dbsession.commit()

		success = "Favorite Deleted"
		return jsonify(response = success)

@app.route('/cronjobs/', methods=['GET'])
def cronjobs():
	if request.method == 'GET':

		job_type = request.args.get('jobtype')

		if job_type == "daily":
			dbsession = db.session()

			query = dbsession.query(User)
			records = query.all()
			for record in records:
				record.beer_added_today = 0

			dbsession.commit()

			success = "Daily records cleared"
			return jsonify(response = success)

		if job_type == "weekly":
			dbsession = db.session()

			query = dbsession.query(Review)
			records = query.all()
			for record in records:
				record.posted_this_week = 0
			
			dbsession.commit()

			success = "Weekly records cleared"
			return jsonify(response = success)


if __name__ == '__main__':
  app.run(debug=False)