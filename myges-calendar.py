#!/usr/bin/python3
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import sys
import json, time, base64
from geopy.geocoders import Nominatim
from icalendar import Calendar

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fonctions import *

file = open("skolae.json", 'r+', encoding="utf-8")
data = json.load(file)

username = data["username"]
password = data["password"]

if username is None or password is None :
    set_identifiants()

hash = check_hash(username, password)

if (data["b64"] is None) or (hash != data["b64"]):
    save_base64("b64", hash)

if data["auth"]["access_token"] is None or data["auth"]["expires_in"] < int(time.time()) :
    token_infos = request_infos(hash)
    
    token_infos = token_infos.replace('comreseaugesskolae:/oauth2redirect#', '')
    token_infos = token_infos.split('&')
    
    for x in range(len(token_infos)):
        token_infos[x] = token_infos[x].split('=')
    
    for x in range(len(token_infos)):
        if token_infos[x][0] == 'expires_in':
            token_infos[x][1] = int(token_infos[x][1])
            token_infos[x][1] += int(time.time())
        
        save_auth(token_infos[x][0], token_infos[x][1])


day1 = []
LastDay = []
for x in range(2):
    result = get_date(x)
    day1.append(result[0])
    LastDay.append(result[1])

calendrier = []

for x in range(2):
    result = get_calendar(day1[x], LastDay[x], data["auth"]["token_type"], data["auth"]["access_token"])
    calendrier.append(result)
  

cal = Calendar()
cal.add('prodid', '-//Made by Flavien FOUQUERAY//')
cal.add('version', '2.0')

for x in range(len(calendrier)):
    create_events(calendrier[x], cal)

MyGES_Calendar_ICS = open(f'MyGES_{data["username"]}.ics', 'wb')
MyGES_Calendar_ICS.write(cal.to_ical())
MyGES_Calendar_ICS.close()
