#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, make_response, redirect, request, session
import fw_subscribe_db as fw_db
from utiles import *
from constants import *

fw_subs_blueprint = Blueprint('fw_subs_blueprint', __name__, template_folder='templates')

def database_connect(func):
	"""
	Decorator que connecta automàticament a la DB, passa la instància com argument, fa commit()/rollback() i tanca la DB
	"""
	def func_wrapper(**kwarg):
		db = fw_db.db_connect()
		#try:
		response = func(db, **kwarg)
		db.commit()
		#except Exception as e:
		#	db.rollback()
		#	raise e
		#finally:
		db.close()
		return response

	func_wrapper.__name__ = func.__name__
	return func_wrapper

@fw_subs_blueprint.route('/login')
@fw_subs_blueprint.route('/login/<extra>')
@database_connect
def login(db, extra=""):

	uid = session['user_id']

	if uid:
		return redirect('/tallers')

	if extra == "invalid":
		return render_template("apuntador/login.html", error=True)
	elif extra != "":
		return render_template("apuntador/login.html", email=extra)
	else:
		return render_template("apuntador/login.html")

@fw_subs_blueprint.route('/check_login', methods=["POST"])
@database_connect
def check_login(db):
	email = request.form.get('email')
	passwd = request.form.get('passwd')
	
	if not email:
		return redirect('/login/invalid')
		
	exist = fw_db.user_exist(db, email)

	if not exist:
		return redirect('/signup/%s' % email)

	if not passwd:
		return redirect('/login/%s' % email)

	status, uid = fw_db.login(db, email, passwd)
	
	if status == fw_db.SUCCESS:
		session['user_id'] = uid
		return redirect('/tallers')

	session['user_id'] = None
	return redirect('/login/invalid')

@fw_subs_blueprint.route('/tallers')
@database_connect
def apuntat(db):
	uid = session['user_id']

	if not uid:
		return redirect('/login/invalid')

	#myTallers = fw_db.getMyTallers(db, uid)
	tallers = [{'id': t.tid, 'nom': t.nom, 'data': t.data, 'inscrit': False} for t in fw_db.getTallers(db)]
	
	return render_template('apuntador/apuntat.html', tallers=tallers)

@fw_subs_blueprint.route('/logout')
@fw_subs_blueprint.route('/logout/<success>')
def logout(success=False):
	if success == 'success':
		return "S'ha tancat la sessió correctament"

	session['user_id'] = None
	return redirect('/logout/success')

@fw_subs_blueprint.route('/signup/<email>')
@database_connect
def signup(db, email):
	return "signup %s" % (email,)
