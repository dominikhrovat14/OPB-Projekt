#Uvoz Bottla, knjižnica za izdelavo spletne strani
from re import TEMPLATE
from bottleext import *
import logging
from logging.handlers import RotatingFileHandler

# Set up logging with rotation
handler = RotatingFileHandler('application.log', maxBytes=2000, backupCount=5)
logging.basicConfig(
    handlers=[handler],
    level=logging.DEBUG
)

#Uvoz podatkov za povezavo na bazo

#Uvoz psycopg2 za priklop na bazo
import psycopg2, psycopg2.extensions, psycopg2.extras

#Uvoz knjižnice za hashiranje gesel
import hashlib


from datetime import date


# KONFIGURACIJA

#Privzete nastavitve za Bottle
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
ROOT = os.environ.get('BOTTLE_ROOT', '/') 
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)
os.getcwd()

#__________________________________________________________________________________________________________
#FUNKCIJE

#če je naslednje sporočilo prazno, izbrišemo cookie, sicer nastavimo novega (skrbimo, da sporočilo izgine)

def nastaviSporocilo(sporocilo = None):
    staro = request.get_cookie("sporocilo", secret=skrivnost)
    if sporocilo is None:
        response.delete_cookie('sporocilo', path="/")
    else:
        response.set_cookie('sporocilo', sporocilo, path="/", secret=skrivnost)
    return staro 

# preveriUporabnika pogleda, če je uporabnik prijavljen oz. njegov cookie shranjen, če ne ga ne spusti mimo

def preveriUporabnika(): 
    username = request.get_cookie("username", secret=skrivnost)
    if username:
        #cur = baza.cursor()
        oseba = None
        try: 
            cur.execute("SELECT * FROM uporabnik WHERE username = %s", (username, ))
            oseba = cur.fetchone()
        except:
            oseba = None
        if oseba: 
            return oseba
    redirect(url('prijava_get'))

def hashGesla(s):
    m = hashlib.sha256()
    m.update(s.encode("utf-8"))
    return m.hexdigest()

def prikaziLastnosti(napaka, book_id):
    knjige = cur.execute("""
        SELECT a.ime_avtor as avtor, k.naslov as naslov, k.avtor_id as avtor_id, k.ocena as ocena,
        k.stevilo_ocen as stevilo_ocen, EXTRACT('year' FROM k.leto_izdaje) as leto, k.jezik as jezik 
        FROM knjiga k
        LEFT JOIN avtor a ON a.avtor_id = k.avtor_id
        WHERE k.id = """ + book_id)
    knjiga_info = cur.fetchall()

    knjige_last = cur.execute("""
        SELECT vesela, zabavna, prijetna, predvidljiva, domisljijska, cudovita,
        optimisticna, neeroticna, lahkotna, dolzina FROM lastnosti
        WHERE book_id = """ + book_id)
    knjiga_lastnosti = cur.fetchall()

    knjige_comment = cur.execute("""
        SELECT komentar_id, uporabnik_id, komentar, ocena, refer
        FROM ocene_uporabnikov 
        WHERE book_id = """ + book_id)
    knjige_komentarji = cur.fetchall()

    return template('knjiga.html', napaka=napaka, book_id = book_id, knjiga_info = knjiga_info, knjiga_lastnosti = knjiga_lastnosti, knjige_komentarji = knjige_komentarji, noMenu='true')

def prikaziAvtorja(napaka, avtor_id):
    print(f"Fetching details for avtor_id: {avtor_id}")  # Debugging line
    # Database queries and logic to fetch author details
    cur.execute("SELECT avtor_id, ime_avtor, zivljenjepis FROM avtor WHERE avtor_id = %s", (avtor_id,))
    avtor_info = cur.fetchall()

    # Fetch the list of books by this author
    cur.execute("SELECT id, naslov, naslov_orig, leto_izdaje, ocena, jezik FROM knjiga WHERE avtor_id = %s", (avtor_id,))
    knjige_avtorja = cur.fetchall()

    return template('o_avtorju.html', napaka=napaka, avtor_info=avtor_info, knjige_avtorja=knjige_avtorja, noMenu='false')



