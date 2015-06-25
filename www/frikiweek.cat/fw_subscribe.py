#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, make_response, redirect, request, session, url_for
import fw_subscribe_db as fw_db
import send_mail as sm
from utiles import *
from constants import *

fw_subs_blueprint = Blueprint('fw_subs_blueprint', __name__, template_folder='templates')

def database_connect(func):
	"""
	Decorator que connecta automàticament a la DB, passa la instància com argument, fa commit()/rollback() i tanca la DB
	"""
	def func_wrapper(**kwarg):
		if current_app.debug:
			db = fw_db.db_connect()
			response = func(db, **kwarg)
			db.commit()
			db.close()
		else:
			try:
				db = fw_db.db_connect()
				response = func(db, **kwarg)
				db.commit()
			except Exception as e:
				db.rollback()
				return "Alguna cosa no ha anat bé :(<br />Posa't amb contacte amb info[arroba]frikiweek.cat"
			finally:
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
		return render_template("apuntador/login.html", error="Usuari o contrassenya incorrectes")
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

@fw_subs_blueprint.route('/tallers', methods=['GET', 'POST'])
@fw_subs_blueprint.route('/tallers/<name>')
@database_connect
def apuntat(db, name=None):
	uid = session['user_id']

	if not uid:
		return redirect('/login/invalid')

	if request.method == 'POST':
		f = request.form
		tallers = []
		for key in f.keys():
			if key == 'each_taller':
				fw_db.update_inscripcions(db, uid, f.getlist(key))
				return redirect('/tallers/actualitzat')

	inscripcions = fw_db.getInscripcions(db, uid)
	tallers = [{'id': t.tid, 'nom': t.nom, 'data': t.data, 'inscrit': t.tid in inscripcions} for t in fw_db.getTallers(db)]

	return render_template('apuntador/apuntat.html', tallers=tallers, success=name == "actualitzat")

@fw_subs_blueprint.route('/logout')
@fw_subs_blueprint.route('/logout/<success>')
def logout(success=False):
	if success == 'success':
		return "S'ha tancat la sessió correctament"

	session['user_id'] = None
	return redirect('/logout/success')

@fw_subs_blueprint.route('/signup', methods=['GET', 'POST'])
@fw_subs_blueprint.route('/signup/<email>', methods=['GET', 'POST'])
@database_connect
def signup(db, email=""):
	if request.method == "POST":
		name = request.form.get("name")
		email = request.form.get("email")
		passwd = request.form.get("passwd")

		if name and email and passwd:
			confirmation = fw_db.Usuari(db, passwd, nom, email).save()
			sm.send_confirmation_mail(email, name, url_for('/signup/validate/') + confirmation)
			return render_template('apuntador/signup.html', success=True)
		else:
			return render_template('apuntador/signup.html', success=False)

	return render_template('apuntador/signup.html', email=email)

@fw_subs_blueprint.route('/signup/validate/<confirmation>')
@database_connect
def signup_validated(db, confirmation=None):
	if confirmation and fw_db.confirma(db, confirmation):
		return redirect('/login')

	return render_template('apuntador/signup_validated.html')
