Beer Manager API - User Manual
============
Author: Christian Charukiewicz - Email: c.charukiewicz@gmail.com


Software Used:
* Python 3.3.x / 3.4.x
* Flask 0.10.1
* Virtualenv 1.11.6
* SQLAlchemy 0.9.7
* Flask-SQLAlchemcy 2.0
* PyMySQL3 0.5
* MySQL 5.6.17


Features:


This Beer Manager API includes a number of features that make a simple yet robust application backend written in Python and utilizing the Flask web application framework.  Features include:
* User account creation, deletion and updating
* SHA256 password encryption with randomly generated 16 byte salt strings
* Beer creation, deletion, and retrieval
* Access to all reviews associated with a single beer
* Access to all reviews posted by a specific user
* Beer glass creation and deletion
* Beer review creation and deletion
* Dynamically generated favorites lists for each user
* Favorite addition and removal for each user
* A maximum of one beer creation per user per day
* A maximum of one beer review per beer per user per week
* Sorting of data retrieved via GET requests
* Human readable and descriptive success/error messages
* JSON based data entry and retrieval

________________


Installation Instructions:


Preliminary requirements:
* Python virtualenv (on Ubuntu: sudo apt-get install python-virtualenv)
* MySQL Server
* routes.py (provided with this manual)


Execute the following commands in the terminal (or perform the system equivalent):


    cd /path/to/beer_manager
    virtualenv venv
    . venv/bin/activate
    pip install flask
    pip install flask-sqlalachemy
    pip install pymysql3


At this point add the import beer_manager.sql into the MySQL database, and add the MySQL user details to routes.py, to the line starting with “app.config['SQLALCHEMY_DATABASE_URI']”


Add the following two cronjobs to the system crontab (sudo -e crontab):
* @daily curl -i -X GET http://localhost:5000/cronjobs/?jobtype=daily
* @weekly curl -i -X GET http://localhost:5000/cronjobs/?jobtype=weekly


Installation is complete.  Return to the beer_manager directory and ensure that the Python virtual environment is active (. venv/bin/activate).  Start the server with:


    python routes.py


It is now possible to connect to the API through localhost using port 5000.  GET requests can be sent via any internet browser using http://localhost:5000/, and other types of requests can be sent using curl on a Linux based system.  Full usage with provided examples is covered in the rest of this manual.

________________


API Overview:


The Beer Manager API accepts the HTTP verbs POST, PUT, GET, and DELETE.  The available paths are shown in the table below.  For detailed usage instructions and expected input parameters, view the guide on the subsequent pages.




|                  | POST              | PUT         | GET                       | DELETE          |
|------------------|-------------------|-------------|---------------------------|-----------------|
| /                | (error)           | (error)     | view statistics           | (error)         |
| /users/          | create new user   | (error)     | view all users            | (error)         |
| /users/<id>/     | (error)           | update user | view user info/favorites  | delete user     |
| /beers/          | create new beer   | (error)     | get beer list             | (error)         |
| /beers/<id>/     | (error)           | (error)     | view beer specs/ratings   | delete beer     |
| /glasses/        | create new glass  | (error)     | view all glasses          | (error)         |
| /glasses/<id>/   | (error)           | (error)     | (error)                   | delete glass    |
| /reviews/        | create new review | (error)     | view all reviews          | (error)         |
| /reviews/<id>/   | (error)           | (error)     | view review               | delete review   |
| /favorites/      | add new favorite  | (error)     | (error)                   | (error)         |
| /favorites/<id>/ | (error)           | (error)     | (error)                   | delete favorite |
| /cronjobs/       | (error)           | (error)     | reset daily/weekly limits | (error)         |
	

________________


API Paths:


**/:**
Provides database statistics.  Accepted HTTP verb: GET
        
GET:
Displays the number of users, beers, reviews, beer glasses, and favorited beers present in the database


**/users/:**
Provides access to users in the database.  Accepted HTTP verbs: GET, POST.


GET:
Displays users in the database


Parameters:
sort={asc,desc} - (optional) - sorts the results list alphabetically by username, can be either ascending or descending


limit=LIMIT - (optional) - limits the number of results to the integer passed in as the LIMIT variable


Example: 
http://localhost:5000/users/?sort=asc&limit=25


This will display the first 25 users in the database in ascending order.


POST:
Creates a new user.


Parameters:
username - (required)
email - (required)
password - (required)


POST parameters must be passed via JSON format.


Example:
curl -i -H "Content-Type: application/json" -X POST -d '{"username":"Jack","email":"asdf@asdf.com","password":"password123"}' http://localhost:5000/users/


This will create a new user named “Jack” with the specified account information.  A password salt will be created and prepended to the input password.  The salt+password string is then encrypted using SHA256.




________________


**/users/[id]/:**
Allows access to an individual user specified by <id> parameter in the path.  Accepted HTTP verbs: PUT, GET, DELETE.


PUT:
Updates the specified user.


Parameters:
username - (optional)
email - (optional)
password - (optional)


PUT parameters must be passed via JSON format.


Example:
curl -i -H "Content-Type: application/json" -X PUT -d '{"email":"asdf@asdf.com"}' http://localhost:5000/users/3/


This will update the email address of the user with user id 3 in the database.


GET:
Retrieves information about the specified user.


Parameters:
None.


Example:
http://localhost:5000/users/3/


DELETE:
Deletes the specified user from the database.


Parameters:
None.


Example:
curl -i -X DELETE http://localhost:5000/users/3/


________________


**/beers/:**
Provides access to beers in the database.  Accepted HTTP verbs: GET, POST.


GET:
Displays beers in the database


