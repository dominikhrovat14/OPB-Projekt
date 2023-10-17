import pandas as pd
import numpy as np
import csv

dir_data = 'C:\\Users\\Milka\\Documents\\OPB_okt\\goodreads_obdelani\\data_goodreads.csv'
df = pd.read_csv(dir_data, ";").sort_values("bookId", ascending=False)

## NAČRTOVANJE BAZE

#____________________________________________________________________________________________________#
# tabela avtor:
# 1 authorID* | 2 authorname | 3 authorAbout
author = df[["authorName", "authorAbout"]]
# dodamo stolpec author_ID 
author['authorID'] = author.index
author_df = author.drop_duplicates("authorName")
author_df.to_csv('avtor.csv',';' ,encoding='utf-8', index=False)

#____________________________________________________________________________________________________#
# tabela knjiga:
#bookId* | ISBN | Title | OriginalTitle | numberofRatings | ratings | firstPublishedDate | Description | EditionLanguage | authorID
knjige_df_1 = df[["bookId", "ISBN", "title", "Original Title", "numberOfRatings", "rating", "firstPublishedDate", "description", "Edition Language", "authorName"]]

## sedaj želimo združiti knjige z authorID 
knjige_df_merge = pd.merge(knjige_df_1, author_df, on='authorName', how="inner")
knjige_df = knjige_df_merge[["bookId", "ISBN", "title", "Original Title", "numberOfRatings", "rating", "firstPublishedDate", "description", "Edition Language", "authorID"]]
knjige_df.to_csv('knjiga.csv',';' ,encoding='utf-8', index=False)

#____________________________________________________________________________________________________#
# tabela uporabnik:
#uporabnikID | ime | priimek | username | e-naslov | geslo | starost | naslov
# nekaj uporabnikov že imamo shranjenih


#____________________________________________________________________________________________________#
# tabela lastnosti:
# bookID | vesela-žalostna | zabavna-resna | prijetna-stresna | predvidljiva-nepredvidljiva | domišljijska-prizemljena | nenasilna-nasilna | optimistična-črnogleda | običajna-neobičajna | lahkotna-zahtevna
# generiramo naključne vrednosti
lastnosti = df[["bookId"]]
df2 = pd.DataFrame(np.random.randint(0,100,size=(655, 9)), columns=['V-Z', 'Z-R', 'P-S', 'P-N', 'D-P', 'N-N', 'O-C', 'O-N', 'L-Z'])
lastnosti_df = pd.merge(lastnosti, df2, left_index=True, right_index=True)
lastnosti_df.to_csv('lastnosti.csv',';' ,encoding='utf-8', index=False)

#____________________________________________________________________________________________________#
# tabela žanri
# bookId | žanr
zanri_df = df[["bookId", "genres"]]
# ustvarimo čisto nov CSV, normalizacijo naredimo skupaj z novim zapisom
zanri_df.to_csv('zanri.csv',';' ,encoding='utf-8', index=False)
dir_zanri = 'C:\\Users\\Milka\\Documents\\OPB_okt\\zanri.csv'

with open(dir_zanri, 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    glava = next(csv_reader)
    with open('zanri_normalizirani.csv', 'w') as new_file:
        csv_writer = csv.writer(new_file)
        csv_writer.writerow(glava)
        for vrstica in csv_reader:
            niz = vrstica[0]
            i = niz.find(';')
            id = niz[0:i]
            zanri = niz[i+1:].split('&')
            for z in zanri:
                csv_writer.writerow([id, z])
            

#____________________________________________________________________________________________________#
# tabela nagrade
# bookId | nagrada
awards_df = df[["bookId", "Literary Awards"]]
awards_df.to_csv('nagrade.csv',';' ,encoding='utf-8', index=False)
dir_nagrade = 'C:\\Users\\Milka\\Documents\\OPB_okt\\nagrade.csv'

with open(dir_nagrade, 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.reader(csv_file)
    glava = next(csv_reader)
    with open('nagrade_normalizirane.csv', 'w', encoding='utf-8') as new_file:
        csv_writer = csv.writer(new_file)
        csv_writer.writerow(glava)
        for vrstica in csv_reader:
            prvi = vrstica[0]
            i = prvi.find(';')
            ID = prvi[0:i]
            ime = prvi[i+1:]
            ostali = vrstica[1:]
            csv_writer.writerow([ID, ime]) 
            for nagrada in ostali:
                csv_writer.writerow([ID, nagrada]) 
            


#____________________________________________________________________________________________________#
# tabela komentar
# bookId | uporabnikID | komentar 
# zaenkrat prazna


#____________________________________________________________________________________________________#
# tabela liki
# bookId | character 
characters_df = df[["bookId", "Characters"]]
characters_df.to_csv('liki.csv',';' ,encoding='utf-8', index=False)
dir_liki = 'C:\\Users\\Milka\\Documents\\OPB_okt\\liki.csv'

with open(dir_liki, 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.reader(csv_file)
    glava = next(csv_reader)
    with open('liki_normalizirani.csv', 'w', encoding='utf-8') as new_file:
        csv_writer = csv.writer(new_file)
        csv_writer.writerow(glava)
        for vrstica in csv_reader:
            prvi = vrstica[0]
            i = prvi.find(';')
            ID = prvi[0:i]
            ime = prvi[i+1:]
            ostali = vrstica[1:]
            csv_writer.writerow([ID, ime]) 
            for lik in ostali:
                csv_writer.writerow([ID, lik]) 
            