# Mapa za statične vire (slike, css, ...)
static_dir = "./static"

skrivnost = "rODX3ulHw3ZYRdbIVcp1IfJTDn8iQTH6TFaNBgrSkjIulr"

@route("/static/<filename:path>")
def static(filename):
    return static_file(filename, root=static_dir)

#___________________________________________________________________________________________________________________________
#ZAČETNA STRAN
@get('/')
def index():
    redirect(url('zacetna_get'))

@get('/zacetna')
def zacetna_get():
    napaka = nastaviSporocilo()
    return template('zacetna.html', napaka=napaka)

#___________________________________________________________________________________________________________________________
#PRIJAVA
@get('/prijava')
def prijava_get():
    napaka = nastaviSporocilo()
    return template('prijava.html', napaka=napaka, noMenu='true')

@post('/prijava')
def prijava_post():
    username = request.forms.username
    geslo = request.forms.password
    
    if username is None or geslo is None:
        nastaviSporocilo('Uporabniško ime in geslo morata biti neprazna') 
        redirect(url('prijava_get'))   
    hgeslo = None
    try: 
        cur.execute("SELECT geslo FROM uporabnik WHERE username = %s", (username, ))
        hgeslo, = cur.fetchone()
    except:
        hgeslo = None
    if hgeslo is None:
        nastaviSporocilo('Uporabniško ime ali geslo nista ustrezni') 
        redirect(url('prijava_get'))
        return
    if geslo != hgeslo:
        nastaviSporocilo('Uporabniško ime ali geslo nista ustrezni') 
        redirect(url('prijava_get'))
        return
    response.set_cookie('username', username, path="/", secret=skrivnost)
    redirect(url('uporabnik'))


#___________________________________________________________________________________________________________________________
#ODJAVA
@get('/odjava')
def odjava_get():
    response.delete_cookie('username', path="/")
    redirect(url('prijava_get'))


#___________________________________________________________________________________________________________________________
#UPORABNIK

@get('/uporabnik')
def uporabnik():
    oseba = preveriUporabnika()
    if oseba is None: 
        return
    napaka = nastaviSporocilo()
    #cur.execute("""SELECT COUNT (*) FROM izposoja WHERE id_uporabnika=1""", (oseba[1], ))

    sporocilo = ''
    return template('uporabnik.html', oseba=oseba,napaka=napaka, sporocilo=sporocilo,noMenu='false')

    
#___________________________________________________________________________________________________________________________
# REGISTRACIJA
@get('/registracija')
def registracija_get():
    print("registracija")
    napaka = nastaviSporocilo()
    return template('registracija.html', napaka=napaka,noMenu='true')


@post('/registracija')
def registracija_post():
    username = request.forms.username
    name = request.forms.name
    surname = request.forms.surname
    email = request.forms.email
    adress = request.forms.adress
    password = request.forms.password
    password_check = request.forms.password_check
    rojstvo = request.forms.age

    #preverimo, ce je izbrani username ze zaseden
    cur.execute("SELECT * FROM uporabnik WHERE username=%s", (username,))
    upor = cur.fetchone()
    if upor is not None:
        return template("registracija.html", name=name, surname=surname, username=username,
                               email=email, napaka="Uporabniško ime je že zasedeno!", noMenu='true')

    # preverimo, ali se gesli ujemata
    if password != password_check:
        return template("registracija.html", name=name, surname=surname, username=username,
                               email=email, napaka="Gesli se ne ujemata!", noMenu='true')

    #preverimo, ce je email ze obstaja
    cur.execute("SELECT * FROM uporabnik WHERE mail=%s", (email,))
    upor = cur.fetchone()
    if upor is not None:
        return template("registracija.html", name=name, surname=surname, username=username,
                               email=email, napaka="Vnešen email že obstaja!", noMenu='true')

    cur.execute("""INSERT INTO uporabnik (ime, priimek, username, mail, geslo, rojstvo, naslov) VALUES (%s, %s, %s, %s, %s, %s, %s)""", (name,surname, username,email,password,'2021-05-20',adress, ))
    redirect(url('uporabnik'))

