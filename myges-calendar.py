#!/usr/bin/python3
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import json, time
from geopy.geocoders import Nominatim
from icalendar import Calendar
from fonctions import *


file = open("skolae.json", 'r+', encoding="utf-8") # On ouvre le fichier JSON
data = json.load(file)

username = data["username"]
password = data["password"]

if username is None or password is None :
    set_identifiants()

hash = check_hash()

if (data["b64"] is None) or (hash != data["b64"]):
    save_base64("b64", hash)

if data["auth"]["access_token"] is None or data["auth"]["expires_in"] < int(time.time()) :
    token_infos = request_infos(hash) # On vient décortiquer une partie du header pour garder les informations nécessaires
    
    token_infos = token_infos.replace('comreseaugesskolae:/oauth2redirect#', '')
    token_infos = token_infos.split('&')
    
    for x in range(len(token_infos)):
        token_infos[x] = token_infos[x].split('=')
    
    for x in range(len(token_infos)): # On vient stocker ces informations nécessaires dans le fichier JSON pour les avoir en cache jusqu'à expiration
        if token_infos[x][0] == 'expires_in':
            token_infos[x][1] = int(token_infos[x][1])
            token_infos[x][1] += int(time.time())
        
        save_auth(token_infos[x][0], token_infos[x][1])


day1 = []
LastDay = []
for x in range(2): # Récupération des timestamp pour le 1er jour et le dernier jour du mois, sur le mois actuel + le prochain mois
    result = get_date(x)
    day1.append(result[0])
    LastDay.append(result[1])

geolocator = Nominatim(user_agent="SkolaeApp") # Déclaration du service de geocoding pour passer d'une latitude + longitude à une adresse

calendrier = []

for x in range(2): # On récupère les cours en se basant sur les timestamp récupéré précédemment
    result = get_calendar(day1[x], LastDay[x], data["auth"]["token_type"], data["auth"]["access_token"])
    calendrier.append(result)


cal = Calendar() # On déclare ce qui deviendra notre fichier ICS avec les informations obligatoire (prodid + version)
cal.add('prodid', '-//SkolaeApp - MyGES Calendar//')
cal.add('version', '2.0')

for x in range(len(calendrier)): # On ajoute les évènements de nos cours dans notre fichier ICS. JE NE STOCK QUE LES COURS, RIEN D'AUTRE
    create_events(calendrier[x], geolocator, cal)

MyGES_Calendar_ICS = open(f'MyGES_{data["username"]}.ics', 'wb') # On crée notre fichier ICS sous le nom de MyGES_pnom.ics à l'emplacement souhaité
MyGES_Calendar_ICS.write(cal.to_ical())
MyGES_Calendar_ICS.close()
