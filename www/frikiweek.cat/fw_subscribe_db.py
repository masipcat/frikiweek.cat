#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
import utiles
import datetime
from constants import *

"""
* TALLER
	- ID (201501, 201502...)
	- nom
	- descripció
	- data
	- duració

* USUARIS
	- ID
	- contrasenya (en hash)
	- nom
	- correu
	- dataRegistre

* INSCRIPCIO
	- ID_taller
	- ID_usuari
	- data
"""

def db_connect():
	db = MySQLdb.connect(host=DB_SERVER, user=DB_USER, passwd=DB_PASSWD, db=DB_NAME)
	db.set_character_set('utf8')
	return db

def getCursor(db):
	dbc = db.cursor()
	dbc.execute('SET NAMES utf8;')
	dbc.execute('SET CHARACTER SET utf8;')
	dbc.execute('SET character_set_connection=utf8;')
	return dbc #db.cursor(MySQLdb.cursors.DictCursor)

def user_exist(db, correu):
	cursor = getCursor(db)
	cursor.execute("SELECT COUNT(*) FROM usuaris WHERE correu=%s", [correu])
	return cursor.fetchone()[0] > 0

def login(db, correu, contrasenya):  
	"""
	Aquesta funció donada BD, correu i contrasenya retorn id de usuari si la contrasenya es correcte, sinó ERR_USER_INVALID_LOGIN
	"""
	cursor = getCursor(db)
	cursor.execute("SELECT id FROM usuaris WHERE correu=%s AND contrasenya=%s", (correu, utiles.sha1(contrasenya)))
	uid = cursor.fetchone()[0]
	
	if uid:
		return (SUCCESS, uid)

	return (ERR_USER_INVALID_LOGIN, None)

class Usuaris(object):

	"""
	Aquest classe representa usuari
	"""
	
	def __init__(self, db, contrasenya, nom, correu):

		self.contrasenya = utiles.sha1(contrasenya)
		self.nom = nom
		self.correu = correu
		self.dataRegistre = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		self.cursor = getCursor(db)

	def save(self):
		
		"""
		Aquest mètode guarda informació de usuari a la taula usuaris 
		"""
		self.cursor.execute("INSERT INTO usuaris (contrasenya, nom, correu, dataRegistre) VALUES(?, ?, ?, ?)", (self.contrasenya, self.nom, self.correu, self.dataRegistre))


def getTallers(db):
	
	"""
	Aquesta funció donada BD retorna una llista de Taller's
	"""
	l = []
	cursor = getCursor(db)
	cursor.execute("SELECT * FROM taller WHERE Year(data) = Year(%s)", (datetime.datetime.now().strftime('%Y-%m-%d'), ))

	for row in cursor:
		tid, nom, descripcio, data, duracio = row
		l.append(Taller(tid, nom, descripcio, data, duracio))

	return l

	
class Taller(object):

	"""
	Aquest classe representa taller
	"""

	def __init__(self, tid, nom, descripcio, data, duracio):

		self.tid = tid
		self.nom = nom
		self.descripcio = descripcio
		self.data = data
		self.duracio = duracio


def getInscripcions(db, id_usuari):
	
	"""
	Aquesta funció donada BD i id_usuari retorna una llista de id's de taller
	"""
	l = []
	cursor = getCursor(db)
	cursor.execute("SELECT id_taller FROM inscripcio WHERE id_usuari = ? AND data LIKE '%?'", (id_usuari, datetime.datetime.now().strftime('%Y')))
	for row in cursor:
		l.append(row)
	return l


class Inscripcio(object):

	"""
	Aquest classe representa inscripció
	"""

	def __init__(self, db, id_taller, id_usuari):

		self.id_taller = id_taller
		self.id_usuari = id_usuari
		self.data = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		self.cursor = getCursor(db)

	def save(self):

		"""
		Aquest mètode guarda inscripció a la taula inscripcio 
		"""
		self.cursor.execute("INSERT INTO inscripcio VALUES(?, ?, ?)", (self.id_taller, self.id_usuari, self.data))

