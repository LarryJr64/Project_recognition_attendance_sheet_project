# Explorateur de fichiers
from tkinter import *
from tkinter.filedialog import askopenfilename
# Selenium / Webdriver
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
# Autres
from rich.progress import track
from rich.console import Console
import getpass
from time import sleep
import re
import pandas as pd
from collections import defaultdict
from datetime import datetime
import json
import pandas as pd

console = Console()

# Sélection des chemin d'accès à chromedriver.exe et navigateur.exe
def get_paths():
    global driver_path
    global browser_path
    root = Tk()
    root.update()
    console.print('Sélectionnez le fichier chromedriver.exe', style="#3399FF")
    driver_path = askopenfilename(
    title='Sélectionnez le fichier chromedriver.exe')
    console.print('Sélectionnez le .exe du navigateur', style="#3399FF")
    root.withdraw()
    browser_path = askopenfilename(title='Sélectionnez le .exe du navigateur')
    root.destroy()
    
get_paths()

def web():
    global driver
    option = webdriver.ChromeOptions()
    option.add_experimental_option("detach", True)
    option.add_experimental_option('excludeSwitches', ['enable-logging'])
    option.add_argument('headless')
    option.binary_location = browser_path
    s = Service(driver_path)
    driver = webdriver.Chrome(service=s, options=option)
    driver.get('https://monemploidutemps.unistra.fr/consult/calendar')
    
web()

# Demande l'identifiant et le mot de passe UNISTRA
def get_user_info():
    global username
    global password
    username = input('Identifiant UNISTRA?')
    password = getpass.getpass('Mot de passe UNISTRA?')

driver.find_element()
# Renvoi des informations au navigateur et clique sur login
def connect():
    driver.find_element(By.ID, 'username').send_keys(username)
    driver.find_element(By.ID, 'password').send_keys(password)
    driver.find_element(By.ID, 'login-btn').click()


# Contrôle si encore sur la page de login ou pas
def check_login():
    try:
        driver.find_element(By.CLASS_NAME, 'login')
    except NoSuchElementException:
        return False
    return True

#get_user_info()
#connect()
#check_login()

def connect_user():
    get_user_info()
    connect()
    while check_login():
        driver.find_element(By.ID, 'username').clear()
        console.print(
            'Mot de passe ou Identifiant incorrect, veuillez réessayer.', style='red')
        connect_user()
    return console.print('Connexion Réussie.', style='green')

connect_user()



### SCRAPING ###
# Récupère les évènements d'aujourd'hui
def get_today_events():
    global today_events
    today_events = driver.find_element(
        By.CLASS_NAME, 'v-calendar-daily__day.v-present').get_attribute('outerHTML')

# Sépare les évènements dans une liste puis str(liste)
def get_sep_events():
    global sep_events
    sep_events = []
    sep_events = re.findall(
        'div class="v-event-timed onsecondary--text"(.*?)</div></div>', today_events)
    sep_events = str(sep_events)
    return sep_events

# Récupère les pixels qui déterminent l'heure de début
def get_top_pixels():
    global top_pixels
    top_pixels = re.findall('top: (.*?)px;', sep_events)
    top_pixels = [int(p) for p in top_pixels]
    return top_pixels

# Récupère les pixels qui déterminent la durée
def get_height_pixels():
    global height_pixels
    height_pixels = re.findall('height: (.*?)px;', sep_events)
    height_pixels = [int(p) for p in height_pixels]
    return height_pixels

def get_prof_cours():
    global professors
    professors_brut = driver.find_elements(
        By.CLASS_NAME, 'v-calendar-daily__day.v-present')
    professors = professors_brut[0].text
    professors = professors.replace("\n"," ")
    return professors

get_today_events()
get_sep_events()
get_top_pixels()
get_height_pixels()
get_prof_cours()

def info_pel():
    # Meilleur en code qu'en skate ##lescroisés
    global infos
    text = get_prof_cours()
    infos= text.replace(" - Idem-Lab","")
    infos = re.split('( . \d{3})',infos)
    [infos[i]+infos[i+1] for i in range(0,len(infos)-1,2)]
    return infos
info_pel()

#Conversion pixels qui déterminent le début en HH:MM
def get_occupation_start():
    global occupation_start_numbers
    global occupation_start_in_hours
    occupation_start_numbers = [
        (7 + ((p / 20) * 0.5)) * 60 for p in top_pixels]
    df1 = pd.DataFrame({'start': occupation_start_numbers})
    df1 = pd.to_datetime(df1.start, unit='m').dt.strftime('%H:%M')
    occupation_start_in_hours = df1.values.tolist()

# Conversion pixels qui déterminent la durée en HH:MM
def get_occupation_duration():
    global occupation_duration
    global occupation_duration_in_hours
    occupation_duration = [(((p / 20) * 0.5) * 60) for p in height_pixels]
    df = pd.DataFrame({'duration': occupation_duration})
    df = pd.to_datetime(df.duration, unit='m').dt.strftime('%H:%M')
    occupation_duration_in_hours = df.values.tolist()


