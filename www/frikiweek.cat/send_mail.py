#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from db_constants import *

def default_structure(nom):
	salutacio = "Hola"

	if len(nom):
		salutacio = "Hola %s" % nom

	return """{0},<br/><br/>%s<br/><br/>
	<strong>T'esperem la setmana del 29!</strong><br/><br/>
	Atentament,<br>
	Els coordinadors de la FW15<br><br>
	<em>Si tens qualsevol dubte, pots escriure'ns a info@frikiweek.cat</em>""".format(salutacio)

def send_confirmation_mail(to, nom, confirm_url):
	html = default_structure(nom) % """Gràcies per registrar-te! Ara només has de clicar el següent enllaç:<br/><br/>
	<a href='{0}'>Confirmació</a><br/><br/>""".format(confirm_url)

	return send_mailgun(to, "Confirmació de l'adreça electrònica", html)

def send_reset_password_mail(to, change_url):
	html = default_structure("") % """Clica el següent enllaç per escollir una nova contrasenya:<br/><br/>
	<a href='{0}'>Canvia</a><br/><br/>""".format(change_url)

	return send_mailgun(to, "Canvi de contrasenya", html)

def send_about_talk(to, taller, html):
	return send_mailgun(to, "FW15 - %s" % taller.nom, html)

def send_mailgun(list_to_send, subject, html):
	if not isinstance(list_to_send, list):
		list_to_send = [list_to_send]

	responses = [requests.post(
		"%s/messages" % MAIL_FW_API_URL,
		auth=("api", MAIL_FW_KEY),
		data={"from": "Frikiweek <%s>" % MAIL_FW_ADDR,
			  "to": to,
			  "subject": subject,
			  "html": html}) for to in list_to_send]

	if len(responses) == 1:
		return responses[0]
	else:
		return responses