#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import make_response, current_app, request
from datetime import timedelta
from functools import update_wrapper
import hashlib, re, json

ALLOWED_EXTENSIONS = set(['zip', 'jpeg', 'jpg', 'png', 'gif'])

def JSONResponse(code, msg, additional = {}):
	d = {"code": code, "msg": msg}
	for k, v in additional.items():
		d[k] = v
	r = make_response(json.dumps(d))
	r.headers["Content-Type"] = "application/json"
	return r

def sha1(s):
	return hashlib.sha1(s).hexdigest()

def getExtension(s):
	r = re.findall(r"[^/\\]+\.(\w+)$", s)
	return "" if len(r) == 0 else r[0].lower()

def getFileName(s):
	r = re.findall(r"([^/\\]+)\.\w+$", s)
	return "" if len(r) == 0 else r[0]

def isValidIdentifier(id):
	return re.match(r"[\d\w]{40}", id)

def crossdomain(origin=None, methods=None, headers=None, max_age=21600, attach_to_all=True, automatic_options=True):
	if methods is not None:
		methods = ', '.join(sorted(x.upper() for x in methods))
	
	if headers is not None and not isinstance(headers, basestring):
		headers = ', '.join(x.upper() for x in headers)
	
	if not isinstance(origin, basestring):
		origin = ', '.join(origin)
	
	if isinstance(max_age, timedelta):
		max_age = max_age.total_seconds()

	def get_methods():
		if methods is not None:
			return methods

		options_resp = current_app.make_default_options_response()
		return options_resp.headers['allow']

	def decorator(f):
		def wrapped_function(*args, **kwargs):
			if automatic_options and request.method == 'OPTIONS':
				resp = current_app.make_default_options_response()
			else:
				resp = make_response(f(*args, **kwargs))
			if not attach_to_all and request.method != 'OPTIONS':
				return resp

			h = resp.headers
			h['Access-Control-Allow-Origin'] = origin
			h['Access-Control-Allow-Methods'] = get_methods()
			h['Access-Control-Max-Age'] = str(max_age)

			if headers is not None:
				h['Access-Control-Allow-Headers'] = headers
			
			h['Access-Control-Allow-Headers'] = "accept, x-authorization" # "chapuza"
			return resp

		f.provide_automatic_options = False
		f.required_methods = ['OPTIONS']
		return update_wrapper(wrapped_function, f)
	
	return decorator
