#Uvoz Bottla, knjižnica za izdelavo spletne strani
from re import TEMPLATE
from bottleext import *
import logging
from logging.handlers import RotatingFileHandler

#Uvoz podatkov za povezavo
import auth as auth

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
DB_PORT = os.environ.get('POSTGRES_PORT', 443)
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
        SELECT a.ime_avtor as avtor, k.naslov as naslov, k.avtor_id as avtor_id,
        k.stevilo_ocen as stevilo_ocen, k.opis as opis, EXTRACT('year' FROM k.leto_izdaje) as leto, k.jezik as jezik 
        FROM knjiga k
        LEFT JOIN avtor a ON a.avtor_id = k.avtor_id
        WHERE k.id = """ + book_id)
    knjiga_info = cur.fetchall()

    cur.execute("""
        SELECT k.opis
        FROM knjiga k
        WHERE k.id = %s""", (book_id,))
    opis_info = cur.fetchone()
    opis = opis_info['opis'] if opis_info else 'Ta knjiga nima opisa.'

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
    oseba = preveriUporabnika()
    objave = cur.execute("""
        SELECT DISTINCT o.id as id, CONCAT(u.ime, ' ', u.priimek) AS full_name, u.id as lastnik_id
        FROM objava o LEFT JOIN uporabnik u ON o.uporabnik_id = u.id
        LEFT JOIN izposoja i ON i.objava_id = o.id
        LEFT JOIN uporabnik u2 ON i.lastnik_id = u2.id
        WHERE o.book_id = %s AND o.uporabnik_id != %s AND (i.status = True OR i.status IS NULL) AND o.available = True""",(book_id, oseba[0],))
    objave = cur.fetchall()

    zanri = cur.execute("""
        SELECT z.zanr
        FROM zanri z
        WHERE z.book_id = """ + book_id)
    zanri = cur.fetchall()
    zanri_string = ', '.join(zanr[0] for zanr in zanri)
    
    
    print(objave)

    return template('knjiga.html', napaka=napaka, oseba_id = oseba[0], book_id = book_id, objave = objave, knjiga_info = knjiga_info, knjiga_lastnosti = knjiga_lastnosti, knjige_komentarji = knjige_komentarji, zanri=zanri_string, opis=opis, noMenu='false')

def prikaziAvtorja(napaka, avtor_id):
    print(f"Fetching details for avtor_id: {avtor_id}")  # Debugging line
    # Database queries and logic to fetch author details
    cur.execute("SELECT avtor_id, ime_avtor, zivljenjepis FROM avtor WHERE avtor_id = %s", (avtor_id,))
    avtor_info = cur.fetchall()

    # Fetch the list of books by this author
    cur.execute("SELECT id, naslov, naslov_orig, leto_izdaje, ocena, jezik FROM knjiga WHERE avtor_id = %s", (avtor_id,))
    knjige_avtorja = cur.fetchall()

    return template('o_avtorju.html', napaka=napaka, avtor_info=avtor_info, knjige_avtorja=knjige_avtorja, noMenu='false')

#_______________________________________________________________________________________________________________________
# funkcija za primerjavo knjig - NOVO

def euclidean_distance(book1, book2, attributes):
    distance = 0
    for attr in attributes:
        distance += (book1.get(attr, 0) - book2.get(attr, 0)) ** 2
    return distance ** (1/2)

def find_most_similar_books(user_data, books_db, threshold=50):
    if not user_data:
            # Return an empty list if user_data is empty
            return []

    attributes = list(user_data.keys())
    similar_books = []

    for book in books_db:
        book_attributes = {key: book[key] for key in attributes if key in book}
        distance = euclidean_distance(user_data, book_attributes, attributes)
        
        if distance < threshold:
            similar_books.append(book['book_id'])
    
    # Return the list of book IDs
    return similar_books



def fetch_books_from_db():
    # Use the existing global connection and cursor
    global conn
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Define the SQL query to fetch attributes
    query = """
    SELECT book_id, vesela, zabavna, prijetna, predvidljiva, domisljijska, cudovita, optimisticna, neeroticna, lahkotna
    FROM lastnosti
    """
    
    # Execute the query
    cur.execute(query)
    
    # Fetch all rows from the executed query
    rows = cur.fetchall()
    
    # Convert rows to a dictionary with book_id as the key
    book_dict = {
        row['book_id']: {
            'vesela': row['vesela'],
            'zabavna': row['zabavna'],
            'prijetna': row['prijetna'],
            'predvidljiva': row['predvidljiva'],
            'domisljijska': row['domisljijska'],
            'cudovita': row['cudovita'],
            'optimisticna': row['optimisticna'],
            'neeroticna': row['neeroticna'],
            'lahkotna': row['lahkotna'],
            'dolzina': row['dolzina'],
        }
        for row in rows
    }
    
    # Close the cursor and return the result
    cur.close()
    return book_dict
#_______________________________________________________________________________________________________________________
# NOVO

# Mapa za statične vire (slike, css, ...)
static_dir = "./static"

skrivnost = "rODX3ulHw3ZYRdbIVcp1IfJTDn8iQTH6TFaNBgrSkjIulr"

@route("/static/<filename:path>")
def static(filename):
    return static_file(filename, root=static_dir)



def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # Nastavite CORS zaglavja za vsak odgovor
        response.headers['Access-Control-Allow-Origin'] = '*'  # Ali določite določeno domeno namesto '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
        
        if request.method == 'OPTIONS':
            return {}  # Prazno telo za OPTIONS preflight zahteve
        return fn(*args, **kwargs)
    return _enable_cors

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
    

    #Moje objave

    objave =cur.execute("""SELECT o.id as id, i.id as izposoja_id,  k.naslov AS naslov, a.ime_avtor as ime_avtor, CONCAT(u.ime, ' ', u.priimek) AS full_name, i.status AS status FROM objava o
                LEFT JOIN izposoja i ON i.objava_id = o.id
                LEFT JOIN knjiga k ON o.book_id = k.id
                LEFT JOIN avtor a ON a.avtor_id = k.avtor_id
                LEFT JOIN uporabnik u ON u.id = i.uporabnik_id
                WHERE o.uporabnik_id=%s""", (oseba[0], ))
    objave = cur.fetchall()

    credit =cur.execute("""SELECT credit FROM uporabnik
                WHERE id=%s""", (oseba[0], ))
    credit = cur.fetchone()

    sporocilo = ''
    return template('uporabnik.html', credit = credit[0], objave = objave, oseba=oseba,napaka=napaka, sporocilo=sporocilo,noMenu='false')

    
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
# NAPREDNO ISKANJE - NOVO
@get('/napredno_iskanje')
def napredno_iskanje_get():
    napaka = nastaviSporocilo()
    similar_books = []  # Default to an empty list
    oseba = preveriUporabnika()
    # Here, you can initialize any data needed for the advanced search page
    # For example, options for dropdowns, etc.
    return template('napredno_iskanje.html', napaka=napaka, noMenu='false',similar_books=similar_books)

@post('/napredno_iskanje')
def napredno_iskanje_post():
    napaka = nastaviSporocilo()

    # Initialize user_data as an empty dictionary
    user_data = {}

    # List of slider names
    sliders = ['vesela', 'zabavna', 'prijetna', 'predvidljiva', 'domisljijska', 'cudovita', 'optimisticna', 'neeroticna', 'lahkotna']

    # Iterate through sliders and check if each is active
    for slider in sliders:
        # Get the compare button status
        compare_status = request.forms.get(f'compare_{slider}', 'false') == 'true'
        
        # Only include in user_data if compare button is active
        if compare_status:
            # Retrieve the slider value
            slider_value = request.forms.get(slider, 50)
            user_data[slider] = int(slider_value)
    
    # Print or process the data as needed
    print("User data received from sliders:", user_data)

    cur.execute("""
        SELECT book_id, vesela, zabavna, prijetna, predvidljiva, domisljijska, cudovita,
               optimisticna, neeroticna, lahkotna
        FROM lastnosti
    """)
    books_db = cur.fetchall()

    books_db = [
        {
            'book_id': row['book_id'],
            'vesela': row['vesela'],
            'zabavna': row['zabavna'],
            'prijetna': row['prijetna'],
            'predvidljiva': row['predvidljiva'],
            'domisljijska': row['domisljijska'],
            'cudovita': row['cudovita'],
            'optimisticna': row['optimisticna'],
            'neeroticna': row['neeroticna'],
            'lahkotna': row['lahkotna']
        }
        for row in books_db
    ]

    similar_books_ids = find_most_similar_books(user_data, books_db, threshold=25)
    # print("Podobne knjige:", similar_books_ids) 
    
    if similar_books_ids:
        similar_books_ids_placeholder = ', '.join(str(id) for id in similar_books_ids)
        
        cur.execute(f"""
            SELECT k.id as book_id, k.naslov as naslov, a.ime_avtor as avtor, k.stevilo_ocen as stevilo_ocen, EXTRACT('year' FROM k.leto_izdaje) as leto, k.jezik as jezik
            FROM knjiga k
            LEFT JOIN avtor a ON a.avtor_id = k.avtor_id
            WHERE k.id IN ({similar_books_ids_placeholder})
        """)
        similar_books = cur.fetchall()
    else:
        similar_books = []

    similar_books = [
    {
        'book_id': row['book_id'],          
        'naslov': row['naslov'],            
        'avtor': row['avtor'],             
        'stevilo_ocen': row['stevilo_ocen'],            
        'leto': row['leto'],             
        'jezik': row['jezik']              
    }
    for row in similar_books
]
    
    return template('napredno_iskanje.html', napaka=napaka, noMenu='false', similar_books=similar_books)

#NOVO
#_______________________________________________________________________________________________________________________


#___________________________________________________________________________________________________________________________
# UPORABNIKOVA IZBIRKA KNJIG
#TODO
@get('/moje_knjige')
def moje_knjige_get():
    napaka = nastaviSporocilo()
    oseba = preveriUporabnika()
    cur.execute("""SELECT o.id as objava_id, i.id as id, i.status as status, i.datum_izposoje as datum_izposoje, i.datum_vracila as datum_vracila, k.naslov as naslov
                    FROM izposoja i LEFT JOIN knjiga k ON i.book_id = k.id
                    LEFT JOIN objava o ON o.id = i.objava_id
                    WHERE i.uporabnik_id =%s""",(oseba[0],))
    izposoje = cur.fetchall()
    
    return template('moje_knjige.html', napaka=napaka, izposoje = izposoje, noMenu='false')

@route('/vracilo', method=['OPTIONS', 'POST'])
@enable_cors
def vracilo():
    # TODO ZAKAJ NE DELA REDIRECT 
    izposoja_id = request.json.get('id')
    objava_id = request.json.get('objava_id')
    napaka = nastaviSporocilo()
    cur.execute("""UPDATE izposoja SET status = TRUE, datum_vracila = CURRENT_DATE WHERE id = %s""", (izposoja_id,))

    cur.execute("""UPDATE objava SET available = TRUE WHERE id = %s""", (objava_id,))
    # Preusmeritev na drugo stran po uspešni obdelavi
    redirect('/moje_knjige')

@route('/izposoja', method=['OPTIONS', 'POST'])
@enable_cors
def izposoja():
    # TODO ZAKAJ NE DELA REDIRECT
    objava_id = request.json.get('id')
    lastnik_id = request.json.get('lastnik_id')
    uporabnik_id = request.json.get('uporabnik_id')
    book_id = request.json.get('book_id')
    napaka = nastaviSporocilo()

    credit =cur.execute("""SELECT credit FROM uporabnik
                WHERE id=%s""", (uporabnik_id, ))
    credit = cur.fetchone()
    print(credit[0])
    #najprej preverimo, če uporabnik se ima kredite
    if credit[0] > 0:
    
        cur.execute("""INSERT INTO izposoja (book_id, uporabnik_id, lastnik_id, status, datum_izposoje, objava_id) VALUES (%s, %s, %s, False, CURRENT_DATE, %s)""", (book_id, uporabnik_id, lastnik_id, objava_id))

        cur.execute("""UPDATE objava SET available = FALSE WHERE id = %s""", (objava_id,))

        cur.execute("""UPDATE uporabnik SET credit = %s WHERE id = %s""", (credit[0] - 1, uporabnik_id,))

        #Lastniku se kredit poveca
        credit =cur.execute("""SELECT credit FROM uporabnik
                    WHERE id=%s""", (lastnik_id, ))
        credit = cur.fetchone()
        
        cur.execute("""UPDATE uporabnik SET credit = %s WHERE id = %s""", (credit[0] + 1, lastnik_id,))
    else:
        errorString = "NAPAKA, NIMATE VEČ KREDITOV"
    


    
@post('/objavi')
def objavi():    
    book_id = request.forms.book_id
    oseba = preveriUporabnika()
    napaka = nastaviSporocilo()
    cur.execute("""INSERT INTO objava (book_id, uporabnik_id) VALUES (%s, %s)""", (book_id, oseba[0]))
    
    credit =cur.execute("""SELECT credit FROM uporabnik
                WHERE id=%s""", (oseba[0], ))
    credit = cur.fetchone()

    cur.execute("""UPDATE uporabnik SET credit = %s WHERE id = %s""", (credit[0] + 1, oseba[0],))

    templ = prikaziLastnosti(napaka, book_id)

    return templ
    
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

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s sumniki
#conn = psycopg2.connect(database=db, host='baza.fmf.uni-lj.si', user=user, password=password, port=DB_PORT)
#conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogocimo transakcije
#cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

conn = psycopg2.connect(database=auth.dbname, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) #Onemogočimo transakcije #### Za enkrat ne rabimo
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
#Požnemo strežnik
#run(host='localhost', port=SERVER_PORT, reloader=RELOADER) # reloader=True nam olajša razvoj (osveževanje sproti - razvoj)
#http://127.0.0.1:8080/
#print("http://127.0.0.1:8080/")

# poženemo strežnik na podanih vratih, npr. http://localhost:8080/
if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)
print("http://127.0.0.1:8080/")
    
