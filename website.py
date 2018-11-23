from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for, copy_current_request_context
from flask_socketio import SocketIO, emit
import os
import datetime
import bcrypt
from sqlalchemy.orm import sessionmaker
from tabledef import db, app, Admin, AdminLog, User, AccessLog
import hardwareControl
import time
import re
from threading import Thread, Event

socketio = SocketIO(app)

thread = Thread()
thread_stop_event = Event()

#app = Flask(__name__)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

connected_IPs = []

class IP:
	last_heard_from = datetime.datetime.now()
	logged_in = False
	is_banned = False
	banned_until = datetime.datetime.now()
	attempts = 0
	
	def __init__(self, ipaddress):
		self.address = ipaddress

class DoorThread(Thread):
	def __init__(self):
		self.delay = 1
		super(DoorThread, self).__init__()

	def doorStatusChecker(self):
		door = hardwareControl.Door()
		
		is_open = door.is_open()
		is_locked = door.is_locked()
		is_blocked = door.is_blocked()
		old_is_open = is_open
		old_is_locked = is_locked
		old_is_blocked = is_blocked
		socketio.emit('doorchange', {'is_open': is_open, 'is_locked': is_locked, 'is_blocked': is_blocked}, namespace='/doorcontrol')
		
		#myTime = time.time()
		
		while not thread_stop_event.isSet():
			old_is_open = is_open
			old_is_locked = is_locked
			old_is_blocked = is_blocked
			is_open = door.is_open()
			is_locked = door.is_locked()
			is_blocked = door.is_blocked()
			
			if (is_open != old_is_open) or (is_locked != old_is_locked) or (is_blocked != old_is_blocked):
				socketio.emit('doorchange', {'is_open': is_open, 'is_locked': is_locked, 'is_blocked': is_blocked}, namespace='/doorcontrol')
			#myTime = time.time()
			
			time.sleep(self.delay)

	def run(self):
		self.doorStatusChecker()

