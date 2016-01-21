from flask import *
from extensions import mysql
import os
import time

albums = Blueprint('albums', __name__, template_folder='templates')

@albums.route('/albums/edit', methods=['GET', 'POST'])
def albums_edit_route():
	# with open(os.path.join('static', 'log.log'), "a") as logfile:
	# 	log = time.strftime('%Y-%m-%d %H:%M:%S') + " "
	# 	if request.method == "POST":
	# 		log += "POST"
	# 	else:
	# 		log += "GET"
	# 	log += " " + request.url
	# 	if request.method == "POST":
	# 		log += " ("
	# 		for key in request.form.keys():
	# 			log += key + ":" + request.form[key] + ","
	# 		log += ")"
	# 	logfile.write(log+"\n")

	error_info = ""
	if request.method == "POST":
		if not ("op" in request.form.keys()):
			abort(404)
		operation = request.form["op"]
		if operation == "delete":
			albumid = request.form["albumid"]
			if not ("albumid" in request.form.keys()):
				abort(404)
			if not check_album_id(albumid):
				abort(404)
			delete_album(albumid)
		elif operation == "add":
			username = request.form["username"]
			if not ("username" in request.form.keys()):
				abort(404)
			if not check_user_name(username):
				abort(404)
			if not ("title" in request.form.keys()):
				abort(404)
			album_title = request.form["title"]
			if check_album_exist(album_title):
				error_info = "Failed! Album title already exists! Please choose another title"
			else:
				add_album(username, album_title)
		else:
			abort(404)

	user_albums, username = get_user_albums()

	options = {
		"edit": True,
		"error_info": error_info,
		"username": username,
		"user_albums": user_albums
	}
	return render_template("albums.html", **options)


@albums.route('/albums')
def albums_route():
	# with open(os.path.join('static', 'log.log'), "a") as logfile:
	# 	log = time.strftime('%Y-%m-%d %H:%M:%S') + " "
	# 	if request.method == "POST":
	# 		log += "POST"
	# 	else:
	# 		log += "GET"
	# 	log += " " + request.url
	# 	if request.method == "POST":
	# 		log += " ("
	# 		for key in request.form.keys():
	# 			log += key + ":" + request.form[key] + ","
	# 		log += ")"
	# 	logfile.write(log+"\n")

	user_albums, username = get_user_albums()

	options = {
		"edit": False,
		"username": username,
		"user_albums": user_albums
	}
	return render_template("albums.html", **options)

def check_user_name(username):
	cur = mysql.connection.cursor()
	cur.execute("SELECT username FROM User WHERE username=%s", [username])
	results = cur.fetchall()
	if not results:
		return False
	return True

def check_album_id(albumid):
	cur = mysql.connection.cursor()
	cur.execute("SELECT albumid FROM Album WHERE albumid=%s", [albumid])
	results = cur.fetchall()
	if not results:
		return False
	return True

''' Utility functions to query database and get results '''
def get_user_albums():
	username = request.args.get('username') # Get username from template file albums.html

	if not check_user_name(username):
		abort(404)

	albums = []
	cur = mysql.connection.cursor()
	cur.execute("SELECT albumid, title FROM Album WHERE username=%s", [username])
	results = cur.fetchall()
	for res in results:
		albums.append(res)

	return albums, username	

def delete_album(albumid):
	conn = mysql.connection
	cur = conn.cursor()

	#Find if there is photo in the album and delete from filesystem
	cur.execute("SELECT picid, format FROM Photo WHERE picid IN (SELECT picid FROM Contain WHERE albumid=%s)", [albumid])
	picid_results = cur.fetchall()
	if picid_results:
		for res in picid_results:
			photo_path = os.path.join("static", "images", res[0]+"."+res[1])
			if os.path.exists(photo_path):
				os.remove(photo_path)

	cur.execute("DELETE FROM Album WHERE albumid=%s", [albumid])
	conn.commit()

def add_album(username, album_title):
	conn = mysql.connection
	cur = conn.cursor()
	cur.execute("INSERT INTO\
				Album(albumid, title, created, lastupdated, username)\
	 			VALUES\
	 			(NULL, %s, NULL, NULL, %s)", [album_title, username])
	conn.commit()

def check_album_exist(album_title):
	user_albums, username = get_user_albums()
	for album_info in user_albums:
		if album_title == album_info[1]:
			return True
	return False

