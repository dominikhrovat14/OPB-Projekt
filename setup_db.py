# Podobno kot bi se priklopili na sqlite:
#   import sqlite3
#   cur = sqlite3.connect('imenik.db', isolation_level=None)
# se priklopimo tudi na postgres (le da bolj na dolgo vklopimo se nekaj prakticnih razsiritev):

db="sem2023_milkag"
user="milkag"
#password="1pmlybto"
password="ljhgej43"


import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s sumniki
conn = psycopg2.connect(database=db, host='baza.fmf.uni-lj.si', user=user, password=password)
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
cur.execute("CREATE TABLE avtor ( "
      + " avtor_id SERIAL PRIMARY KEY, "
      + " ime_avtor TEXT NOT NULL, "
      + " zivljenjepis TEXT NOT NULL); ")

# Kreiranje tabele knjiga
cur.execute("CREATE TABLE knjiga ( "
      + " id SERIAL PRIMARY KEY, "
      + " naslov TEXT NOT NULL, "
      + " naslov_orig TEXT, "
      + " ISBN TEXT, "
      + " ocena DECIMAL NOT NULL DEFAULT 0, "
      + " stevilo_ocen INTEGER NOT NULL DEFAULT 0, "
      + " leto_izdaje DATE, "
      + " avtor_id INTEGER NOT NULL, "
      + " opis TEXT, "
      + " jezik TEXT NOT NULL); ")

# kreiranje tabele izposoja

cur.execute("CREATE TABLE lastnosti ( "
      + " id_knjige INTEGER, "
      + " v_z INTEGER , "
      + " z_r INTEGER , "
      + " p_s INTEGER , "
      + " p_n INTEGER , "
      + " d_p INTEGER , "
      + " n_n INTEGER , "
      + " o_c INTEGER , "
      + " o_n INTEGER , "
      + " l_z INTEGER ); ")

cur.execute("CREATE TABLE nagrade ( "
      + " book_id INTEGER, "
      + " nagrada TEXT ); ")

cur.execute("CREATE TABLE uporabnik ( "
      + " id SERIAL PRIMARY KEY, "
      + " ime TEXT NOT NULL, "
      + " priimek TEXT NOT NULL, "
      + " username TEXT NOT NULL UNIQUE, "
      + " mail TEXT NOT NULL UNIQUE, "
      + " geslo TEXT NOT NULL UNIQUE, "
      + " rojstvo DATE NOT NULL, "
      + " naslov TEXT); ")

cur.execute("CREATE TABLE zanri ( "
      + " book_id INTEGER, "
      + " zanr TEXT ); ")

print("KONČANO BREZ NAPAK")