@app.before_request
def limit_remote_addr():
    if get_ip().is_banned and (get_ip().banned_until > datetime.datetime.now()):
        abort(403)  # Forbidden

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def home():
	if (get_ip().is_banned):
		if (get_ip().banned_until < datetime.datetime.now()):
			get_ip().is_banned = False
		else:
			flash("You are currently banned from too many login attempts!")
		return render_template('login.html')
	elif (datetime.datetime.now() - get_ip().last_heard_from > datetime.timedelta(minutes=30)):
		session['logged_in'] = False
		session['username'] = ""
		ip = get_ip()
		ip.logged_in = False
		#ip.last_heard_from = datetime.datetime.now()
		flash("You've been logged out from inactivity.")
		return render_template("login.html")
	elif (not session.get('logged_in')) or (not get_ip().logged_in):
		return render_template('login.html')
	else:
		get_ip().last_heard_from = datetime.datetime.now()
		selected=1
		door = hardwareControl.Door()
		search_users = []
		if request.method == "POST":
			if request.form.get('panel') == 'admin-list':
				selected=1
				if request.form.get('add'):
					admin_name = request.values.get('username').lower()
					admin_password = request.values.get('password')
					
					logged_in_admin = str(session['username']).lower()
					logged_in_admin_password = str(request.values.get('admin-password')).encode('UTF-8')
					
					s = db.session
					query = s.query(Admin).filter(Admin.username.in_([logged_in_admin]))
					result = query.first()
					
					if not result or not bcrypt.checkpw(logged_in_admin_password, result.password):
						flash("Admin password does not match logged in admin")
					elif not admin_name or not admin_password:
						flash('Blank Username or Password')
					elif not password_meets_complexity(admin_password):
						flash('Password does not meet complexity requirements.')
					else:
						admin_password = construct_hash_from(admin_password)
						admin = Admin(username=admin_name, password=admin_password)
						add_admin(admin)
				elif request.form.get('delete'):
					logged_in_admin = str(session['username']).lower()
					logged_in_admin_password = str(request.values.get('admin-password')).encode('UTF-8')
					
					s = db.session
					query = s.query(Admin).filter(Admin.username.in_([logged_in_admin]))
					result = query.first()
					
					if not result or not bcrypt.checkpw(logged_in_admin_password, result.password):
						flash("Admin password does not match logged in admin")
					else:
						admin_name = request.values.get('username')
						remove_admin(admin_name)
			elif request.form.get('panel') == 'admin-log':
				selected=2
			elif request.form.get('panel') == 'user-list':
				selected=3
				if request.form.get('add') :
					user_first_name = request.values.get('first-name')
					user_last_name = request.values.get('last-name')
					user_name = "{}, {}".format(user_last_name, user_first_name)
					user_id = request.values.get('id')
					user_email = request.values.get('email')
					user = User(name=user_name, id=user_id, email=user_email)
					add_user(user)
				elif request.form.get('delete'):
					user_name = request.values.get('name')
					user_id = request.values.get('id')
					user_email = request.values.get('email')
					user = User(name=user_name, id=user_id, email=user_email)
					remove_user(user)
			elif request.form.get('panel') == 'user-log':
				selected=4
			elif request.form.get('panel') == 'user-search':
				selected=5
				search_user = {}
				if request.form.get('id'):
					search_user['id'] = request.form.get('id')
				if request.form.get('name'):
					search_user['name'] = request.form.get('name')
				if request.form.get('email'):
					search_user['email'] = request.form.get('email')
				search_users = search_for_user(search_user)
				if request.form.get('delete'):
					user = User(name=search_user["name"], id=search_user["id"], email=search_user["email"])
					remove_user(user)
					search_users = {}
			elif request.form.get('panel') == 'door-control':
				selected=6
				if request.form.get('unlock'):
					door.unlock()
				elif request.form.get('lock'):
					door.lock()
				elif request.form.get('block'):
					door.block()
				elif request.form.get('unblock'):
					door.unblock()
		
		username = session['username']
		return render_template('dashboard.html', username=username, get_admins=get_admins, get_admin_logs=get_admin_logs, get_users=get_users, get_user_logs=get_user_logs, search_users=search_users, selected=selected, door=door)

@app.route('/login', methods=['POST'])
def do_admin_login():
	ip = get_ip()
	ip.attempts += 1
	
	if (ip.is_banned):
		if (ip.banned_until < datetime.datetime.now()):
			ip.is_banned = False
		else:
			flash("You are currently banned from too many login attempts!")
			return render_template('login.html')
	
	POST_USERNAME = str(request.form['username']).lower()
	POST_PASSWORD = str(request.form['password']).encode('UTF-8')
	
	time.sleep((ip.attempts - 1) ** 1.5)

	s = db.session
	query = s.query(Admin).filter(Admin.username.in_([POST_USERNAME]))
	result = query.first()
	if result and bcrypt.checkpw(POST_PASSWORD, result.password):
		ip.attempts = 0
		ip.logged_in = True
		ip.last_heard_from = datetime.datetime.now()
		session['logged_in'] = True
		session['username'] = POST_USERNAME
		return redirect("/")
	else:
		flash('Incorrect username or password!')
		if ip.attempts > 30:
			ip.is_banned = True
			ip.banned_until = datetime.datetime.now() + datetime.timedelta(hours=24)
		elif ip.attempts % 5 == 0:
			event = "{} invalid login attempts as user {}.".format(ip.attempts, POST_USERNAME)
			log_event(event, ip.address)
	return home()

@app.route('/login', methods=['GET'])
def pass_to_login():
	return home()

@app.route('/admin-logs', methods=['GET', 'POST'])
def do_admin_logs():
	if not session.get('logged_in'):
		return render_template('login.html')
	else:
		return render_template('admin-logs.html', get_all_admin_logs=get_all_admin_logs)

@app.route('/user-logs', methods=['GET', 'POST'])
def do_user_logs():
	if not session.get('logged_in'):
		return render_template('login.html')
	else:
		return render_template('user-logs.html', get_all_user_logs=get_all_user_logs)
 