Parameters:
sort={asc,desc} - (optional) - sorts the results list alphabetically by username, can be either ascending or descending


stat={name,ibu,calories,abv,style,brewery_location,glass_type} - (optional) - specifies the stat which the beers will be sorted by


NOTE: if stat is not specified, specifying sort will not have any impact on the results


limit=LIMIT - (optional) - limits the number of results to the integer passed in as the LIMIT variable


Example: 
http://localhost:5000/beers/?sort=asc&stat=abv&limit=10


This will display the first 10 beers in the database in ascending order, sorted by ABV.


POST:
Creates a new beer.


Parameters:
name - (required) - string
ibu - (required) - integer
calories - (required) - integer
abv - (required) - float
style - (required) - string
brewery_location - (required) - string
glass_type - (required) - integer - this is the ID of the glass type
user_id - (required) - this is the user ID of the user adding the beer


POST parameters must be passed via JSON format.


Example:
curl -i -H "Content-Type: application/json" -X POST -d '{"name":"312","ibu":"40","calories":"125","abv":"4.2","style":"Pale Ale","brewery_location":"Goose Island","glass_type":"1","user_id":"1"}' http://localhost:5000/beers/


________________


**/beers/[id]/:**
Provides access to a specific beer.  Accepted HTTP verbs: GET, DELETE.


GET:
Retrieves information and reviews about the specified beer.


Parameters:
None


Example:
http://localhost:5000/beers/3/


DELETE:
Deletes the specified beer from the database.  Will also delete all reviews about the specified beer and delete all favorites associated with the specified beer.


Parameters:
None


Example:
curl -i -X DELETE http://localhost:5000/beers/3/

_______________________


**/glasses/:**
Provides access to all beer glasses in the database.  Accepted HTTP verbs: POST, GET.


GET:
Retrieves list of all glasses in the database.


Parameters:
sort={asc,desc} - (optional) - sorts the results list alphabetically by name, can be either ascending or descending


limit=LIMIT - (optional) - limits the number of results to the integer passed in as the LIMIT variable


Example:
http://localhost:5000/glasses/?sort=desc&limit=5


POST:
Creates a new beer glass:


Parameters:
name - (required) - string


POST parameters must be passed via JSON format


Example:
curl -i -H "Content-Type: application/json" -X POST -d '{"name":"Beer Boot"}' http://localhost:5000/glasses/

________________


**/glasses/[id]/:**
Allows access to a specific glass.  Accepted HTTP verb: DELETE.


DELETE:
Deletes the specified glass.


Parameters:
None


Example:
curl -i -X DELETE http://localhost:5000/glasses/3/


/reviews/:
Provides access to all reviews in the database.  Accepted HTTP verbs: GET, POST.


GET:
Displays reviews in the database


Parameters:
sort={asc,desc} - (optional) - sorts the results list alphabetically by username, can be either ascending or descending


stat={user_id,beer_id,aroma,appearance,taste,palate,bottle_style,overall} - (optional) - specifies the stat which the beers will be sorted by


NOTE: if stat is not specified, specifying sort will not have any impact on the results


limit=LIMIT - (optional) - limits the number of results to the integer passed in as the LIMIT variable


Example: 
http://localhost:5000/reviews/?sort=desc&stat=overall&limit=50


This will display the first 50 reviews in the database in descending order, sorted by overall rating.


POST:
Creates a new beer.


Parameters:
user_id - (required) - integer
beer_id - (required) - integer
aroma - (required) - float (minimum 0.0, maximum 5.0)
appearance - (required) - float (minimum 0.0, maximum 5.0)
taste - (required) - float (minimum 0.0, maximum 10.0)
palate - (required) - float (minimum 0.0, maximum 5.0)
bottle_style - (required) - float (minimum 0.0, maximum 5.0)


POST parameters must be passed via JSON format.


Example:
curl -i -H "Content-Type: application/json" -X POST -d '{"user_id":"1","beer_id":"3","aroma":"2.5","appearance":"4.2","taste":"7.8","palate":"4.0","bottle_style":"3.5"}' http://localhost:5000/reviews/


________________


**/reviews/[id]/:**
Provides access to a specific review.  Accepted HTTP verbs: GET, DELETE.


GET:
Retrieves content of a specific beer review.


Parameters:
None


Example:
http://localhost:5000/reviews/3/


DELETE:
Deletes the specified review from the database.


Parameters:
None


Example:
curl -i -X DELETE http://localhost:5000/reviews/3/


___________________


**/favorites/:**
Provides access to favorites in the database.  Accepted HTTP verb: POST.


POST:
Creates a new favorite:


Parameters:
user_id - (required) - integer
beer_id - (required) - integer


POST parameters must be passed via JSON format


Example:
curl -i -H "Content-Type: application/json" -X POST -d '{"user_id":"2",”beer_id”:”5”}' http://localhost:5000/favorites/

________________


**/favorites/[id]/:**
Allows access to a specific favorite.  Accepted HTTP verb: DELETE.


DELETE:
Deletes the specified favorite.


Parameters:
None


Example:
curl -i -X DELETE http://localhost:5000/favorites/3/

_________________


**/cronjobs/:**
Special path designed for daily and weekly system tasks.  Accepted HTTP verb: GET.


GET:
Triggers system tasks for resetting daily and weekly user limits.


Parameters:
jobtype={daily,weekly} - The daily job type will allow all users to add new beers to the database again.  The weekly job type will allow all users to review all beers again.


NOTE: This path is designed to be executed automatically at the specified intervals via system cronjobs as specified in the installation portion of this manual.


Example:
http://localhost:5000/cronjobs/?jobtype=daily
