#Uvoz Bottla, knjižnica za izdelavo spletne strani
from re import TEMPLATE
from bottleext import *

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
        SELECT id, naslov, avtor_id, ocena, stevilo_ocen, EXTRACT('year' FROM leto_izdaje), jezik FROM knjiga ORDER BY EXTRACT('year' FROM leto_izdaje)
    """)
    knjige = cur.fetchall()

    query = """
     SELECT DISTINCT EXTRACT('year' FROM leto_izdaje) as leto_izdaje FROM knjiga ORDER BY leto_izdaje
     """

    filterYearKnjige = cur.execute(query)
    filterYearKnjige = cur.fetchall()

    results=[]
    for item in filterYearKnjige:
        results.append(item[0])
    
    return template('brskalnik.html', napaka=napaka, knjige = knjige, filterYearKnjige = results, noMenu='false')


@post('/brskalnik')
def brskalnik():

    name = request.forms.name + ""
    year = request.forms.year
    oseba = preveriUporabnika()
    napaka = nastaviSporocilo()

    query = """SELECT id, naslov, avtor_id, ocena, stevilo_ocen, EXTRACT('year' FROM leto_izdaje) as leto_izdaje, jezik FROM knjiga """

    appendWhere = False

    dolzina = len(name)

    if dolzina > 0:
        query += " WHERE naslov = "+ " '"+ name +"' "
        appendWhere = True
    
##    if len(name) > 0:
##        query += " WHERE name= "+name
##        appendWhere = True

    if year != 'all':
        if appendWhere:
            query += " AND  EXTRACT('year' FROM leto_izdaje) = "+ year
        else:
            appendWhere = True
            query += " WHERE EXTRACT('year' FROM leto_izdaje) = "+ year

    knjige = cur.execute(query)
    knjige = cur.fetchall()

    
    filterYearKnjige = cur.execute("""
     SELECT DISTINCT EXTRACT('year' FROM leto_izdaje) as leto_izdaje FROM knjiga ORDER BY leto_izdaje
     """)
    filterYearKnjige = cur.fetchall()
    results=[]
    for item in filterYearKnjige:
        results.append(item[0])
    
    return template('brskalnik.html', napaka=napaka, knjige = knjige, filterYearKnjige = results, noMenu='false')




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
