#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, redirect, url_for, send_from_directory, make_response, render_template
from werkzeug import secure_filename
from utiles import *
import os, json

app = Flask(__name__)

@app.route('/')
def redirection():
	return beta()

@app.route('/beta')
def beta():
	c1 = u"""<h2>Benvinguts al lloc web de la FrikiWeek!</h2>
			<!--<img src="static/images/today.png" class="thumb" />-->
			<p>Aquí trobareu tota la informació sobre aquest esdeveniment que des de fa quatre anys es celebra a l'Escola Politècnica Superior de Enginyeria de Manresa (EPSEM). Quasi bé hem acabat d'enllestir el calendari de tallers, però mentre no publiquem la llista definitva, us animem a deixar el vostre correu electrònic per què no us perdeu cap activitat!</p>
			<p>Si vols més informació sobre la FW, <strong>dona'ns el teu correu electrònic i et farem arribar les novetats</strong> (prometem no enviar-te gaires correus).</p>"""
	c2 = u"""<p>Enguany, la FW'15 serà del dia <strong>29 de juny al 3 de juliol</strong>, on acabarem la setmana d'activitats amb la tradicional paella.</p>
<p><em>La llista d'activitats estarà fixada durant els pròxims dies. Si estàs interessat en conèixer quines activitats es realitzaran, deixa'ns al teu correu electrònic.</em></p>"""
	c3 = u"""<p><strong>Les dates definitives de l'esdeveniment encara no s'han fixat,</strong> però us podem avançar una data aproximada.</p>
			<p>Cada any la FW es celebra una setmana després dels examens finals, de manera que es celebrarà entre la última setmana de juny i la primera de juliol</p>"""
	c4 = u"""<p>La <strong>FrikiWeek</strong> va néixer l'estiu de l'any 2011 de la mà dels primers estudiants de l'<strong>Enginyeria de Sistemes TIC</strong> (troba més informació sobre el grau a <a href="http://itic.cat">itic.cat</a>), amb el recolzament dels professors del grau.</p><p>Any rere any, els estudiants han continuat realitzant activitats per compartir els seus coneixaments amb altres estudiants, de l'escola o de fora.</p>"""

	nav = [\
		{"id": "inici", "type": u"text", "title": "inici", u"content": c1},\
		{"id": "activitats", "type": u"text", "title": u"activitats", "content": c2, "img": "/static/images/arduino.jpg"},\
		{"id": "calendari", "type": u"text", "title": u"calendari", "content": c3, "img": "/static/images/calendar.jpg"},\
		{"id": "historia", "type": u"text", "title": u"història", "content": c4, "img": "/static/images/historia.jpg"}]
	
	return render_template("index.html", container=nav, navigation=nav)

@app.route('/robots.txt')
def robots():
	return app.send_static_file("robots.txt")

@app.route('/humans.txt')
def humans():
	return app.send_static_file("humans.txt")

def getBlockContentWithContent(content):
	block = "{% extends 'index.html' %}\n{% block content %}{0}{% endif %}\n{% endblock %}"
	return block.format(content)

if __name__ == '__main__':
	app.debug = True
	app.run()
