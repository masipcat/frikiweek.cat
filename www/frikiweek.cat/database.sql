CREATE TABLE IF NOT EXISTS taller (
	id INTEGER PRIMARY KEY AUTO_INCREMENT,
	nom VARCHAR(20),
	descripcio VARCHAR (200),
	data DATETIME,
	duracio REAL
);

CREATE TABLE IF NOT EXISTS usuaris (
	id INTEGER PRIMARY KEY AUTO_INCREMENT,
	contrasenya VARCHAR(20),
	nom VARCHAR(10),
	correu VARCHAR(30),
	dataRegistre DATETIME
);

CREATE TABLE IF NOT EXISTS inscripcio (
	id_usuari INTEGER REFERENCES usuaris(id),
	id_taller INTEGER REFERENCES taller(id),
	data DATETIME
);
