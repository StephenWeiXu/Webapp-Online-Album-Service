from flask import *
from extensions import mysql
import hashlib
import time
import os

album = Blueprint('album', __name__, template_folder='templates')

@album.route('/album/edit', methods=['GET', 'POST'])
def album_edit_route():
	error_info = ""
	albumid = request.args.get('id')
	if not check_album_id(albumid):
		abort(404)

	if request.method == "POST":
		operation = request.form["op"]
		if operation == "delete":
			picid = request.form["picid"]
			if check_pic_exist(albumid, picid):
				delete_pic(picid)
		elif operation == "add":
			file = request.files['file']
			if file and check_img_ext(file.filename):
				picid = get_hash(albumid, file.filename)
				if check_pic_exist(albumid, picid):  # if picid haven't been added
					error_info = "Failed! Photo already exists in this album! Please choose abother photo"
				else:	
					format = file.filename[-3:]
					date = time.strftime('%Y-%m-%d')
					add_pic(picid, format, date, albumid)
					if not os.path.exists("static/images"):
						os.mkdir("static/images")
					file.save(os.path.join("static", "images", picid+"."+format))
				
	options = {"edit": True, "error_info": error_info, "albumid": albumid, "pics": get_pics(albumid)}
	return render_template("album.html", **options)

@album.route('/album')
def album_route():
	albumid = request.args.get('id')
	if not check_album_id(albumid):
		abort(404)

	options = {"edit": False, "pics": get_pics(albumid), "albumid": albumid}
	return render_template("album.html", **options)

def delete_pic(picid):
	cur = mysql.connection.cursor()
	cur.execute("SELECT format FROM Photo WHERE picid=%s", [picid])
	results = cur.fetchall()
	format = results[0][0]

	cur = mysql.connection.cursor()
	cur.execute("DELETE FROM Contain WHERE picid=%s", [picid])
	cur.execute("DELETE FROM Photo WHERE picid=%s", [picid])
	mysql.connection.commit()

	filename = os.path.join("static", "images", picid+"."+format)
	if os.path.exists(filename):
		os.remove(filename)

def add_pic(picid, format, date, albumid):
	cur = mysql.connection.cursor()
	cur.execute("SELECT MAX(sequencenum) FROM Contain WHERE albumid=%s", [albumid])
	results = cur.fetchall()
	if not results[0][0] == None:
		sequencenum = results[0][0]
	else:
		sequencenum = -1

	cur = mysql.connection.cursor()
	cur.execute("INSERT INTO Photo (picid, format, date) VALUES (%s, %s, %s)", (picid, format, date))
	cur.execute("INSERT INTO Contain (albumid, picid, caption, sequencenum) VALUES (%s, %s, %s, %s)", (albumid, picid, "", sequencenum+1))
	mysql.connection.commit()


def get_pics(albumid):
	cur = mysql.connection.cursor()
	cur.execute("SELECT picid FROM Contain WHERE albumid=%s ORDER BY sequencenum", [albumid])
	results = cur.fetchall()

	pics = []
	for res in results:
		cur2 = mysql.connection.cursor()
		cur2.execute("SELECT format FROM Photo WHERE picid=%s", [res[0]])
		results2 = cur2.fetchall()
		pics.append(res[0]+'.'+results2[0][0])
	return pics

def check_pic_exist(albumid, picid):
	cur = mysql.connection.cursor()
	cur.execute("SELECT picid FROM Contain WHERE albumid=%s", [albumid])
	results = cur.fetchall()

	for res in results:
		if picid == res[0]:
			return True
	return False


def check_img_ext(filename):
	fname, fileext = os.path.splitext(filename)
	fileext = fileext[1:].lower()
	if fileext == "png" or fileext == "jpg" or fileext == "bmp" or fileext == "bmp":
		return True
	return False

def check_album_id(albumid):
	cur = mysql.connection.cursor()
	cur.execute("SELECT albumid FROM Album WHERE albumid=%s", [albumid])
	results = cur.fetchall()
	if results:
		return True
	return False


def get_hash(albumid, filename):
	cur = mysql.connection.cursor()
	cur.execute("SELECT username, title FROM Album WHERE albumid=%s", [albumid])
	results = cur.fetchall()

	username, album_title = results[0]
	m = hashlib.md5(username + album_title + filename)
	return m.hexdigest()
