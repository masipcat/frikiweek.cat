#!/usr/bin/env python
# -*- coding: utf-8 -*-

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from db_constants import *

def send_confirmation_mail(to, nom, confirm_url):
	txt = """Hola {0},<br/><br/>
	Gràcies per registrar-te! Ara només has de clicar el següent enllaç:<br/><br/>
	<a href='{1}'>Confirmació</a><br/><br/>T'esperem la setmana del 29!""".format(nom, confirm_url)
	
	return send_mail(to, "Confirmació de l'adreça electrònica", txt)

def send_mail(to, subject, text):
	server = "smtp.frikiweek.cat"
	me = "info@frikiweek.cat"

	# Create message container - the correct MIME type is multipart/alternative.
	msg = MIMEMultipart('alternative')
	msg['Subject'] = "Link"
	msg['From'] = me
	msg['To'] = to

	# Create the body of the message (a plain-text and an HTML version).
	#text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"
	html = """\
	<html>
	  <head></head>
	  <body>
	    %s
	  </body>
	</html>
	""" % text

	# Record the MIME types of both parts - text/plain and text/html.
	#part1 = MIMEText(text, 'plain')
	part2 = MIMEText(html, 'html')

	# Attach parts into message container.
	# According to RFC 2046, the last part of a multipart message, in this case
	# the HTML message, is best and preferred.
	#msg.attach(part1)
	msg.attach(part2)

	# Send the message via local SMTP server.
	s = smtplib.SMTP(server)
	s.login(me, 'QiweiBonica')
	# sendmail function takes 3 arguments: sender's address, recipient's address
	# and message to send - here it is sent as one string.
	s.sendmail(to, me, msg.as_string())
	s.quit()
