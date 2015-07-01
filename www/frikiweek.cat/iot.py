#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, redirect, request, url_for, session
from time import time
import requests, traceback

last_update_timestamp = 0

fw_iot_blueprint = Blueprint('fw_iot_blueprint', __name__, template_folder='templates')

def catch_exceptions(func):
	def func_wrapper(**kwarg):
		try:
			return func(**kwarg)
		except Exception as e:
			return """Alguna cosa no ha anat bé :(<br />
					  Posa't amb contacte amb info[arroba]frikiweek.cat<br />
					  <pre>%s</pre>""" % traceback.format_exc().replace("\n", "<br />")

	func_wrapper.__name__ = func.__name__
	return func_wrapper

@fw_iot_blueprint.route("/iot")
@catch_exceptions
def iot():
	return render_template("iot.html")

@fw_iot_blueprint.route("/iot/increase")
@catch_exceptions
def iot_increase():
	global last_update_timestamp
	count = increaseCount()
	now = time()
	if now - last_update_timestamp > 15: # Si han passaat més de 15 segons
		if requests.get("https://api.thingspeak.com/update?key=3EAP0MW7ZDICW6SZ&field3=%d" % count).status_code == 200:
			last_update_timestamp = time()
			return "ok! {RE} last update: %d - actual count %d" % (last_update_timestamp, count)

	return "ok! last update: %d - actual count %d" % (last_update_timestamp, count)

def increaseCount():
	try:
		count = session['iot_count']
	except KeyError:
		count = 0

	count += 1
	session['iot_count'] = count
	return count