#___________________________________________________________________________________________________________________________
# BRSKALNIK
@get('/brskalnik')
def brskalnik_get():
    

    oseba = preveriUporabnika()
    napaka = nastaviSporocilo()

    knjige = cur.execute("""
        SELECT a.ime_avtor, k.id, k.naslov, k.avtor_id, k.ocena,
        k.stevilo_ocen, EXTRACT('year' FROM k.leto_izdaje), k.jezik, l.dolzina as dolzina
        FROM knjiga k
        LEFT JOIN avtor a ON a.avtor_id = k.avtor_id
        LEFT JOIN lastnosti l ON l.book_id = k.id
        ORDER BY EXTRACT('year' FROM k.leto_izdaje)
    """)
    knjige = cur.fetchall()

    queryYear = """
         SELECT DISTINCT EXTRACT('year' FROM leto_izdaje) as leto_izdaje FROM knjiga ORDER BY leto_izdaje
     """

    filterYearKnjige = cur.execute(queryYear)
    filterYearKnjige = cur.fetchall()

    results=[]
    for item in filterYearKnjige:
        results.append(item[0])

    queryLanguage = """
         SELECT DISTINCT jezik FROM knjiga ORDER BY jezik 
     """

    filterLanguageKnjige = cur.execute(queryLanguage)
    filterLanguageKnjige = cur.fetchall()

    resultsLanguage=[]
    for item in filterLanguageKnjige:
        if len(item[0])>0:
            resultsLanguage.append(item[0])

    
    return template('brskalnik.html', napaka=napaka, knjige = knjige, filterYearKnjige = results, filterLanguageKnjige = resultsLanguage, noMenu='false')


@post('/brskalnik')
def brskalnik():

    name = request.forms.name
    year = request.forms.year
    from_year, to_year = year.split(" - ")
    avtor = request.forms.avtor
    jezik = request.forms.language
    oseba = preveriUporabnika()
    napaka = nastaviSporocilo()

    query = """
            SELECT a.ime_avtor, k.id, k.naslov, k.avtor_id, k.ocena,
            k.stevilo_ocen, EXTRACT('year' FROM k.leto_izdaje) as leto_izdaje, k.jezik, l.dolzina as dolzina
            FROM knjiga k
            LEFT JOIN avtor a ON a.avtor_id = k.avtor_id
            LEFT JOIN lastnosti l ON l.book_id = k.id
        
            """

    appendWhere = False

    if len(name) > 0:
        if appendWhere:
            if '*' in name:
                name = name.replace('*', '%')
                query += " AND k.naslov LIKE '" + name + "'"
            else:
                query += " AND  k.naslov= '""" + name + """'"""
        else:
            appendWhere = True
            if '*' in name:
                name = name.replace('*', '%')
                query += " WHERE k.naslov LIKE '" + name + "'"
            else:
                query += " WHERE k.naslov = '""" + name + """'"""
                
    if len(avtor) > 0:
        if appendWhere:
            if '*' in avtor:
                avtor = avtor.replace('*', '%')
                query += " AND a.ime_avtor LIKE '" + avtor + "'"
            else:
                query += " AND  a.ime_avtor= '""" + avtor + """'"""
        else:
            appendWhere = True
            if '*' in avtor:
                avtor = avtor.replace('*', '%')
                query += " WHERE a.ime_avtor LIKE '" + avtor + "'"
            else:
                query += " WHERE a.ime_avtor = '""" + avtor + """'"""
    if len(jezik) > 0 and jezik != 'all':
        if appendWhere:
            query += " AND  k.jezik = '""" + jezik + """'"""
        else:
            appendWhere = True
            query += " WHERE  k.jezik = '""" + jezik + """'"""

    if len(year) > 0:
        if appendWhere:
            query += " AND  EXTRACT('year' FROM k.leto_izdaje) >= " +from_year + " AND EXTRACT('year' FROM k.leto_izdaje) <= " +to_year 
                     
        else:
            appendWhere = True
            query += " WHERE  EXTRACT('year' FROM k.leto_izdaje) >= " +from_year + " AND EXTRACT('year' FROM k.leto_izdaje) <= " +to_year 
                     

    query +=  "ORDER BY EXTRACT('year' FROM k.leto_izdaje)"
    knjige = cur.execute(query)
    knjige = cur.fetchall()

    queryYear = """
             SELECT DISTINCT EXTRACT('year' FROM leto_izdaje) as leto_izdaje FROM knjiga ORDER BY leto_izdaje
     """

    filterYearKnjige = cur.execute(queryYear)
    filterYearKnjige = cur.fetchall()

    results=[]
    for item in filterYearKnjige:
            results.append(item[0])

    queryLanguage = """
             SELECT DISTINCT jezik FROM knjiga ORDER BY jezik 
     """

    filterLanguageKnjige = cur.execute(queryLanguage)
    filterLanguageKnjige = cur.fetchall()

    resultsLanguage=[]
    for item in filterLanguageKnjige:
        if len(item[0])>0:
            resultsLanguage.append(item[0])


    return template('brskalnik.html', napaka=napaka, knjige = knjige, filterYearKnjige = results, filterLanguageKnjige = resultsLanguage, noMenu='false')