@app.route('/logout')
def logout():
	session['logged_in'] = False
	session['username'] = ""
	#ip = get_ip()
	#ip.logged_in = False
	#ip.last_heard_from = datetime.datetime.now()
	return home()

@socketio.on('connect', namespace='/doorcontrol')
def test_connect():
	global thread
	global thread_stop_event
	
	if not thread.isAlive():
		thread_stop_event.clear()
		thread = DoorThread()
		thread.start()

@socketio.on('disconnect', namespace='/doorcontrol')
def test_disconnect():
	global thread_stop_event
	thread_stop_event.set()

def get_admins():
	s = db.session
	return_list = list(s.query(Admin).all())
	return return_list

def add_admin(admin):
	s = db.session
	user = Admin(username=admin.username, password=admin.password)
	s.add(user)
	s.commit()
	event = "Added admin {}".format(user.username)
	log_event(event, session["username"])

def remove_admin(admin_name):
	s = db.session
	selected_user = s.query(Admin).filter_by(username=admin_name).first()
	s.delete(selected_user)
	s.commit()
	event = "Removed admin {}".format(admin_name)
	log_event(event, session["username"])

def get_users():
	s = db.session
	return_list = list(s.query(User).all())
	return return_list

def add_user(user):
	s = db.session
	s.add(user)
	s.commit()
	event = "Added user {}".format(user.name)
	log_event(event, session["username"])

def remove_user(user):
	s = db.session
	selected_user = s.query(User).filter(User.id==user.id, User.name==user.name, User.email==user.email).first()
	s.delete(selected_user)
	s.commit()
	event = "Removed user {}".format(user.name)
	log_event(event, session["username"])

def search_for_user(user):
	s = db.session
	q = s.query(User)
	for attr, value in user.items():
		q = q.filter(getattr(User, attr).like("%%%s%%" % value))
	return_list = list(q.all())
	return return_list

def get_admin_logs():
	s = db.session
	return_list = list(s.query(AdminLog).order_by(AdminLog.date.desc()).limit(20).all())
	return return_list

def get_all_admin_logs():
	s = db.session
	return_list = list(s.query(AdminLog).order_by(AdminLog.date.desc()).all())
	return return_list

def get_user_logs():
	s = db.session
	return_list = list(s.query(AccessLog).order_by(AccessLog.date.desc()).limit(20).all())
	return return_list
	
def get_all_user_logs():
	s = db.session
	return_list = list(s.query(AccessLog).order_by(AccessLog.date.desc()).all())
	return return_list

def log_event(event, cause):
	s = db.session
	log = AdminLog(event=event, cause=cause, date=datetime.datetime.now())
	s.add(log)
	s.commit()

def get_ip():
	return_ip = None
	for ip in connected_IPs:
		if ip.address == request.remote_addr:
			return_ip = ip
	if not return_ip:
		return_ip = IP(request.remote_addr)
		connected_IPs.append(return_ip)
	return return_ip

def password_meets_complexity(password):
	length_error = len(password) < 8
	digit_error = re.findall(r"\d", password) is None
	uppercase_error = re.findall(r"[A-Z]", password) is None
	lowercase_error = re.findall(r"[a-z]", password) is None
	symbol_error = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) is None

	password_ok = not (length_error or digit_error or uppercase_error or lowercase_error or symbol_error)
	
	return password_ok

def construct_hash_from(password):
	salt = bcrypt.gensalt()
	password = password.encode('UTF-8')
	hash = bcrypt.hashpw(password, salt)
	return(hash)
 
if __name__ == "__main__":
	app.secret_key = os.urandom(12)
	socketio.run(app=app, debug=True, host='0.0.0.0', port=443, ssl_context=('keys/server.crt', 'keys/server.key'))
	#app.run(debug=True, host='0.0.0.0', port=443, ssl_context=('keys/server.crt', 'keys/server.key'))
