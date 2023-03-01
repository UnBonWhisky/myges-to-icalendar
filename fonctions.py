import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import requests, datetime, time, sys, json, dateutil.relativedelta, pytz, base64
from icalendar import Calendar, Event, vText

file = open("skolae.json", 'r+', encoding="utf-8")
data = json.load(file)

def check_hash(username, password):
    hash = bytes(f"{username}:{password}", encoding="utf-8")
    hash = base64.b64encode(hash).decode('utf-8')
    return hash

def set_identifiants():
    print("Entrez vos identifiants MyGES entre \"\" dans le fichier skolae.json\nUn exemple est affiché sous le nom de \"_exemple\".\nVous pouvez ouvrir ce fichier avec le bloc-notes ou notepad++.")
    time.sleep(3)
    sys.exit()

def save_base64(key, value):
    data[key] = value
    file.seek(0)
    json.dump(data, file, indent=4)
    file.truncate()

def save_auth(key, value):
    data['auth'][key] = value
    file.seek(0)
    json.dump(data, file, indent=4)
    file.truncate()

def request_infos(b64):
    url = "https://authentication.kordis.fr/oauth/authorize?response_type=token&client_id=skolae-app"
    headers = {
        'accept-encoding': 'gzip',
        'authorization': f'Basic {b64}',
        'connection': 'Keep-Alive',
        'user-agent': 'okhttp/3.13.1'
    }
    infos = requests.get(url, headers=headers, allow_redirects=False)
    if infos.status_code == 401 :
        print("Les identifiants que vous avez entré sont incorrectes. Merci de les changer dans le fichier skolae.json avant de relancer le programme.")
        time.sleep(3)
        sys.exit()
    else:
        return infos.headers["Location"]

def get_date(more_month):
    day1 = datetime.datetime.today().replace(day=1, hour=0, minute=0, second=0) + dateutil.relativedelta.relativedelta(months=more_month)
    LastDate = day1.replace(day=28, hour=23, minute=59, second=59) + datetime.timedelta(days=4)
    LastDate = LastDate - datetime.timedelta(days=LastDate.day)

    day1 = (int(day1.timestamp())+3600)*1000
    LastDate = (int(LastDate.timestamp())+3600)*1000

    return day1, LastDate

def get_calendar(day1, LastDay, token_type, access_token):
    url = f"https://api.kordis.fr/me/agenda?start={day1}&end={LastDay}"
    headers = {
        'accept-encoding': 'gzip',
        'authorization': f'{token_type} {access_token}',
        'connection': 'Keep-Alive',
        'user-agent': 'okhttp/3.13.1'
    }
    calendrier = requests.get(url, headers=headers)
    
    return calendrier.json()

def create_events(calendrier, cal):
    event_campus = {}
    for x in range(len(calendrier["result"])):    
        event = Event()
        AddressCampus = ""

        if calendrier["result"][x]["type"] == "Cours" :
            if calendrier["result"][x]["modality"] == "Présentiel":
                if calendrier["result"][x]["rooms"] is None :
                    AddressCampus = "En attente de réservation"
                    description = f'Type de présence : {calendrier["result"][x]["modality"]}\nCampus : SALLE NON RÉSERVÉE\nAdresse : NON DISPONIBLE'
                
                else:
                    AddressCampus = data["campus"][calendrier["result"][x]["rooms"][0]["campus"]]
                    description = f'Type de présence : {calendrier["result"][x]["modality"]}\nCampus : {calendrier["result"][x]["rooms"][0]["campus"]}\nSalle : {calendrier["result"][x]["rooms"][0]["name"]}\nAdresse : {AddressCampus}'

            elif calendrier["result"][x]["modality"] == "Distanciel":
                description = f'Type de présence : {calendrier["result"][x]["modality"]}'
        
        elif calendrier["result"][x]["type"] == "Examen" or calendrier["result"][x]["type"] == "Soutenance" :
            if calendrier["result"][x]["modality"] == "" and calendrier["result"][x]["rooms"] is None :
                AddressCampus = "En attente des informations"
                description = "Informations indisponibles pour le moment"
            
            elif calendrier["result"][x]["rooms"] is not None :
                for campus in range(len(calendrier["result"][x]["rooms"])):
                    if f'{calendrier["result"][x]["start_date"]}' not in event_campus:
                        event_campus[f'{calendrier["result"][x]["start_date"]}'] = []
                    
                    if calendrier["result"][x]["rooms"][campus]["campus"] not in event_campus[f'{calendrier["result"][x]["start_date"]}'] :
                        event_campus[f'{calendrier["result"][x]["start_date"]}'].append(calendrier["result"][x]["rooms"][campus]["campus"])
                        break
                
                salles = []
                for room in range(len(calendrier["result"][x]["rooms"])):
                    if calendrier["result"][x]["rooms"][room]["campus"] == event_campus[f'{calendrier["result"][x]["start_date"]}'][-1] :
                        salles.append(calendrier["result"][x]["rooms"][room]["name"])
                
                
                AddressCampus = data["campus"][event_campus[f'{calendrier["result"][x]["start_date"]}'][-1]]
                campus_name = event_campus[f'{calendrier["result"][x]["start_date"]}'][-1]
                description = f'Type de présence : Présentiel\nCampus : {campus_name}\nSalle{"s" if len(salles) > 1 else ""} : {", ".join(salles)}\nAdresse : {AddressCampus}'
            
            elif calendrier["result"][x]["modality"] != "" and calendrier["result"][x]["rooms"] is None :
                AddressCampus = "En attente des informations"
                description = "Informations indisponibles pour le moment"

        else :
            continue

        if calendrier["result"][x]["type"] == "Cours" :
            event.add('summary', f'{calendrier["result"][x]["name"]} - {calendrier["result"][x]["discipline"]["teacher"]}')
        else:
            event.add('summary', f'{calendrier["result"][x]["type"]} - {calendrier["result"][x]["name"]}')
        dtstart = datetime.datetime.fromtimestamp(int(calendrier["result"][x]["start_date"])/1000, tz=pytz.utc)
        dtend = datetime.datetime.fromtimestamp(int(calendrier["result"][x]["end_date"])/1000, tz=pytz.utc)
        
        event.add('description', description)
        
        event.add('dtstart', dtstart)
        event.add('dtend', dtend)

        event.add('priority', 5)

        event['location'] = vText(AddressCampus)
        
        cal.add_component(event)
