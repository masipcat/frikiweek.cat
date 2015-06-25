#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, redirect, url_for, send_from_directory, make_response, render_template, session
from flask.ext.session import Session
from fw_subscribe import fw_subs_blueprint
from werkzeug import secure_filename
from utiles import *
import json, datetime, sys

reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
app.register_blueprint(fw_subs_blueprint)

DB_SERVER = "10.131.153.116"

SESSION_TYPE = 'redis'
app.config.from_object(__name__)
Session(app)

@app.route('/')
def redirection():
	return beta()

@app.route('/github')
def github():
	return redirect("http://github.com/masipcat/frikiweek.cat")

@app.route('/beta')
def beta():
	nav = getNavigation()
	return render_template("index.html", container=nav, navigation=nav)

@app.route('/robots.txt')
def robots():
	return app.send_static_file("robots.txt")

@app.route('/humans.txt')
def humans():
	return app.send_static_file("humans.txt")

@app.route('/sitemap.xml')
def sitemap():
	nav = getNavigation()

	for item in nav:
		item["lastmod"] = datetime.datetime.now().strftime("%Y-%m-%d")

	return render_template("sitemap.xml", map=nav)

def getNavigation():
	with app.open_resource('templates/tallers.html', 'r') as f:
		tallers = unicode(f.read(), 'utf-8')

	c1 = u"""<h2>Benvinguts a la 5a edició de la FW!</h2>
			<p>La FW és una iniciativa nascuda dels estudiants del Grau en Enginyeria de Sistemes TIC, que <strong>té com a objectiu intercanviar coneixements, relacionats amb les TIC, entre estudiants i interessats</strong>.</p> <p>La FW se celebra la setmana posterior als exàmens finals dels estudiants de TIC. És a dir, la última setmana de juny (vés a les <a href="#activitats">activitats</a> per a més informació). Aquí trobareu tota la informació sobre aquest esdeveniment que des del 2011 es celebra a l'<strong>Escola Politècnica Superior d'Enginyeria de Manresa</strong> (EPSEM, UPC). </p>
			<p>Tot seguit trobareu a l'apartat <a href="#activitats">activitats</a> un llistat provisional de les activitats que es realitzaran enguany, però si vols que t'avisem quan obrim les inscripcions (gratuïtes, excepte la paella), deixa el teu correu electrònic per no perdre't cap activitat!</p>"""
	c2 = u"""<p>Enguany, la FW'15 serà del dia <strong>29 de juny al 3 de juliol</strong>, on acabarem la setmana d'activitats amb la tradicional paella.</p>
			<p>Per fi tenim la llista definitiva d'activitats! <strong>Apunta't ara, només tardaràs un minut!</strong> Per fer-ho, vés a l'<a href="/login">*apuntador</a> d'activitats.</p>
			<ul>{0}</ul>
			<p><strong>Si no et vols perdre cap correu subscriu-te</strong> i t'avisarem quan ho tinguem tot ben programat.
			Si tens qualsevol dubte, envia'ns un correu a <strong>info[ensaimada]frikiweek.cat</strong>.</p>""".format(tallers)
	#c3 = u"""<p><strong>Les dates definitives de l'esdeveniment encara no s'han fixat,</strong> però us podem avançar una data aproximada.</p>
	#		<p>Cada any la FW es celebra una setmana després dels examens finals, de manera que es celebrarà entre l'última setmana de juny i la primera de juliol</p>"""
	c4 = u"""<p>La <strong>FrikiWeek</strong> va néixer l'estiu de l'any 2011 de la mà dels primers estudiants de l'<strong>Enginyeria de Sistemes TIC</strong> (troba més informació sobre el grau a <a href="http://itic.cat">itic.cat</a>), amb el suport dels professors del grau.</p>
			 <p>Any rere any, els estudiants han continuat realitzant activitats per compartir els seus coneixements amb altres estudiants, de l'escola o de fora, i gent interessada en les tecnologies.</p>
			 <p>Pots consultar les edicions anteriors a la <a href="http://wiki.itic.cat/UniversitatEstiu/">wiki d'itic</a>!</p>"""
	#c5 = u"""<script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=false"></script><div style="overflow:hidden;"><div id="gmap_canvas" style="height:300px;width:100% !important;"></div><style>#gmap_canvas img{max-width:none!important;background:none!important}</style></div><script type="text/javascript"> function init_map(){var myOptions = {zoom:17,center:new google.maps.LatLng(41.7368466,1.8284403999999768),mapTypeId: google.maps.MapTypeId.ROADMAP};map = new google.maps.Map(document.getElementById("gmap_canvas"), myOptions);marker = new google.maps.Marker({map: map,position: new google.maps.LatLng(41.7368466, 1.8284403999999768)});infowindow = new google.maps.InfoWindow({content:"<b>Escola Polit&egrave;cnica Superior d&rsquo;Enginyeria de Manresa</b><br/>Av. de les Bases de Manresa 61<br/> Manresa" });google.maps.event.addListener(marker, "click", function(){infowindow.open(map,marker);});}google.maps.event.addDomListener(window, 'load', init_map);</script>"""

	nav = [\
		{"id": "inici", "type": u"text", "title": "inici", u"content": c1},\
		{"id": "activitats", "type": u"text", "title": u"activitats", "content": c2, "img": "/static/images/arduino.jpg"},\
		#{"id": "calendari", "type": u"text", "title": u"calendari", "content": c3, "img": "/static/images/calendar.jpg"},\
		#{"id": "trobans", "type": u"text", "title": u"", "content": c5}, \
		{"id": "historia", "type": u"text", "title": u"història", "content": c4, "img": "/static/images/historia.jpg"}]

	return nav

def getBlockContentWithContent(content):
	block = "{% extends 'index.html' %}\n{% block content %}{0}{% endif %}\n{% endblock %}"
	return block.format(content)

if __name__ == '__main__':
	DB_SERVER = "d2.frikiweek.cat"
	app.debug = True
	app.run()
