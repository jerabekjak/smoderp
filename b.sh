# pri posteni na linux stroji se vetsina dat nacita z souboru *.save
# ten je vytvoren pomoci malicku pickle a funkce pickle.dump


# pri pousteni ze souboru *.save 
# nelze nektereme parametry menit 
# ty jsou oznaceny pomlckou zatim asi netreba popisovat

# nektere lze prevzit z *.save, ale jsou zmenit pokud das misto pomlcky promenou (havne zadavana srazka)

# nektere jsou pro linux povinne, ty jsou vyplnene a popsane


[GIS]
dem: -
soil: - 
lu: -

[shape atr]
soil-atr: -
lu-atr: -



# soubor s informaci o srazkce lze menit
# kdyz je - smoderp bere srazku ktera je 
# v *.save souboru
[srazka]
file: indata/srazka.txt
# file: -


# maximalni (a zaroven pocatecni)
# casovy krok se zde zadava 
# i konecni cas simulace se zde zadava
[time]
#sec
maxdt: 20
#min
endtime: 20


[Other]
points: -
# 
# output adresar ze zadava
# obsah adresare se na zacatku vypoctu smaze
outdir: out-test

# 
# zadava se 
# pro zousteni z arvgis je zkryt
# zatim mozna neni zajimavy...
typecomp: 0
# 
# Mfda zatim zustava false
mfda: False
soilvegtab : -
soilvegcode : -
streamshp :  -
streamtab: -
streamtabcode: -
#
# pro linux musi zustat False / false.
arcgis: false
#
# Zde si muzes nechat podrobneji 
# vypsat vypisy, hlavne otazka zapsani vysledku
extraout: true
#
# kde se zadava cesta k souboru se vstupnimi data
# indata: indata/trych01.save
indata: indata/konk01.save
#
#
# pro linux zatim jen roff - nacteni vstupnich souboru
# zadava se i jako povinna option pri spusteni skriptU
# ten si nevzpomenu proc...
partialcomp: roff
#
# tu jsem mel moznost detalneji popsat prubeh vypostU
# momentalne to nic nedela...
debugprt: True
#
# zde lze zadat casy, kde chces ulozit vysledky
# pokud pomlcka nedela nic
printtimes: -



