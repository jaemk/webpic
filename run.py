#!/home/james/projects/envs/flask/bin/python

import os, sys, subprocess, time, datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, send_file, Response
from User import user

print(sys.version)

faillog = 'fail.log'

app = Flask(__name__)

def check_auth(username, password):
	return username == user.name and password == user.password

def authenticate():
	return Response(
		'Could not verify your access level for that URL.\n'
		'You have to login first',401,
		{'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		auth = request.authorization
		if not auth or not check_auth(auth.username, auth.password):
			if auth:
				with open(faillog,'a') as fail:
					today = datetime.date.today()
					now = datetime.datetime.now()
					fail.write(str(today) + "_"+ str(now.hour) + '.' +\
					str(now.minute) +'.'+ str(now.second) +": " +\
					auth.username + ", " + auth.password + "\n")
			return authenticate()
		return f(*args, **kwargs)
	return decorated

@app.route("/", methods=["GET","POST"])
@requires_auth
def index():
	return render_template("showpic.html")
	# return redirect("/cat")


@app.route("/cam_feed", methods=["GET"])
@requires_auth
def cam_feed():
	return send_file('static/pic.png', mimetype='image/png')

def get_pic_cat():
	print("Getting couch pic...")
	subprocess.call(['sudo /home/james/projects/webpic/app/cam.py 2'], shell=True)

def get_pic_dog():
	print("Getting dog pic...")
	subprocess.call(['sudo /home/james/projects/webpic/app/cam.py 1'], shell=True)
		

@app.route("/cat", methods=["GET","POST"])
@requires_auth
def cat():
	get_pic_cat()	
	return render_template("showpic.html")

@app.route("/dog", methods=["GET","POST"])
@requires_auth
def dog():
	get_pic_dog()	
	return render_template("showpic.html")


if __name__ == "__main__":
	app.run(host ='0.0.0.0', debug = False)
