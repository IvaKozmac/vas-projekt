# Upute za pokretanje 

Ove upute pisane su za Linux Ubuntu 22.04.

1. Instalirati python 3.9 (Spade ne radi sa verzijom 3.10!!!)
    - Ako je već po defaultu instalirana druga verzija Python onda nakon instalacije:
        1. Pokrenuti u terminalu `update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9`
        2. Provjeriti da li je uneseno sa `update-alternatives --list python3`
        3. Zamijeniti glavnu verziju Pythona u 3.9 pomoću `update-alternatives --config python3` i nakon toga odabirom nečeg poput: /usr/bin/python3.9.
    - Za dodatne upute, pratiti ovo [Multiple python versions on Ubuntu](https://hackersandslackers.com/multiple-python-versions-ubuntu-20-04/)
2. Instalirati pip 
3. Instalirati NodeJS (LTS) i npm
4. Instalirati spade sa komandom `python3.9 -m pip install spade` (sada u editoru ne bi smjelo biti greške da se ne može pronaći biblioteka kod importa)
5. Pozicionirati se u mapu agenti/ i u 5 različitih terminala pokrenuti NPC-jeve 1-5 sa narednom `python3.9 ./NPC{broj}.py`
6. U 6. terminalu pozicionirati se u mapu web/, zatim pokrenuti komandu `npm install` i nakon toga `npm run dev`
7. U terminalu će pisati lokalni url na kojem se može vidjeti glavna web stranica igre.
8. Pratiti upute i igrati!


## Podaci za prijavu

Stranica za registraciju agenata: [5222.de](https://5222.de)

**Igrač** 
iva-vas-projekt-main@jabber.eu.org
12345678

**NPC1** 
iva-vas-projekt-npc1@5222.de
12345678

**NPC2** 
iva-vas-projekt-npc2@5222.de
12345678

**NPC3** 
iva-vas-projekt-npc3@5222.de
12345678

**NPC4** 
iva-vas-projekt-npc4@5222.de
12345678

**NPC5** 
iva-vas-projekt-npc5@5222.de
12345678

