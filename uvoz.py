import psycopg2, psycopg2.extensions, psycopg2.extras 
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

from psycopg2 import sql

import csv

from auth import *

filename_knjige = 'testni podatki\knjige.csv'
glava_knjige = []
podatki_knjige = []

with open(filename_knjige, 'r') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=',')
    glava_knjige = next(csv_reader)
    for row in csv_reader:
        podatki_knjige.append(row)
    #print(glava_knjige)
    podatki_knjige.pop()
    #print(podatki_knjige)

filename_opisi = 'testni podatki\\opisi_knjig.csv'
glava_opisi = []
podatki_opisi = []

with open(filename_opisi, 'r', encoding="utf8" ) as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=';')
    glava_opisi = next(csv_reader)
    for row in csv_reader:
        podatki_opisi.append(row)
    #print(glava_opisi)
    #print(podatki_opisi)

filename_uporabiki = 'testni podatki\\uporabniki.csv'
glava_uporabniki = []
podatki_uporabniki = []

with open(filename_uporabiki, 'r',encoding="utf8" ) as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=';')
    glava_uporabniki = next(csv_reader)
    for row in csv_reader:
        podatki_uporabniki.append(row)
    print(glava_uporabniki)
    print(podatki_uporabniki)

def uvozi_knjige(cur):
    sqlinsert = ''
    for row in podatki_knjige:
        #print(row)
        naslov = row[0]
        avtor = row[1]
        ocena = float(row[2])
        stevilo_ocen = int(row[3])
        leto_izdaje = int(row[4])
        dolzina = int(row[5])
        zanr = row[6]
        jezik = row[7]
        sqlinsert = """INSERT INTO knjiga (naslov, avtor, ocena, stevilo_ocen, leto_izdaje, dolzina, zanr, jezik) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        cur.execute(sqlinsert, (naslov, avtor, ocena, stevilo_ocen, leto_izdaje, dolzina, zanr, jezik,))

def uvoz_opisov(cur):
    sqlinsert = ''
    for row in podatki_opisi:
        #print(row)
        naslov = row[0]
        opis = row[1]
        sqlinsert = """INSERT INTO opisi (naslov, opis) VALUES (%s, %s)"""
        cur.execute(sqlinsert, (naslov, opis,))

def uvozi_uporabnike(cur):
    sqlinsert = ''
    for row in podatki_uporabniki:
        print(row)
        ime = row[0]
        priimek = row[1]
        username = row[2]
        email = row[3]
        geslo = row[4]
        starost = int(row[5])
        naslov = row[6]
        sqlinsert = """INSERT INTO uporabnik (ime, priimek, username, email, geslo, starost, naslov) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cur.execute(sqlinsert, (ime, priimek, username, email, geslo, starost, naslov,))



with psycopg2.connect(database=db, host=host, user=user, password=password) as con:
    cur = con.cursor()
    #uvozi_knjige(cur)
    #uvoz_opisov(cur)
    #uvozi_uporabnike(cur)
    con.commit()




