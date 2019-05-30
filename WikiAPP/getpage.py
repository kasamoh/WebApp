#!/usr/bin/python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from json import loads
from urllib.request import urlopen
from urllib.parse import urlencode
import ssl
from urllib.parse import unquote

find_all = lambda c,s: [x for x in range(c.find(s), len(c)) if c[x] == s] # fonction retournant tous les indices d'un char dans une str
cache = {}  ## initialize cache



#########################   fonction qui retourne le contenu d'une reponse web      #################
def getJSON(page):
    params = urlencode({
      'format': 'json',  # TODO: compléter ceci
      'action': 'parse',  # TODO: compléter ceci
      'prop': 'text',  # TODO: compléter ceci
      'redirects':'true',
      'page': page})
    API = "http://fr.wikipedia.org/w/api.php"  # TODO: changer ceci
    # désactivation de la vérification SSL pour contourner un problème sur le
    # serveur d'évaluation -- ne pas modifier
    gcontext = ssl.SSLContext()
    response = urlopen(API + "?" + params, context=gcontext)
    return response.read().decode('utf-8')


######################### fonction qui extrai le titre et le contenu d'une reponse html################

def getRawPage(page):
    parsed = loads(getJSON(page))
    try:
        title = parsed['parse']['title']  
        content = parsed['parse']['text']["*"] 
        return title, content
    except KeyError:
        # La page demandée n'existe pas
        return None, None

######################### chech intermediaire des link  avant d'examiner la réponse ##################

def checklink ( link) :
    if 'http' in link or  'fr.wikipedia.org' in link or 'redlink' in link or ':' in link.lower(): 
        return True 
    else :
        return False

######################### fontion qui retourne le titre et la liste des hyperlinks dans l'article ################

def getPage(page):
    links_with_text = [] ## liste de tous les href
    max_items=10 ### max href

    ### tester si l'article est dans le cache #####
    if unquote(unquote(page)) in list(cache.keys()) :
        title,listhref=cache[unquote(unquote(page))]
        return unquote(title),listhref
    else : 
    ### sinon
        try:
            title,content =getRawPage(unquote(page)) ## recuperer le contenu
            soup = BeautifulSoup(content, 'html.parser')
            ###### chercher les balises p dans la racine est div#########
            #anchors = [el_div.find_all('p') for el_div in  soup.find_all('div') ]
            anchors=soup.div.find_all("p", recursive=False)
            links_with_text=[]
            ###### recuperer les href ###############
            for p_text_a in anchors :
                list_coherent_href=[a.get('href') for a in p_text_a.find_all('a', href=True) if a.text]
                links_with_text.append(list_coherent_href)
            listhref=[item for sublist in links_with_text for item in sublist]


            ####### filtrage des href ##############
            if (len(listhref)) > 0: ## au moins un lien
                nb_items=0
                listehref_final=[] ## listefinale des href
                k=0 ## compteur
                nb_items=0 ## number of collected items
                while (nb_items < max_items and k < len(listhref)):
                    ref=listhref[k]
                    if checklink(ref)==False : 
                        new_ref=unquote(ref.replace('/wiki/',''))
                        indice_dies=find_all(new_ref,'#')
                        if len (indice_dies)> 0:
                             new_ref=new_ref[0:indice_dies[0]]
                        new_ref=new_ref.replace("_"," ")
                        if new_ref not in listehref_final  and len(new_ref)>1:
                            listehref_final.append(new_ref)
                            nb_items+=1
                    k+=1    
                cache[unquote(page)]=(unquote(title),listehref_final) ## mettre à jour le cache
                return  unquote(title),listehref_final
            else : 
                cache[unquote(page)]=(unquote(title),[] )## mettre à jour le cache
                return unquote(title),[] 
        except :
        # La page demandée n'existe pas
            cache[unquote(page)]=(None, [])
            return None, []



#################################           main            ##############################

if __name__ == '__main__':
    # Ce code est exécuté lorsque l'on exécute le fichier
    print("Ça fonctionne !")
    title,listhref=getPage( "Jean-Jacques Rousseau")
    print(listhref)
    # print(getRawPage("Histoire"))

