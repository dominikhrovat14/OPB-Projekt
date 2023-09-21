import requests
from bs4 import BeautifulSoup
import re
import csv
# zapeljem se po csv-ju; vsaki vrstici dodam še seznam žanrov

file = "C:\\Users\\Milka\\Documents\\OPB_okt\\zanri_manjkajoci.csv"

def seznam_v_niz(seznam):
    niz = ''
    sez = []
    for i in seznam:
        if i not in sez:
            niz += i
            niz += "&"
        sez.append(i)
    if len(niz) != 0:
        return niz[:-1]
    else:
        return ''


with open(file, 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    glava = next(csv_reader)
    glava.append('genres')
    with open('zanri_manjkajoci_novi_zadnji.csv', 'w') as new_file:
        csv_writer = csv.writer(new_file)
        csv_writer.writerow(glava)
        for vrstica in csv_reader:
            url = vrstica[1]
            page = requests.get(url)
            soup = BeautifulSoup(page.text, "html.parser")
            zanri_seznam = re.findall(r'"https://www.goodreads.com/genres/(.*?)"', page.text)
            zanri = seznam_v_niz(zanri_seznam)
            print(zanri)
            vrstica.append(zanri)
            csv_writer.writerow(vrstica)

