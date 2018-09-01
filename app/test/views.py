from flask import after_this_request, send_file
from flask import render_template, redirect, url_for, abort, flash, request, current_app, make_response
from flask_login import login_required, current_user, login_user, logout_user
from . import test
from .. import db
from ..models.ua_models import ua_user, ua_session, ua_session_data, User
from ..models.res_models import res_file
import json


@test.before_app_request
def before_request():
	#print(current_user)
	current_user


@test.route('/', methods=['GET', 'POST'])
def index():

	current_user.set_data('key1', 'val1')
	current_user.set_data('key2', 'val2')
	current_user.set_data('key3', 'val3')

	current_user.set_data('key4', None)


	return render_template('test/index.html', session=current_user.datas)

@test.route('/edit', methods=['GET', 'POST'])
def edit():

	return render_template('test/edittest.html')

@test.route('/login', methods=['GET', 'POST'])
def login():
	user = User(current_user.sess, 1)
	login_user(user, True)

	current_user.set_data('loginkey1', 'val1')

	return render_template('test/login.html', session=current_user.datas)

@test.route('/user', methods=['GET', 'POST'])
@login_required
def user_index():

	current_user.set_data('userkey1', 'val1')

	return render_template('test/user.html', session=current_user.datas)

@test.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():

	current_user.logout()
	logout_user()
	current_user.clear()
	

	flash('You have been logged out.')
	return redirect(url_for('test.index'))

@test.route('/auth', methods=['GET', 'POST'])
def auth():
	

	return render_template('test/login.html', session=current_user.datas)


@test.route('/uploadtest', methods=['GET', 'POST'])
def upload_test():

	return render_template('test/upload.html')

@test.route('/uploadfile/<file_name>/<path:type_name>', methods=['POST'])
def upload_file(file_name, type_name):

	print("%s, %s" % (file_name, type_name))

	file = res_file(file_name=file_name, file_type=type_name, file_data=request.data)
	db.session.add(file)
	db.session.commit()

	#f_img.write(request.data)

	jsonrep = {'state': '200'}

	return json.dumps(jsonrep, ensure_ascii=False)

@test.route('/file/<fileid>', methods=['GET'])
def file_get(fileid):

	file = res_file.query.get(int(fileid))
	
	response = make_response(file.file_data)
	response.mimetype = file.file_type

	return response





