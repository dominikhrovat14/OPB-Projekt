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
      + " avtor_id INTEGER PRIMARY KEY, "
      + " ime_avtor TEXT NOT NULL, "
      + " zivljenjepis TEXT NOT NULL); ")

# Kreiranje tabele knjiga
cur.execute("CREATE TABLE knjiga ( "
      + " id INTEGER PRIMARY KEY, "
      + " naslov TEXT NOT NULL, "
      + " naslov_orig TEXT, "
      + " ISBN TEXT, "
      + " ocena DECIMAL NOT NULL DEFAULT 0, "
      + " stevilo_ocen INTEGER NOT NULL DEFAULT 0, "
      + " leto_izdaje DATE, "
      + " avtor_id INTEGER NOT NULL REFERENCES avtor(avtor_id), "
      + " opis TEXT, "
      + " jezik TEXT NOT NULL); ")

# kreiranje tabele izposoja

cur.execute("CREATE TABLE lastnosti ( "
      + " book_id INTEGER NOT NULL , "
      + " v_z INTEGER , "
      + " z_r INTEGER , "
      + " p_s INTEGER , "
      + " p_n INTEGER , "
      + " d_p INTEGER , "
      + " n_n INTEGER , "
      + " o_c INTEGER , "
      + " o_n INTEGER , "
      + " l_z INTEGER , "
      + " PRIMARY KEY (book_id), "
      + " FOREIGN KEY (book_id) REFERENCES knjiga(id), "
      + " CHECK (v_z >= 0), "
      + " CHECK (v_z <= 100), "
      + " CHECK (z_r >= 0), "
      + " CHECK (z_r <= 100), "
      + " CHECK (p_s >= 0), "
      + " CHECK (p_s <= 100), "
      + " CHECK (p_n >= 0), "
      + " CHECK (p_n <= 100), "
      + " CHECK (d_p >= 0), "
      + " CHECK (d_p <= 100), "
      + " CHECK (n_n >= 0), "
      + " CHECK (n_n <= 100), "
      + " CHECK (o_c >= 0), "
      + " CHECK (o_c <= 100), "
      + " CHECK (o_n >= 0), "
      + " CHECK (o_n <= 100), "
      + " CHECK (l_z >= 0), "
      + " CHECK (l_z <= 100) ); ")

cur.execute("CREATE TABLE nagrade ( "
      + " book_id INTEGER NOT NULL, "
      + " nagrada TEXT, "
      + " FOREIGN KEY (book_id) REFERENCES knjiga(id) ); ")

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
      + " book_id INTEGER NOT NULL, "
      + " zanr TEXT, "
      + " FOREIGN KEY (book_id) REFERENCES knjiga(id) ); ")

cur.execute("CREATE TABLE liki ( "
      + " book_id INTEGER NOT NULL, "
      + " lik TEXT, "
      + " FOREIGN KEY (book_id) REFERENCES knjiga(id) ); ")

print("KONČANO BREZ NAPAK")
