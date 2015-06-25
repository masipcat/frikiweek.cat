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
	cursor.execute("SELECT id FROM usuaris WHERE correu=%s AND contrasenya=%s", (correu, utiles.sha1('friki' + contrasenya)))
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
        

class Usuaris(object):

	"""
	Aquest classe representa usuari
	"""
	
	def __init__(self, db, contrasenya, nom, correu):

		self.contrasenya = utiles.sha1('friki' + contrasenya)
		self.nom = nom
		self.correu = correu
                data = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		self.dataRegistre = data
                self.confirmacio = utiles.sha1(data + correu)
		self.cursor = getCursor(db)

	def save(self):
		
		"""
		Aquest mètode guarda informació de usuari a la taula usuaris 
		"""
		self.cursor.execute("INSERT INTO usuaris (contrasenya, nom, correu, dataRegistre, confirmacio) VALUES(%s, %s, %s, %s, %s)", (self.contrasenya, self.nom, self.correu, self.dataRegistre, self.confirmacio))
                return self.confirmacio


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
        for x in llista_tallers:
                cursor.execute("INSERT INTO inscripcio VALUES(%s, %s, %s)", (id_usuari, x, data))
        

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

"""
# test

db = db_connect()
confirma(db, '123')
db.commit()
"""