# Déterminent l'heure de fin en HH:MM
def get_occupation_end():
    global occupation_end_in_hours
    occupation_end_in_minutes = [
        x + y for x, y in zip(occupation_start_numbers, occupation_duration)]
    df2 = pd.DataFrame({'end': occupation_end_in_minutes})
    df2 = pd.to_datetime(df2.end, unit='m').dt.strftime('%H:%M')
    occupation_end_in_hours = df2.values.tolist()

#Mise ensemble de l'haure de début et l'heure de fin
# Intégration de toutes les informations dans un dictionnaire
def get_dict():
    global dict_content
    global start_end
    dict_content = defaultdict(list)
    start_end = [list(t) for t in zip(occupation_start_in_hours, 
                                      occupation_end_in_hours)]
    
get_occupation_start()
get_occupation_duration()
get_occupation_end()
get_dict()

start_end = [['08:00', '09:00'], ['09:00', '11:00'], ['11:00', '12:00']]
infos = ['Travail personnel',
 ' A 330',
 ' UE 1. Architectures, modèles et langages de données',
 ' A 330',
 ' Travail personnel',
 ' A 330',
 '']
with open(r'D:\Cours_2021-2022\Semestre_3\Architecture_de_donnees\output_facial.json', 'r') as fp:
    output_facial= json.load(fp)

output_facial

df_cours_1 = 

def prep_df():
        global a,b,c,d,e,k,l,m,n,o
        if len(start_end)==0:
                a=""
                b=""
                c=""
                d=""
                e=""
                k=""
                l=""
                m=""
                n=""
                o=""
        elif len(start_end)==1:
                a=infos[0]
                b=""
                c=""
                d=""
                e=""
                k=start_end[0]
                l=""
                m=""
                n=""
                o=""
        elif len(start_end)==2:
                a=infos[0]
                b=infos[2]
                c=""
                d=""
                e=""
                k=start_end[0]
                l=start_end[1]
                m=""
                n=""
                o=""
        elif len(start_end)==3:
                a=infos[0]
                b=infos[2]
                c=infos[4]
                d=""
                e=""
                k=start_end[0]
                l=start_end[1]
                m=start_end[2]
                n=""
                o=""
        elif len(start_end)==3:
                a=infos[0]
                b=infos[2]
                c=infos[4]
                d=infos[6]
                e=""
                k=start_end[0]
                l=start_end[1]
                m=start_end[2]
                n=start_end[3]
                o=""
        elif len(start_end)==4:
                a=infos[0]
                b=infos[2]
                c=infos[4]
                d=infos[6]
                e=infos[8]
                k=start_end[0]
                l=start_end[1]
                m=start_end[2]
                n=start_end[3]
                o=start_end[4]  
        else: 
                pass
    
prep_df()

data0 = {'Colonne_0' : [datetime.today().strftime('%d-%m-%Y'),'Intitulé_du_cours_prof','Horaires','signature_de_l_enseignant'],
        'Colonne_1' : ['',a,k,'Signature1'],
        'Colonne_2' : ['',b,l,'Signature2'],
        'Colonne_3' : ['',c,m,'Signature3'],
        'Colonne_4' : ['',d,n,'Signature4'],
        'Colonne_5' : ['',e,o,'Signature4']}

df0 = pd.DataFrame(data0)

data1 = {'Colonne_0' :['Elève_alternant','NEURETHER Alexander','LANEVE Louis'],
        'Colonne_1' : ['','Signature1','Signature1'],
        'Colonne_2' : ['','Signature2','Signature2'],
        'Colonne_3' : ['','Signature3','Signature3'],
        'Colonne_4' : ['','Signature4','Signature4'],
        'Colonne_5' : ['','Signature5','Signature5']}

df1 = pd.DataFrame(data1)

data2 = {'Colonne_0' :['Elève_non_alternant','ROUSSAUX Claude-Marie'],
        'Colonne_1' : ['','Signature1'],
        'Colonne_2' : ['','Signature2'],
        'Colonne_3' : ['','Signature3'],
        'Colonne_4' : ['','Signature4'],
        'Colonne_5' : ['','Signature5']}

df2 = pd.DataFrame(data2)

frames = [df0, df1, df2]
df = pd.concat(frames)

df.set_index("Colonne_0", inplace=True)
df.index.names= ['testi']
df

output_facial


for i in df['testi']:
    if df['testi']=re(output_facial)== true and colonne_1 = signature1 == true:
        append ("x")
    elif ...
        

pd.read_csv(r"D:\Cours_2021-2022\Semestre_3\Architecture_de_donnees\output_csv.csv")
        
# https://www.projectpro.io/recipes/insert-new-column-based-on-condition-in-python