#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, make_response, redirect, request, session, url_for
import fw_subscribe_db as fw_db
import send_mail as sm
import traceback
from utiles import *

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
				return """Alguna cosa no ha anat bé :(<br />
						  Posa't amb contacte amb info[arroba]frikiweek.cat<br />
						  <pre>%s</pre>""" % traceback.format_exc().replace("\n", "<br />")
			finally:
				db.close()

		return response

	func_wrapper.__name__ = func.__name__
	return func_wrapper

def current_uid():
	try:
		uid = session['user_id']
	except KeyError:
		uid = None
	return uid

@fw_subs_blueprint.route('/login')
@fw_subs_blueprint.route('/login/<extra>')
@database_connect
def login(db, extra=""):
	uid = current_uid()
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
	uid = current_uid()
	if not uid:
		return redirect('/login/invalid')

	if request.method == 'POST':
		f = request.form
		tallers = []
		for key in f.keys():
			if key == 'each_taller':
				fw_db.update_inscripcions(db, uid, f.getlist(key))
				return redirect('/tallers/actualitzat')

	user = fw_db.Usuari.getById(db, uid)
	inscripcions = fw_db.getInscripcions(db, uid)
	tallers = [{'id': t.tid, 'nom': t.nom, 'data': t.data.strftime("%d/%m a les %H:%M"), 'inscrit': t.tid in inscripcions} for t in fw_db.getTallers(db)]
	return render_template('apuntador/apuntat.html', name=user.nom, tallers=tallers, success=name == "actualitzat")

@fw_subs_blueprint.route('/logout')
@fw_subs_blueprint.route('/logout/<success>')
def logout(success=False):
	if success == 'success':
		return render_template('apuntador/logout.html')

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
			usuari = fw_db.Usuari.getByEmail(db, email)

			if usuari:
				return render_template('apuntador/signup.html', error="Aquest usuari ja existeix!")

			usuari = fw_db.Usuari(db, passwd, name, email)
			r = sm.send_confirmation_mail(email, name, url_for('.signup_validate', confirmation=usuari.confirmacio, _external=True))

			status_code = -1
			if r != None:
				status_code = r.status_code

			if status_code == 200:
				usuari.insert()
				advert = "hotmail" in email or "outlook" in email # Mostra l'advertència de comprovar la carpeta d'spam
				return render_template('apuntador/signup.html', check_inbox=True, advert=advert)
		
			return render_template('apuntador/signup.html', email=email, error="Hi ha hagut un error en enviar l'email")

		return render_template('apuntador/signup.html', email=email, check_inbox=True)

	return render_template('apuntador/signup.html', email=email)

@fw_subs_blueprint.route('/signup/validate/<confirmation>')
@database_connect
def signup_validate(db, confirmation=None):
	if confirmation and fw_db.confirma(db, confirmation):
		return redirect('/login')

	return render_template('apuntador/signup_validated.html')

@fw_subs_blueprint.route('/admin/tallers')
@fw_subs_blueprint.route('/admin/tallers/<status>')
@database_connect
def admin_tallers(db, status=None):
	msg = error = None

	if status == "success_send":
		msg = "El missatge s'ha enviat correctament"
	elif status == "failed_send":
		error = "El missatge està buit o ha fallat alguna cosa... :(\nPosa't en contacte nosaltres a través de info@frikiweek.cat"
	
	return render_template('apuntador/admin_tallers.html', tallers=fw_db.tallers_count(db), msg=msg, error=error, my_uid=current_uid())

@fw_subs_blueprint.route('/admin/send_msg/<id_taller>', methods=["GET", "POST"])
@database_connect
def send_msg(db, id_taller=None):

	if not id_taller:
		return render_template("apuntador/send_msg.html", error="No s'ha especificat cap identificador de taller")
	
	uid = current_uid()
	if not uid:
		return render_template("apuntador/send_msg.html", error="No estàs autoritzat per veure aquesta pàgina")

	usuari = fw_db.Usuari.getById(db, uid)
	taller = fw_db.getTallerById(db, id_taller)

	if taller.id_ponent != uid:
		return render_template("apuntador/send_msg.html", error="No estàs autoritzat per veure aquesta pàgina")

	# L'usuari està autoritzat per enviar missatges a aquest taller
	if request.method == "GET":
		return render_template("apuntador/send_msg.html", taller=taller, authorized=True)

	elif request.method == "POST":
		msg = request.form.get("msg")
		
		if not msg:
			return render_template("apuntador/send_msg.html", taller=taller, error="No has enviat cap missatge", authorized=True)

		inscrits = taller.getInscrits(db)
		responses = sm.send_about_talk([i.correu for i in inscrits], taller, msg.replace("\n", "<br/ >"))
		n_success = sum([r.status_code == 200 for r in responses])

		# Si la resposta és una llista de respostes de 'requests' i més del 80% són satisfactòries:
		if isinstance(responses, list) and n_success > len(responses) * 0.8:
			return redirect('/admin/tallers/success_send')

	return redirect('/admin/tallers/failed_send')
