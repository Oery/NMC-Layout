import sys
import re
import os
import json
import getpass
import time
import ctypes
from urllib.parse import urlparse, parse_qs, urlencode, unquote
from itertools import product
from pynput.keyboard import Key, Controller
from PIL import Image
from colored import fg
import requests

VERSION = 1.0

ctypes.windll.kernel32.SetConsoleTitleW(f"NMC-Layout v{str(VERSION)} | By Oery")

SE = os.name
if SE == "nt":
    os.system('cls')
elif SE == "posix":
    os.system('clear')

b = fg('light_cyan')
info = fg('light_cyan')
ntext = fg('white')
text = fg('light_yellow')
green = fg('green')
error = fg('light_red')

print("")
print(b +"ooooo      ooo ooo        ooooo   .oooooo.           ooooo                                                        .   ")
print(b +"`888b.     `8' `88.       .888'  d8P'  `Y8b          `888'                                                      .o8   ")
print(b +" 8 `88b.    8   888b     d'888  888                   888          .oooo.   oooo    ooo  .ooooo.  oooo  oooo  .o888oo ")
print(b +" 8   `88b.  8   8 Y88. .P  888  888                   888         `P  )88b   `88.  .8'  d88' `88b `888  `888    888   ")
print(b +" 8     `88b.8   8  `888'   888  888          8888888  888          .oP\"888    `88..8'   888   888  888   888    888   ")
print(b +" 8       `888   8    Y     888  `88b    ooo           888       o d8(  888     `888'    888   888  888   888    888 . ")
print(b +"o8o        `8  o8o        o888o  `Y8bood8P'          o888ooooood8 `Y888""8o     .8'     `Y8bod8P'  `V88V\"V8P'   \"888\" ")
print(b +"                                                                            .o..P'                                    ")
print(b +"                                                                            `Y8P'                                     ")
print(fg("light_cyan") + "Version 1.0 | " + fg("white") + "développé par " + fg("light_cyan") + "Oery#0001")
print("")
print("")  

#Chargement du layout et du skin template
layout = Image.open("layout.png").copy().convert('RGBA')
skin = Image.open("assets/template.png").copy().convert('RGBA')

#Génération des skins
ext = ".png"
w, h = layout.size
d = 8
dir_out = "assets/skins"

grid = list(product(range(0, h-h%d, d), range(0, w-w%d, d)))
index = 27
for i, j in grid:
    box = (j, i, j+d, i+d)
    out = os.path.join(dir_out, f'{index}{ext}')
    skin.paste(layout.crop(box), (8, 8))

    pixels = skin.load()
    pixels[index+8, 0] = (255, 255, 255)

    skin.save(out)
    index -= 1

#Récupération des infos de connexion
LOGIN = input(info + "[INFO] " + ntext + "Adresse Mail : " + text + "")
PASSWORD = getpass.getpass(info + "[INFO] " + ntext + "Mot de passe : ")
print("")

#Connexion au compte Microsoft
ctypes.windll.kernel32.SetConsoleTitleW(f"NMC-Layout v{str(VERSION)} | Connexion au compte Microsoft")
try:
    session = requests.session()

    base_url = 'https://login.live.com/oauth20_authorize.srf?'
    qs = unquote(urlencode({
        'client_id': '0000000048093EE3',
        'redirect_uri': 'https://login.live.com/oauth20_desktop.srf',
        'response_type': 'token',
        'display': 'touch',
        'scope': 'service::user.auth.xboxlive.com::MBI_SSL',
        'locale': 'en',
    }))
    resp = session.get(base_url + qs)
    url_re = b'urlPost:\\\'([A-Za-z0-9:\?_\-\.&/=]+)'
    ppft_re = b'sFTTag:\\\'.*value="(.*)"/>'
    login_post_url = re.search(url_re, resp.content).group(1)
    post_data = {
        'login': LOGIN,
        'passwd': PASSWORD,
        'PPFT': re.search(ppft_re, resp.content).groups(1)[0],
        'PPSX': 'Passpor',
        'SI': 'Sign in',
        'type': '11',
        'NewUser': '1',
        'LoginOptions': '1',
        'i3': '36728',
        'm1': '768',
        'm2': '1184',
        'm3': '0',
        'i12': '1',
        'i17': '0',
        'i18': '__Login_Host|1',
    }
    resp = session.post(
        login_post_url, data=post_data, allow_redirects=False,
    )
    location = resp.headers.get('Location', "ERREUR")
    if location == "ERREUR": raise Exception("MDP")
    parsed = urlparse(location)
    fragment = parse_qs(parsed.fragment)
    access_token = fragment['access_token'][0]

    print(green + "[SUCCÈS] " + ntext + "Connexion à Microsoft réussie !")
except Exception as inst:
    if inst.args[0] == "MDP":
        input(error + "[ERREUR] " + ntext + "Impossible de se connecter au compte Microsoft ! Mot de passe ou nom d'utilisateur invalide." + fg("black"))
        sys.exit()
    else:
        input(error + "[ERREUR] " + ntext + "Impossible de se connecter au compte Microsoft ! Veuillez vérifier votre connexion à Internet. Votre réseau peut aussi bloquer l'accès au site." + fg("black"))
        sys.exit()

