# Podobno kot bi se priklopili na sqlite:
#   import sqlite3
#   cur = sqlite3.connect('imenik.db', isolation_level=None)
# se priklopimo tudi na postgres (le da bolj na dolgo vklopimo se nekaj prakticnih razsiritev):

import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s sumniki
conn = psycopg2.connect(database='sem2023_dominikh', host='baza.fmf.uni-lj.si', user='dominikh', password='1pmlybto')
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogocimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
# Nadaljni ukazi so enaki ne glede na to, ali "cur" prihaja iz sqlite ali psycopg2 knjiznice:

###########################################
                #PRAVICE#


cur.execute("GRANT ALL ON DATABASE sem2023_dominikh TO milkag;")
cur.execute("GRANT ALL ON SCHEMA public TO milkag;")
cur.execute("GRANT ALL ON ALL TABLES IN SCHEMA public TO milkag;")
cur.execute("GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO milkag;")


#cur.execute("GRANT SELECT, UPDATE, INSERT ON DATABASE sem2023_dominikh TO javnost;")
#cur.execute("GRANT SELECT, UPDATE, INSERT ON ALL TABLES IN SCHEMA public TO javnost;")



print("PRAVICE DODANE")
###########################################



# Kreiranje tabele uporabnik
cur.execute("CREATE TABLE uporabnik ( "
      + " id SERIAL PRIMARY KEY, "
      + " ime TEXT NOT NULL, "
      + " priimek TEXT NOT NULL, "
      + " username TEXT NOT NULL UNIQUE, "
      + " geslo TEXT NOT NULL, "
      + " email TEXT NOT NULL UNIQUE, "
      + " starost INTEGER); ")

# Kreiranje tabele knjiga
cur.execute("CREATE TABLE knjiga ( "
      + " id SERIAL PRIMARY KEY, "
      + " naslov TEXT NOT NULL, "
      + " ocena DECIMAL NOT NULL DEFAULT 0, "
      + " stevilo_ocen INTEGER NOT NULL DEFAULT 0, "
      + " leto_izdaje INTEGER NOT NULL, "
      + " dolzina INTEGER NOT NULL UNIQUE, "
      + " zanr TEXT NOT NULL, "
      + " jezik TEXT NOT NULL); ")

# kreiranje tabele izposoja

cur.execute("CREATE TABLE izposoja ( "
      + " id SERIAL PRIMARY KEY, "
      + " id_knjige INTEGER NOT NULL, "
      + " id_uporabnika INTEGER NOT NULL, "
      + " datum_izposoje DATE NOT NULL, "
      + " datum_vracila DATE NOT NULL); ")

print("KONČANO BREZ NAPAK")
