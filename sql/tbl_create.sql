/* SQL commands to create tables */

-- DROP TABLE Contain;
-- DROP TABLE Album;
-- DROP TABLE User;
-- DROP TABLE Photo;

CREATE TABLE User(
	username VARCHAR(20),
	firstname VARCHAR(20),
	lastname VARCHAR(20),
	password VARCHAR(20),
	email VARCHAR(40),
	PRIMARY KEY (username)
);

CREATE TABLE Album(
	albumid INT NOT NULL AUTO_INCREMENT,
	title VARCHAR(50),
	created DATE,
	lastupdated DATE,
	username VARCHAR(20),
	PRIMARY KEY (albumid),
	FOREIGN KEY (username) REFERENCES User(username) ON DELETE CASCADE
);

CREATE TABLE Photo(
	picid VARCHAR(40),
	format CHAR(3),  /* format is fixed-length for 3 characters */
	date DATE,
	PRIMARY KEY (picid)
);

CREATE TABLE Contain(
	albumid INT,
	picid VARCHAR(40),
	caption VARCHAR(255) DEFAULT "",
	sequencenum INT,
	PRIMARY KEY (albumid, picid),
	FOREIGN KEY (albumid) REFERENCES Album(albumid) ON DELETE CASCADE,
	FOREIGN KEY (picid) REFERENCES Photo(picid) ON DELETE CASCADE
);

CREATE TRIGGER album_created_date BEFORE INSERT
ON Album
FOR EACH ROW 
SET 
NEW.created = IFNULL(NEW.created, CURRENT_DATE),
NEW.lastupdated = IFNULL(NEW.lastupdated, CURRENT_DATE);


CREATE TRIGGER album_lastupdated_update AFTER INSERT
ON Contain
FOR EACH ROW
UPDATE Album SET Album.lastupdated = CURRENT_DATE
WHERE Album.albumid = NEW.albumid;

CREATE TRIGGER delete_pic_when_delete_album BEFORE DELETE
ON Album
FOR EACH ROW
DELETE FROM Photo WHERE picid IN (SELECT picid FROM Contain WHERE albumid=OLD.albumid);
