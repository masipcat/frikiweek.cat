#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from db_constants import *

def default_structure(nom):
	salutacio = "Hola"

	if len(nom):
		salutacio = "Hola %s" % nom

	return """{0},<br/><br/>%s<br/><br/>
	T'esperem la setmana del 29!<br/><br/>
	<em>Si tens qualsevol dubte, pots escriure'ns a info@frikiweek.cat</em>""".format(salutacio)

def send_confirmation_mail(to, nom, confirm_url):
	html = default_structure(nom) % """Gràcies per registrar-te! Ara només has de clicar el següent enllaç:<br/><br/>
	<a href='{1}'>Confirmació</a><br/><br/>""".format(nom, confirm_url)
	
	return send_mailgun(to, "Confirmació de l'adreça electrònica", html)

def send_mailgun(to, subject, html):
	if isinstance(to, str):
		to = [to]

	return requests.post(
		MAIL_FW_API_URL,
		auth=("api", MAIL_FW_KEY),
		data={"from": "Frikiweek <%s>" % MAIL_FW_ADDR,
			  "to": [to],
			  "subject": subject,
			  "html": html})
