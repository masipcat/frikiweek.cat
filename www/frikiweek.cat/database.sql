CREATE TABLE IF NOT EXISTS taller (
	id INTEGER PRIMARY KEY AUTO_INCREMENT,
	nom VARCHAR(20),
	descripcio VARCHAR (200),
	data DATETIME,
	duracio REAL,
	id_ponent INTEGER
);

CREATE TABLE IF NOT EXISTS usuaris (
	id INTEGER PRIMARY KEY AUTO_INCREMENT,
	contrasenya VARCHAR(40),
	nom VARCHAR(40),
	correu VARCHAR(254) UNIQUE,
	dataRegistre DATETIME,
	confirmacio VARCHAR(40),
	permisos INTEGER,
);

CREATE TABLE IF NOT EXISTS inscripcio (
	id_usuari INTEGER REFERENCES usuaris(id),
	id_taller INTEGER REFERENCES taller(id),
	data DATETIME,
	PRIMARY KEY(id_usuari, id_taller)
);

CREATE TRIGGER IF NOT EXISTS auto_increment_permisos_1
    BEFORE INSERT ON taller
    FOR EACH ROW
    WHEN New.id_ponent IS NOT NULL
    BEGIN
        UPDATE usuaris set permisos = 1 WHERE id = New.id_ponent;
    END;

CREATE TRIGGER IF NOT EXISTS auto_increment_permisos_2
    BEFORE UPDATE ON taller
    FOR EACH ROW
    WHEN New.id_ponent <> Old.id_ponent
    BEGIN
        UPDATE usuaris set permisos = 1 WHERE id = New.id_ponent;
    END;
