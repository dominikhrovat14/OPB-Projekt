import pandas as pd
# podatke sem pridobila s pomočjo Apify Web Scraper v obliki json dat, vendar kot takšni še niso uporabni.

# v opisih knjig in avtorjev imamo še ostanke html-ja, pobrišemo vse značke in nove vrstice
def ocisti(str):
    str.replace('><', ' ')
    novi_niz = ''
    v_znacki = False
    for znak in str:
        if znak != "<" and znak != ">" and v_znacki == False:
            novi_niz += znak
        if znak == "<":
            v_znacki = True
        if znak == ">":
            v_znacki = False
    novi_niz.replace('\n', '')
    return novi_niz

# pretvorimo datume v format YYYY-MM-DD
slovar_mesecev = {'January' : '01', 
                  'February': '02', 
                  'March' : '03', 
                  'April' :'04', 
                  'May' : '05', 
                  'June' : '06', 
                  'July' : '07', 
                  'August' : '08', 
                  'September' : '09', 
                  'October' : '10', 
                  'November' : '11', 
                  'December' : '12'}

def convertDate(str):
    str_sez = str.replace(',', '').split(' ')
    stevilo = str_sez[1]
    date = str_sez[2] + '-' + slovar_mesecev[str_sez[0]] + '-'
    if len(stevilo) == 1:
        date += '0' + stevilo
    else:
        date += stevilo
    return date

dir = 'C:\\Users\\Milka\\Documents\\OPB_okt\\goodreads_neobdelani\\dataset_goodreads.json'
with open(dir, encoding='utf-8') as inputfile:
    df = pd.read_json(inputfile)

df['authorAbout'] = df['authorAbout'].map(lambda x: ocisti(x)) 
df['description'] = df['description'].map(lambda x: ocisti(x)) 
df['firstPublishedDate'] = df['firstPublishedDate'].map(lambda x: convertDate(x))
df.sort_values("bookId", ascending=False)

# dobimo csv ločen s ; 
df.to_csv('data_set_goodreads.csv',';' ,encoding='utf-8', index=False)

# v csv datoteki zanri imamo še navedene žanre
# odprimo oba DF in ju združimo v eno datoteko:
dir_data = 'C:\\Users\\Milka\\Documents\\OPB_okt\\data_set_goodreads.csv'
dir_zanri = 'C:\\Users\\Milka\\Documents\\OPB_okt\\zanri.csv'
goodreads_DF = pd.read_csv(dir_data, ";").sort_values("bookId", ascending=False)
goodreads_zanri = pd.read_csv(dir_zanri, ";")

alldata = pd.merge(goodreads_DF, goodreads_zanri, on='bookId', how='inner')
## sedaj izvozimo celo tabelo v nov csv:
alldata.to_csv('data_goodreads.csv',';' ,encoding='utf-8', index=False)