#Connexion au compte Xbox
ctypes.windll.kernel32.SetConsoleTitleW(f"NMC-Layout v{str(VERSION)} | Connexion au compte Xbox")
try:
    headers = {
        "Content-Type" : "application/json",
    }

    body = {
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": access_token
        },
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT"
    }

    URL = "https://user.auth.xboxlive.com/user/authenticate"

    response = requests.post(URL, data=json.dumps(body), headers={'Content-Type': 'application/json'})

    Token = response.json()["Token"]
    Hash = response.json()["DisplayClaims"]["xui"][0]["uhs"]

    print(green + "[SUCCÈS] " + ntext + "Connexion aux services Xbox réussie !")

except:
    input(error + "[ERREUR] " + ntext + "Impossible de se connecter aux services Xbox ! Veuillez vérifier votre connexion à Internet. Votre réseau peut aussi bloquer l'accès au site." + fg("black"))
    sys.exit()

#Récupération du token Xbox
ctypes.windll.kernel32.SetConsoleTitleW(f"NMC-Layout v{str(VERSION)} | Récupération du token Xbox")
try:
    URL = "https://xsts.auth.xboxlive.com/xsts/authorize"
    response = requests.post(URL, data=json.dumps({
        "Properties": {
            "SandboxId": "RETAIL",
            "UserTokens": [
                Token
            ]
        },
        "RelyingParty": "rp://api.minecraftservices.com/",
        "TokenType": "JWT"
    }), headers={"Content-Type": "application/json"})

    XTS_Token = response.json()["Token"]

    print(green + "[SUCCÈS] " + ntext + "Connexion au service d'authentification Xbox réussie !")

except:
    input(error + "[ERREUR] " + ntext + "Impossible de se connecter au service d'authentification XboX ! Veuillez vérifier votre connexion à Internet. Votre réseau peut aussi bloquer l'accès au site." + fg("black"))
    sys.exit()

#Connexion à l'API Minecraft
ctypes.windll.kernel32.SetConsoleTitleW(f"NMC-Layout v{str(VERSION)} | Connexion à minecraft.net")
try:
    identity = f"XBL3.0 x={Hash};{XTS_Token}"
    URL = "https://api.minecraftservices.com/authentication/login_with_xbox"
    response = requests.post(URL, data=json.dumps({
    "identityToken" : identity,
    "ensureLegacyEnabled" : True
    }), headers={"Content-Type": "application/json"})

    access_token = response.json()["access_token"]

except:
    input(error + "[ERREUR] " + ntext + "Impossible de se connecter à l'API Minecraft ! Veuillez vérifier votre connexion à Internet. Votre réseau peut aussi bloquer l'accès au site." + fg("black"))
    sys.exit()

hed = {
    "Authorization": "Bearer " + access_token,
    }

#Récupération du skin et du format actuel du joueur
r = requests.get("https://api.minecraftservices.com/minecraft/profile", headers=hed).json()
actual_skin = r["skins"][0]["url"]
actual_skin_variant = r["skins"][0]["variant"]
IGN = r["name"]
print(green + "[SUCCÈS]" + ntext + " Connexion réussie en tant que : " + text + IGN)
print("")

#Récupération des paramètres
with open("assets/settings.json", 'r') as f:
    delay = json.load(f)["delay"]

#Chargement de la page NameMC
SE = os.name
if SE == "nt": os.system(f"start https://fr.namemc.com/profile/{r['id']}")
elif SE == "posix": os.system(f"open -a https://fr.namemc.com/profile/{r['id']}")

time.sleep(delay)

#Chargement des skins du layout
ctypes.windll.kernel32.SetConsoleTitleW(f"NMC-Layout v{str(VERSION)} | Skins Téléversés : 0/27")
hed = {
    "Authorization": "Bearer " + access_token,
    "Content-Type": "multipart/form-data"
    }

api_url = "https://api.minecraftservices.com/minecraft/profile/skins"

hed = {
        "Authorization": "Bearer " + access_token,
        }

payload = {
        "variant": 'classic'
        }

try:
    for tile in range(1, 27):
        file = {f"{tile}.png": open(f'assets/skins/{tile}.png', 'rb')}
        response = requests.post(api_url, files=file, headers=hed, data=payload)

        time.sleep(delay // 2)
        Controller().press(Key.f5)
        Controller().release(Key.f5)
        time.sleep(delay - (delay // 2))
        ctypes.windll.kernel32.SetConsoleTitleW(f"NMC-Layout v{str(VERSION)} | Skins Téléversés : {tile}/27")
        print(green + "[SUCCÈS] " + ntext + f"Skin n°{tile}/27 publié !")

except:
    input(error + "[ERREUR] " + ntext + f"Impossible de publier le skin n°{tile} ! Veuillez vérifier votre connexion à Internet. Votre réseau peut aussi bloquer l'accès au site." + fg("black"))
    sys.exit()

#Chargement du skin actuel
hed = {
    "Authorization": "Bearer " + access_token,
    "Content-Type": "application/json"
    }

payload = {
  "url": actual_skin,
  "variant": actual_skin_variant
}
response = requests.post(api_url, data=json.dumps(payload), headers=hed)

time.sleep(delay // 2)

Controller().press(Key.f5)
Controller().release(Key.f5)
print(green + "[SUCCÈS] " + ntext + "Skin n°27/27 publié !")
ctypes.windll.kernel32.SetConsoleTitleW(f"NMC-Layout v{str(VERSION)} | Skins Téléversés : 27/27")
print("")
time.sleep(0.5)
ctypes.windll.kernel32.SetConsoleTitleW(f"NMC-Layout v{str(VERSION)} | By Oery")
input(green + "[SUCCÈS] " + ntext + "Le layout a été publié !" + fg("black"))
sys.exit()