#___________________________________________________________________________________________________________________________
# O KNJIGI
#TODO
#PRIJAVA
@get('/knjiga')
def knjiga_get():
    napaka = nastaviSporocilo()
    book_id = request.query['book_id']

    templ = prikaziLastnosti(napaka, book_id)
    return templ

@post('/knjiga')
def post_comment():
    new_comment = request.forms.new_comment
    book_id = request.forms.book_id
    starRating = request.forms.starRating
    oseba = preveriUporabnika()

    napaka = nastaviSporocilo()


    cur.execute("""INSERT INTO ocene_uporabnikov (book_id, uporabnik_id, komentar, ocena) VALUES (%s, %s, %s, %s)""", (book_id, oseba[0], new_comment, starRating))
    templ = prikaziLastnosti(napaka, book_id)
    return templ
    

#_______________________________________________________________________________________________________________________
# ENA SAMA KNJIGA



#___________________________________________________________________________________________________________________________
# UPORABNIKOVA IZBIRKA KNJIG
#TODO
@get('/moje_knjige')
def moje_knjige_get():
    print("test")
    napaka = nastaviSporocilo()
    oseba = preveriUporabnika()
    id_uporabnika = oseba[0]
    k = cur.execute("""SELECT id FROM knjiga""")
                        #WHERE id_uporabnika=%s""",(id_uporabnika,))
    k = cur.fetchall()
    return template('moje_knjige.html', napaka=napaka, noMenu='false')


#___________________________________________________________________________________________________________________________
# ENA SAMA KNJIGA
# todo 
@get('/avtorji')
def avtorji():
    napaka = nastaviSporocilo()
    query = """SELECT avtor.avtor_id as avtor_id, avtor.ime_avtor as ime_avtor from avtor"""
    avtorji = cur.execute(query)
    avtorji = cur.fetchall()
    return template('avtorji.html', napaka = napaka, avtorji=avtorji, noMenu='false')
#___________________________________________________________________________________________________________________________
# O AVTORJU
@get('/avtor')
def avtor_get():
    napaka = nastaviSporocilo()
    avtor_id = request.query['avtor_id']
    print(f"Received avtor_id: {avtor_id}")  # Debugging line
    templ = prikaziAvtorja(napaka, avtor_id)
    return templ


#___________________________________________________________________________________________________________________________
#POVEZAVA NA BAZO

db="sem2023_milkag"
user="milkag"
#password="1pmlybto"
password="ljhgej43"

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s sumniki
conn = psycopg2.connect(database=db, host='baza.fmf.uni-lj.si', user=user, password=password)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogocimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

#Požnemo strežnik
run(host='localhost', port=SERVER_PORT, reloader=RELOADER) # reloader=True nam olajša razvoj (osveževanje sproti - razvoj)
#http://127.0.0.1:8080/
print("http://127.0.0.1:8080/")

    
