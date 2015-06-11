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
	c1 = u"""<h2>Benvinguts a la 5a edició de la FW!</h2>
			<p>La <strong>FW</strong> és una iniciativa nascuda dels estudiants de TIC que té com a objectiu intercanviar coneixements entre estudiants relacionats amb TIC. La FW se celebra la setmana posterior als exàmens finals dels estudiants de TIC, la última setmana de juny (vés a les <a href="#activitats">activitats</a> per a més informació). Aquí trobareu tota la informació sobre aquest esdeveniment que des del 2011 es celebra a l'<strong>Escola Politècnica Superior d'Enginyeria de Manresa</strong> (EPSEM, UPC). </p>
			<p>Tot seguit trobareu a l'apartat <a href="#activitats">activitats</a> un llistat provisional de les activitats que es realitzaran enguany, però si vols que t'avisem quan obrim les inscripcions (gratuïtes), deixa el teu correu electrònic per no perdre't cap activitat!</p>"""
	c2 = u"""<p>Enguany, la FW'15 serà del dia <strong>29 de juny al 3 de juliol</strong>, on acabarem la setmana d'activitats amb la tradicional paella.</p>
			<p><strong>La llista definitiva d'activitats estarà fixada durant els pròxims dies. Estigues atent!</strong></p>
			<ul>
				<li><strong>Introducció a la programació amb Python</strong> - per <strong>Hafid Kharbouch</strong> <em>(obert a tothom)</em></li>
				<li><strong>Taller de pàgines web dinàmiques amb Laravel (PHP)</strong> - per <strong>Èrik Campobadal</strong> <em>(requereix conèixer algun llenguatge de programació)</em></li>
				<li><strong>Taller sobre la instrumentació de laboratori</strong> - per <strong>Jordi Bonet</strong> <em>(requereix coneixements bàsics de la instrumentació de lab.)</em></li>
				<li><strong>Xerrada sobre l'IoT i taller</strong> - per <strong>Joan Martínez</strong> <em>(tots els públics)</em></li>
				<li><strong>Què és guifi.net?</strong> - per <strong>Francisco del Águila</strong> <em>(tots els públics)</em></li>
				<li><strong>Introducció a les expressions regulars (RegEx)</strong> - per <strong>Jordi Masip</strong> <em>(requereix coneixements de Python)</em></li>
			</ul>
			<p><em>i alguna sorpresa més...</em><br>
			Si tens qualsevol dubte, envie'ns un correu a <strong>info[ensaimada]frikiweek.cat</strong>.</p>"""
	c3 = u"""<p><strong>Les dates definitives de l'esdeveniment encara no s'han fixat,</strong> però us podem avançar una data aproximada.</p>
			<p>Cada any la FW es celebra una setmana després dels examens finals, de manera que es celebrarà entre l'última setmana de juny i la primera de juliol</p>"""
	c4 = u"""<p>La <strong>FrikiWeek</strong> va néixer l'estiu de l'any 2011 de la mà dels primers estudiants de l'<strong>Enginyeria de Sistemes TIC</strong> (troba més informació sobre el grau a <a href="http://itic.cat">itic.cat</a>), amb el suport dels professors del grau.</p><p>Any rere any, els estudiants han continuat realitzant activitats per compartir els seus coneixements amb altres estudiants, de l'escola o de fora.</p>
		<p>Pots consultar les edicions anteriors a la <a href="http://wiki.itic.cat/UniversitatEstiu/">wiki d'itic</a>!</p>"""

	nav = [\
		{"id": "inici", "type": u"text", "title": "inici", u"content": c1},\
		{"id": "activitats", "type": u"text", "title": u"activitats", "content": c2, "img": "/static/images/arduino.jpg"},\
		#{"id": "calendari", "type": u"text", "title": u"calendari", "content": c3, "img": "/static/images/calendar.jpg"},\
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
