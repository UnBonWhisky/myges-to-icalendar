# myges to icalendar

Voici un script utilisant l'API de l'application mobile Skolae, qui est utilisée pour les écoles du réseau GES.

Ce programme récupère l'agenda de cours que nous avons sur le mois actuel + le mois suivant, et en fait un fichier ICS qui peut être importé sur les iDevices
(application "Calendrier" par défaut) ou sur Google Calendar.

Pour les iPhone / iPad, il est possible de l'intégrer en tant que calendrier suivi afin d'obtenir les informations et modifications en temps réel.
Il est possible que ça se fasse également sur Google Calendar, mais je ne connais pas assez le sujet sur cette plateforme pour le confirmer.

----

# Fonctionnement

Le script fonctionne avec python, il vous faut donc l'installer sur votre ordinateur / serveur ainsi que les paquets situés dans le fichier `requirements.txt`
grâce à `pip`. Si vous ne savez pas comment faire
[voici un tutoriel sur l'installation de paquets avec pip](https://docs.python.org/fr/3.5/installing/index.html#work-with-multiple-versions-of-python-installed-in-parallel).

Une fois ces paquets installés, vous devrez télécharger les 3 fichiers suivants :
- `skolae.json`
- `myges-calendar.py`
- `fonctions.py`

Dans le fichier `skolae.json`, vous devrez modifier les variables où il est écrit `ICI` en rouge pour mettre votre identifiant et votre mot de passe MyGES.  
Il faudra également que vos identifiants soient entre guillemets et que vous ajoutiez vos campus, comme dans l'`_exemple` :
```json
{
    "_exemple": {
        "username": "pnom",
        "password": "mot de passe myges",
        "commentaire": "Mettez vos informations en dessous (là ou c'est actuellement marqué null)"
    },
    "username": ICI,
    "password": ICI,
    "b64": null,
    "auth": {
        "access_token": null,
        "token_type": null,
        "expires_in": 0,
        "scope": null
    },
    "Campus1": "Adresse du campus 1",
    "Campus2": "Adresse du campus 2",
    "Campus3": "Adresse du campus 3"
}
```

Une fois que vous avez entré votre identifiant et votre mot de passe, vous pouvez executer `myges-calendar.py`. Si aucun message ne vous est renvoyé, alors tout se passe bien.
Lorsque le programme se fermera, vous trouverez au même emplacement que `myges-calendar.py`, un nouveau fichier sous le nom de MyGES_pnom.ics que vous pourrez
ajouter à votre calendrier mobile.
