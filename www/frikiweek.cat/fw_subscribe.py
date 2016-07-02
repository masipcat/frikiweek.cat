#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, make_response, redirect, request, session, url_for
import fw_subscribe_db as fw_db
import send_mail as sm
import traceback
from utiles import *

fw_subs_blueprint = Blueprint('fw_subs_blueprint', __name__, template_folder='templates')

def auth(func):
	def func_wrapper(*args, **kwarg):
		uid = current_uid()
		if not uid:
			return redirect('/login')

		return func(uid, *args, **kwarg)
	
	func_wrapper.__name__ = func.__name__
	return func_wrapper

def database_connect(func):
	"""
	Decorator que connecta automàticament a la DB, passa la instància com argument, fa commit()/rollback() i tanca la DB
	"""
	def func_wrapper(*args, **kwarg):
		if current_app.debug:
			db = fw_db.db_connect()
			response = func(db, *args, **kwarg)
			db.commit()
			db.close()
		else:
			try:
				db = fw_db.db_connect()
				response = func(db, *args, **kwarg)
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
@fw_subs_blueprint.route('/login/<error>')
@fw_subs_blueprint.route('/login/<error>/<email>')
@database_connect
def login(db, error="", email=""):
	uid = current_uid()
	if uid:
		return redirect('/tallers')
	
	if error == "invalid":
		return render_template("apuntador/login.html", error="Usuari o contrassenya incorrectes", email=email)
	
	if error == "_":
		return render_template("apuntador/login.html", email=email)
	
	else:
		return render_template("apuntador/login.html")

def unauthorized():
	return render_template("apuntador/login.html", content="No estàs autoritzat per veure aquesta pàgina")

@fw_subs_blueprint.route('/check_login', methods=["POST"])
@database_connect
def check_login(db):
	email = request.form.get('email')
	passwd = request.form.get('passwd')
	
	if not email:
		return redirect('/login/invalid')
		
	exist = fw_db.user_exist(db, email)

	if not exist or not passwd:
		return redirect('/login/invalid/%s' % email)

	status, uid = fw_db.login(db, email, passwd)
	
	if status == fw_db.SUCCESS:
		session['user_id'] = uid
		return redirect('/tallers')

	session['user_id'] = None
	return redirect('/login/invalid/%s' % email)

@fw_subs_blueprint.route('/resetpassword')
@fw_subs_blueprint.route('/resetpassword/<password_hash>')
def reset_password_action_get(password_hash=None):
	# Formulari per posar l'email o la nova contrasenya
	return render_template('apuntador/reset_password.html', password_hash=password_hash)

@fw_subs_blueprint.route('/resetpassword', methods=['POST'])
@fw_subs_blueprint.route('/resetpassword/<password_hash>', methods=['POST'])
@database_connect
def reset_password_action_post(db, password_hash=None):
	if password_hash == None: # Processar enviament email
		email = request.form.get("email")
		token = fw_db.get_reset_password_hash_if_exists(db, email)
		
		if token:
			sm.send_reset_password_mail(email, url_for('.reset_password_action_get', password_hash=token, _external=True))
		
		return render_template('apuntador/reset_password.html', msg="Si l'adreça de correu es troba a la nostra base de dades, rebràs un missatge. El correu pot tardar a enviar-se fins a 5 minuts.")
		
	else: # Processar el canvi de contrasenya
		if fw_db.can_reset_password(db, password_hash):
			email = request.form.get("email")
			passwd = request.form.get("passwd")
			
			if email and passwd:
				if fw_db.reset_password(db, password_hash, email, passwd):
					return render_template('apuntador/reset_password.html', msg="La contrasenya s'ha canviat correctament")
		
		return render_template('apuntador/reset_password.html', msg="La contrasenya s'ha canviat correctament")

@fw_subs_blueprint.route('/tallers', methods=['GET', 'POST'])
@fw_subs_blueprint.route('/tallers/<name>')
@auth
@database_connect
def apuntat(db, uid, name=None):
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
	
	return render_template('apuntador/admin_tallers.html', tallers=fw_db.llista_tallers(db), msg=msg, error=error, my_uid=current_uid())

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
