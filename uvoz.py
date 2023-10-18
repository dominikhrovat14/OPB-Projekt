import psycopg2, psycopg2.extensions, psycopg2.extras 
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

from psycopg2 import sql

import csv

from auth import *


# ____________________________________________________________________________________________________________#
filename_uporabiki = 'C:\\Users\\Milka\\Documents\\OPB_okt\\normalizirani_podatki_csv\\uporabniki.csv'

glava_uporabniki = []
podatki_uporabniki = []

with open(filename_uporabiki, 'r',encoding="utf8" ) as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=';')
    glava_uporabniki = next(csv_reader)
    for row in csv_reader:
        podatki_uporabniki.append(row)
    print(glava_uporabniki)
    print(podatki_uporabniki)

def uvozi_uporabnike(cur):
    sqlinsert = ''
    for row in podatki_uporabniki:
        print(row)
        ime = row[0]
        priimek = row[1]
        username = row[2]
        mail = row[3]
        geslo = row[4]
        rojstvo = format(row[5])
        naslov = row[6]
        sqlinsert = """INSERT INTO uporabnik (ime, priimek, username, mail, geslo, rojstvo, naslov) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cur.execute(sqlinsert, (ime, priimek, username, mail, geslo, rojstvo, naslov,))


# ____________________________________________________________________________________________________________#
filename_avtorji = 'C:\\Users\\Milka\\Documents\\OPB_okt\\normalizirani_podatki_csv\\avtor.csv'
glava_avtorji = []
podatki_avtorji = []

with open(filename_avtorji, 'r',encoding="utf8" ) as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=';')
    glava_avtorji = next(csv_reader)
    for row in csv_reader:
        podatki_avtorji.append(row)
    print(glava_avtorji)
    #print(podatki_avtorji)

def uvozi_avtorje(cur):
    sqlinsert = ''
    for row in podatki_avtorji:
        print(row)
        ime = row[0]
        zivljenjepis = row[1]
        avtorid = row[2]
        sqlinsert = """INSERT INTO avtor (avtor_id, ime_avtor, zivljenjepis) VALUES (%s, %s, %s)"""
        cur.execute(sqlinsert, (avtorid, ime, zivljenjepis,))



# ____________________________________________________________________________________________________________#
filename_knjige = 'C:\\Users\\Milka\\Documents\\OPB_okt\\normalizirani_podatki_csv\\knjiga.csv'


glava_knjige = []
podatki_knjige = []

with open(filename_knjige, 'r',encoding="utf8" ) as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=';')
    glava_knjige = next(csv_reader)
    for row in csv_reader:
        podatki_knjige.append(row)
    print(glava_knjige)
    

def uvozi_knjige(cur):
    sqlinsert = ''
    for row in podatki_knjige:
        bookId = row[0]
        isbn = row[1]
        title = row[2]
        orig_title = row[3]
        numRatings = row[4]
        rating = row[5]
        firstPublishedDate = row[6]
        description = row[7]
        language = row[8]
        authorID = row[9]
        sqlinsert = """INSERT INTO knjiga (id, naslov, naslov_orig, ISBN, ocena, stevilo_ocen, leto_izdaje, avtor_id, opis, jezik) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cur.execute(sqlinsert, (bookId, title, orig_title, isbn, rating, numRatings, firstPublishedDate, authorID, description, language,))


# ____________________________________________________________________________________________________________#
filename_lastnosti = 'C:\\Users\\Milka\\Documents\\OPB_okt\\normalizirani_podatki_csv\\lastnosti.csv'


glava_lastnosti = []
podatki_lastnosti = []

with open(filename_lastnosti, 'r',encoding="utf8" ) as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=';')
    glava_lastnosti = next(csv_reader)
    for row in csv_reader:
        podatki_lastnosti.append(row)
    print(glava_lastnosti)
    

def uvozi_lastnosti(cur):
    sqlinsert = ''
    for row in podatki_lastnosti:
        bookId = row[0]
        vz = row[1]
        zr = row[2]
        ps = row[3]
        pn = row[4]
        dp = row[5]
        nn = row[6]
        oc = row[7]
        on = row[8]
        lz = row[9]
        sqlinsert = """INSERT INTO lastnosti (book_id, v_z, z_r, p_s, p_n, d_p, n_n, o_c, o_n, l_z) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cur.execute(sqlinsert, (bookId, vz, zr, ps, pn, dp, nn, oc, on, lz,))


# ____________________________________________________________________________________________________________#
filename_nagrade = 'C:\\Users\\Milka\\Documents\\OPB_okt\\normalizirani_podatki_csv\\nagrade_normalizirane.csv'

glava_nagrade = []
podatki_nagrade = []

with open(filename_nagrade, 'r',encoding="utf8" ) as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=',')
    glava_nagrade = next(csv_reader)
    for row in csv_reader:
        if len(row) == 2:
            podatki_nagrade.append(row)
            print(row)
    print(glava_nagrade)
    print(podatki_nagrade)
    

def uvozi_nagrade(cur):
    sqlinsert = ''
    for row in podatki_nagrade:
        bookId = row[0]
        if row[1] != '[]':
            nagrada = row[1]
            sqlinsert = """INSERT INTO nagrade (book_id, nagrada) VALUES (%s, %s)"""
            cur.execute(sqlinsert, (bookId, nagrada,))

with psycopg2.connect(database=db, host=host, user=user, password=password) as con:
    cur = con.cursor()
    #uvozi_knjige(cur)
    #uvozi_uporabnike(cur)
    #uvozi_avtorje(cur)
    #uvozi_lastnosti(cur)
    uvozi_nagrade(cur)
    con.commit()


# ____________________________________________________________________________________________________________#
filename_zanri = 'C:\\Users\\Milka\\Documents\\OPB_okt\\normalizirani_podatki_csv\\zanri_normalizirani.csv'

glava_zanri = []
podatki_zanri = []

with open(filename_zanri, 'r',encoding="utf8" ) as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=',')
    glava_zanri = next(csv_reader)
    for row in csv_reader:
        if len(row) == 2:
            podatki_zanri.append(row)
            print(row)
    

def uvozi_zanre(cur):
    sqlinsert = ''
    for row in podatki_zanri:
        bookId = row[0]
        zanr = row[1]
        sqlinsert = """INSERT INTO zanri (book_id, zanr) VALUES (%s, %s)"""
        cur.execute(sqlinsert, (bookId, zanr,))


# ____________________________________________________________________________________________________________#
filename_liki = 'C:\\Users\\Milka\\Documents\\OPB_okt\\normalizirani_podatki_csv\\liki_normalizirani.csv'
glava_liki = []
podatki_liki = []

with open(filename_liki, 'r',encoding="utf8" ) as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=',')
    glava_liki = next(csv_reader)
    for row in csv_reader:
        if len(row) == 2:
            podatki_liki.append(row)
            print(row)
    

def uvozi_like(cur):
    sqlinsert = ''
    for row in podatki_liki:
        if row[1] != '[]':
            bookId = row[0]
            lik = row[1]
            sqlinsert = """INSERT INTO liki (book_id, lik) VALUES (%s, %s)"""
            cur.execute(sqlinsert, (bookId, lik,))

with psycopg2.connect(database=db, host=host, user=user, password=password) as con:
    cur = con.cursor()
    #uvozi_knjige(cur)
    #uvozi_uporabnike(cur)
    #uvozi_avtorje(cur)
    #uvozi_lastnosti(cur)
    #uvozi_nagrade(cur)
    #uvozi_zanre(cur)
    uvozi_like(cur)
    con.commit()

