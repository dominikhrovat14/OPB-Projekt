# OPB-Projekt- Knjižni črviček
Projektna naloga pri predmetu Osnove podatkovnih baz
Avtorja: Dominik Hrovat, Milka Gruber

## Opis

Aplikacija je zamišljena kot spletna platforma za izmenjavo knjig in informacij o njih. Uporabnik si lahko knjige izposodi od drugih uporabnikov ali pa jih sam posoja.
Baza že hrani podatke o nekaterih knjigah in avtorjih, med njimi so opisi, žanri ter (že dodeljene) ocene posameznih knjig.

## Funkcionalnosti

- **Zavihek "Avtorji"**: Tukaj lahko uporabnik brska po avtorjih knjig iz baze. Če klikne na avtorja, se izpiše avtorjev življenjepis in seznam njegovih ostalih del.

- **Zavihek "Brskaj"**: Uporabnik lahko v tem zavihku dostopa do celotnega seznama knjig v bazi. Brska lahko z vnosom imena knjige ali avtorja, lahko
  pa tudi nastavi časovno obdobje v katerem je bila knjiga izdana. Poleg tega lahko uporabnik po imenu knjige ali avtorja išče tudi z uporabo nadomestnih znakov \*, kar omogoča širše iskanje z vzorci: primer Avtor: "James\*" vrne vse knjige katerih avtor se imenuje James.

- **Zavihek "Napredno iskanje"**: Vsaka knjiga v bazi ima pripisane določene vsebinske lastnosti. Uporabnik lahko izbere lastnosti, po katerih išče ujemanje. Aplikacija vrne knjige, ki se najbolj ujemajo z željenimi lastnostmi. 

- **Stran knjige**: Če uporabnik klikne na knjigo, se prikaže stran, na kateri lahko pusti komentar o knjigi ali pa knjigo ponudi na izposojo drugim uporabnikom.
  Na dnu strani je prikazan seznam vseh uporabnikov, ki dano knjigo izposojajo.

- **Zavihek "Profil"**: Uporabnik vidi svoje osebne podatke in seznam knjig, ki jih izposoja.

- **Zavihek "Zgodovina izposoj"**: Uporabnik spremlja status svojih izposojenih knjig in tam lahko tudi knjigo vrne lastniku.


[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/dominikhrovat14/OPB-Projekt/main?urlpath=proxy%2F8080)
