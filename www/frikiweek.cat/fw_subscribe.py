#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, make_response, redirect, request
#from fw_subscribe_db import *
from utiles import *
from constants import *

fw_subs_blueprint = Blueprint('fw_subs_blueprint', __name__, template_folder='templates')

def database_connect(func):
	"""
	Decorator que connecta automàticament a la DB, passa la instància com argument, fa commit()/rollback() i tanca la DB
	"""
	def func_wrapper(**kwarg):
		db = db_connect()
		try:
			response = func(db, **kwarg)
			db.commit()
		except e:
			db.rollback()
			raise e
		finally:
			db.close()
		return response

	func_wrapper.__name__ = func.__name__
	return func_wrapper

@fw_subs_blueprint.route('/login/<error>')
@database_connect
def login(db, error=False):
	error = error and True
	return render_template("apuntador/login.html", error=error)

@fw_subs_blueprint.route('/check_login', methods=["POST"])
@database_connect
def check_login(db):
	email = request.form['email']
	passwd = request.form['passwd']
	
	if email and passwd:
		uid = login(db, email, passwd)
		
		if uid == ERR_USER_NOT_FOUND or uid == ERR_USER_INVALID_LOGIN:
			session['user_id'] = None
			return redirect('/login/invalid')
		
		session['user_id'] = uid
		return redirect('/apuntat')

@fw_subs_blueprint.route('/tallers')
@database_connect
def apuntat(db):
	uid = session['user_id']

	myTallers = getMyTallers(db, uid)
	tallers = [{'id': t.tid, 'nom': t.nom, 'data': t.data, 'inscrit': t in myTallers} for t in getTallers(db)]
	
	return render_template('apuntat.html', tallers=tallers)

@fw_subs_blueprint.route('/logout/<success>')
def logout(success=False):

	if success == 'success':
		return "S'ha tancat la sessió correctament"

	session['user_id'] = None
	return redirect('/logout/success')

@fw_subs_blueprint.route('/signup/<email>')
@database_connect
def signup(db, email):
	return "db %s, signup %s" % (db, email)