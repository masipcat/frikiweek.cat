#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
import utiles
import datetime, time
from constants import *

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
	cursor.execute("SELECT id FROM usuaris WHERE correu=%s AND contrasenya=%s", (correu, utiles.sha1(HASH_KEY_PAYLOAD + contrasenya)))
	uid = cursor.fetchone()
	
	if uid:
		return (SUCCESS, uid[0])

	return (ERR_USER_INVALID_LOGIN, None)

def confirma(db, codi):
	
	"""
	Aquesta funció actulitza el camp de usuari que té la confirmació codi a NULL
	"""
	cursor = getCursor(db)
	return cursor.execute("UPDATE usuaris SET confirmacio = NULL WHERE confirmacio = %s", (codi)) > 0

class Usuari(object):

	"""
	Aquest classe representa usuari
	"""
	
	def __init__(self, db, contrasenya, nom, correu, permisos = 0):
		self.uid = None
		self.contrasenya = utiles.sha1(HASH_KEY_PAYLOAD + contrasenya)
		self.nom = nom
		self.correu = correu.lower()
		self.dataRegistre = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		self.confirmacio = utiles.sha1(str(time.time()) + correu)
		self.cursor = getCursor(db)
		self.permisos = permisos

	def insert(self):
		"""
		Aquest mètode guarda informació de usuari a la taula usuaris 
		"""
		if self.uid == None:
			self.cursor.execute("INSERT INTO usuaris (contrasenya, nom, correu, dataRegistre, confirmacio) VALUES(%s, %s, %s, %s, %s)", (self.contrasenya, self.nom, self.correu, self.dataRegistre, self.confirmacio))

	@staticmethod
	def getById(db, uid):
		cursor = getCursor(db)
		cursor.execute("SELECT * FROM usuaris WHERE id = %s", str(uid))
		r = cursor.fetchone()
		if not r:
			return None

		u = Usuari(db, r[1], r[2], r[3])
		u.dataRegistre = r[4]
		u.uid = r[0]
		u.confirmacio = r[5]
		u.permisos = r[6]
		return u

	@staticmethod
	def getByEmail(db, email):
		cursor = getCursor(db)
		cursor.execute("SELECT * FROM usuaris WHERE correu = %s", email)
		r = cursor.fetchone()
		if not r:
			return None

		u = Usuari(db, r[1], r[2], r[3])
		u.dataRegistre = r[4]
		u.uid = r[0]
		u.confirmacio = r[5]
		u.permisos = r[6]
		return u

def get_reset_password_hash_if_exists(db, email):
	"""
	Aquest funció donada BD i cadena hash retorna True is el hash és vàlid
	"""
	cursor = getCursor(db)
	cursor.execute("SELECT contrasenya FROM usuaris WHERE correu = %s", (email, ))

	try:
		return cursor.fetchone()[0]
	except:
		return None

def can_reset_password(db, password_hash):
	"""
	Aquest funció donada BD i cadena hash retorna True is el hash és vàlid
	"""
	cursor = getCursor(db)
	cursor.execute("SELECT * FROM usuaris WHERE contrasenya = %s", (password_hash, ))

	try:
		return cursor.fetchone()[0] != None
	except:
		return False

def reset_password(db, password_hash, email, passwd):
	"""
	Aquesta funció canvia la contrasenya d'usuari amb correu email si la cadena hash és vàlida
	"""
	cursor = getCursor(db)
	return cursor.execute("UPDATE usuaris SET contrasenya = %s WHERE correu = %s AND contrasenya = %s", (utiles.sha1(HASH_KEY_PAYLOAD + passwd), email, password_hash)) > 0

def getTallers(db):
	
	"""
	Aquesta funció donada BD retorna una llista de Taller's
	"""
	l = []
	cursor = getCursor(db)
	cursor.execute("SELECT * FROM taller WHERE Year(data) = Year(%s) ORDER BY data", (datetime.datetime.now().strftime('%Y-%m-%d'), ))

	for row in cursor:
		tid, nom, descripcio, data, duracio, id_ponent = row
		l.append(Taller(tid, nom, descripcio, data, duracio, id_ponent))

	return l

def getTallerById(db, id_taller):

	"""
	Aquest funció donada BD db i id_taller retorna Taller on id de taller és id_taller
	"""
	l = []
	cursor = getCursor(db)
	cursor.execute("SELECT * FROM taller WHERE id = %s", (id_taller, ))
	r = cursor.fetchone()
	if not r:
		return None

	return Taller(r[0], r[1], r[2], r[3], r[4], r[5])
	
class Taller(object):

	"""
	Aquest classe representa taller
	"""

	def __init__(self, tid, nom, descripcio, data, duracio, id_ponent):

		self.tid = tid
		self.nom = nom
		self.descripcio = descripcio
		self.data = data
		self.duracio = duracio
		self.id_ponent = id_ponent

	def getInscrits(self, db):

		"""
		Aquesta funció retorna una llista de correus que són inscrits al taller
		"""
		l = []
		cursor = getCursor(db)
		cursor.execute("SELECT u.* FROM usuaris u, inscripcio i WHERE u.id = i.id_usuari AND i.id_taller = %s", self.tid)

		for r in cursor:
			u = Usuari(db, r[1], r[2], r[3])
			u.dataRegistre = r[4]
			u.uid = r[0]
			u.confirmacio = r[5]
			u.permisos = r[6]
			l.append(u)

		return l


def getInscripcions(db, id_usuari):
	
	"""
	Aquesta funció donada BD i id_usuari retorna una llista de id's de taller
	"""
	l = []
	cursor = getCursor(db)
	cursor.execute("SELECT id_taller FROM inscripcio WHERE id_usuari = %s AND Year(data) = Year(%s)", (id_usuari, datetime.datetime.now().strftime('%Y-%m-%d')))
	for row in cursor:
		l.append(row[0])
	return l


def update_inscripcions(db, id_usuari, llista_tallers):

	"""
	Aquesta funció actulitza inscripcions de id_usuari
	"""
	cursor = getCursor(db)
	cursor.execute("DELETE FROM inscripcio WHERE id_usuari = %s AND Year(data) = Year(%s)", (id_usuari, datetime.datetime.now().strftime('%Y-%m-%d')))
	data = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	
	for id_taller in llista_tallers:
		cursor.execute("INSERT INTO inscripcio VALUES(%s, %s, %s)", (id_usuari, id_taller, data))

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
		self.cursor.execute("INSERT INTO inscripcio VALUES(%s, %s, %s)", (self.id_taller, self.id_usuari, self.data))


def llista_tallers(db):
	
	"""
	Aquesta funció donada BD db retorn una llista de tuples on cada tuple té el format (Taller, nombre de inscripcions)
	"""
	l = []
	cursor = getCursor(db)
	cursor.execute("SELECT t.*, COUNT(*) AS recompte FROM taller t INNER JOIN inscripcio i ON t.id = i.id_taller WHERE Year(t.data) = Year(%s) GROUP BY t.id ORDER BY t.data", (datetime.datetime.now().strftime('%Y-%m-%d'),))

	for row in cursor:
		tid, nom, descripcio, data, duracio, id_ponent, recompte = row
		l.append((Taller(tid, nom, descripcio, data, duracio, id_ponent), recompte))
	
	return l
