CREATE TABLE IF NOT EXISTS taller (
	id INTEGER PRIMARY KEY AUTO_INCREMENT,
	nom VARCHAR(20),
	descripcio VARCHAR (200),
	data DATETIME,
	duracio REAL
);

CREATE TABLE IF NOT EXISTS usuaris (
	id INTEGER PRIMARY KEY AUTO_INCREMENT,
	contrasenya VARCHAR(40),
	nom VARCHAR(40),
	correu VARCHAR(30) UNIQUE,
	dataRegistre DATETIME,
	confirmacio VARCHAR(40)
);

CREATE TABLE IF NOT EXISTS inscripcio (
	id_usuari INTEGER REFERENCES usuaris(id),
	id_taller INTEGER REFERENCES taller(id),
	data DATETIME,
	PRIMARY KEY(id_usuari, id_taller)
);
