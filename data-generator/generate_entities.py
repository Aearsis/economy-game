import sqlite3
from shutil import copyfile

copyfile("db_empty_entities.sqlite3", "db_created_entities.sqlite3")
conn = sqlite3.connect("db_created_entities.sqlite3")

from settings import *

# table entity is created by this command:
"""
CREATE TABLE "core_entity" (
	"id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
	"name" varchar(128) NOT NULL, 
	"units" varchar(128) NOT NULL, 
	"licence_id" integer NULL REFERENCES "core_entity" ("id"),
	"is_licence" bool NOT NULL, 
	"is_strategic" bool NOT NULL);
"""

# TODO: pro jednoduchost má všechno jednotky kusy. Až bude konečná herní
# verze surovin, tak se může šáhnout do databáze ručně přes webové rozhraní a předělat kusy na
# něco jiného. To samé s důležitými surovinami.
def insert_entity(e):
	return """INSERT INTO "core_entity"("name","units","licence_id","is_licence","is_strategic")
	VALUES("%s", "ks", NULL, 0, 0);""" % e


def insert_licensed_pair(licence, licenced_entities):
	pass

for e in normal:
	conn.execute(insert_entity(e))

conn.commit()
conn.close()

