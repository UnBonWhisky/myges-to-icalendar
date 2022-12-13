import requests, datetime, time, sys, json, dateutil.relativedelta, geopy, pytz, base64
from icalendar import Calendar, Event, vText

file = open("skolae.json", 'r+', encoding="utf-8")
data = json.load(file)

def check_hash(username, password): # On check si le base64 des ID est toujours le bon par rapport à celui de notre username:password
    hash = bytes(f"{username}:{password}", encoding="utf-8")
    hash = base64.b64encode(hash).decode('utf-8')
    return hash

def set_identifiants(): # Si les identifiants n'ont pas été entré, on renvoie ici et on quitte le programme
    print("Entrez vos identifiants MyGES entre \"\" dans le fichier skolae.json\nUn exemple est affiché sous le nom de \"_exemple\".\nVous pouvez ouvrir ce fichier avec le bloc-notes ou notepad++.")
    time.sleep(3)
    sys.exit()

def save_base64(key, value): # On sauvegarde le base64 s'il est vide ou s'il est incorrecte par rapport à username:password
    data[key] = value
    file.seek(0)
    json.dump(data, file, indent=4)
    file.truncate()

def request_infos(b64): # On vient demander les informations nécessaires comme le token et sa date d'expiration, mais aussi checker si username + password sont bons
    url = "https://authentication.kordis.fr/oauth/authorize?response_type=token&client_id=skolae-app"
    headers = {
        'accept-encoding': 'gzip',
        'authorization': f'Basic {b64}',
        'connection': 'Keep-Alive',
        'user-agent': 'okhttp/3.13.1'
    }
    infos = requests.get(url, headers=headers, allow_redirects=False)
    if infos.status_code == 401 : # une réponse 401 signifie que les identifiants ne sont pas bons
        print("Les identifiants que vous avez entré sont incorrectes. Merci de les changer dans le fichier skolae.json avant de relancer le programme.")
        time.sleep(3)
        sys.exit()
    else:
        return infos.headers["Location"]

def save_auth(key, value): # On sauvegarde les informations d'authentification (token, expiration de celui-ci...)
    data['auth'][key] = value
    file.seek(0)
    json.dump(data, file, indent=4)
    file.truncate()

def get_date(more_month): # On vient récupérer les timestamp du mois actuel + mois prochain (boucle par rapport au fichier principal / myges-calendar.ics)
    day1 = datetime.datetime.today().replace(day=1, hour=0, minute=0, second=0) + dateutil.relativedelta.relativedelta(months=more_month)
    LastDate = day1.replace(day=28, hour=23, minute=59, second=59) + datetime.timedelta(days=4)
    LastDate = LastDate - datetime.timedelta(days=LastDate.day)

    day1 = (int(day1.timestamp())+3600)*1000
    LastDate = (int(LastDate.timestamp())+3600)*1000

    return day1, LastDate

def get_calendar(day1, LastDay, token_type, access_token): # On récupère un LOOOOONG JSON de tous les cours que l'on a sur la période donnée (mois actuel ou mois +1)
    url = f"https://api.kordis.fr/me/agenda?start={day1}&end={LastDay}"
    headers = {
        'accept-encoding': 'gzip',
        'authorization': f'{token_type} {access_token}',
        'connection': 'Keep-Alive',
        'user-agent': 'okhttp/3.13.1'
    }
    calendrier = requests.get(url, headers=headers)
    
    return calendrier.json()

def create_events(calendrier, geolocator, cal): # On crée les evenements qui iront dans le fichier ics / icalendar pour notre téléphone par rapport au JSON du mois de cours
    for x in range(len(calendrier["result"])):    
        event = Event()
        
        if calendrier["result"][x]["modality"] == "Présentiel":
            location = geolocator.reverse(f'{calendrier["result"][x]["rooms"][0]["latitude"]},{calendrier["result"][x]["rooms"][0]["longitude"]}').raw['address']
            try:
                if location['shop'] == "L'Eden Coiffure" :
                    location['house_number'] = '218'
                    location['postcode'] = '75012'
            except:
                pass
            AddressCampus = f"{location['house_number']} {location['road']}, {location['postcode']} {location['city']}"
            
            description = f'Type de présence : {calendrier["result"][x]["modality"]}\nCampus : {calendrier["result"][x]["rooms"][0]["campus"]}\nSalle : {calendrier["result"][x]["rooms"][0]["name"]}\nAdresse : {AddressCampus}'

            event['location'] = vText(AddressCampus)
        
        elif calendrier["result"][x]["modality"] == "Distanciel":
            description = f'Type de présence : {calendrier["result"][x]["modality"]}'

        else :
            continue
        
        event.add('summary', f'{calendrier["result"][x]["name"]} - {calendrier["result"][x]["discipline"]["teacher"]}')
        dtstart = datetime.datetime.fromtimestamp(int(calendrier["result"][x]["start_date"])/1000, tz=pytz.utc) # Le pytz.utc permet de garder la période de temps UTC et adapter l'heure de cours au fuseau horaire du téléphone
        dtend = datetime.datetime.fromtimestamp(int(calendrier["result"][x]["end_date"])/1000, tz=pytz.utc)
        
        event.add('description', description)
        
        event.add('dtstart', dtstart)
        event.add('dtend', dtend)

        event.add('priority', 5) # On met la priorité par défaut
        cal.add_component(event) # On ajoute l'évènement au fichier de calendrier qui contiendra chacun de nos cours
