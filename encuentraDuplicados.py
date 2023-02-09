from jira import JIRA
from datetime import timedelta
import datetime as dt

import xlsxwriter
import pandas as pd

import nltk
from nltk.metrics.distance import jaccard_distance
from nltk.corpus import wordnet

import spacy
import re
import slack
from gensim.models import Word2Vec
from gensim.models.keyedvectors import KeyedVectors

nlp = spacy.load("es_core_news_md")

import nltk
nltk.download("stopwords")
from nltk.corpus import stopwords
stop_words = stopwords.words("spanish")
#print(stop_words)

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from unidecode import unidecode


from nltk.corpus import wordnet_ic
from nltk.corpus import wordnet

nltk.download('wordnet_ic')
#ic = wordnet_ic.ic('ic-es.dat')



 
SLACK_TOKEN = ("xoxb-65459601617-4762853541925-q5nkytexDU5EW337wjqI8F0x")
 
client = slack.WebClient(token=SLACK_TOKEN)


nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

def remove_stopwords(ticket):
    ticket = [word for word in ticket if word not in stop_words]
    return ticket

def preprocess_ticket(ticket):
    ticket = unidecode(ticket)
    ticket = re.sub('[^a-zA-Z]', ' ', ticket) 
    ticket = ticket.lower()
    ticket = ticket.split()
    return ticket


def get_synonyms(word, lang='spa'):
    synonyms = []
    for syn in wordnet.synsets(word, lang=lang):
        for lemma in syn.lemmas(lang=lang):
            synonyms.append(lemma.name())
    return set(synonyms)

def obtener_sinonimos(palabra):
    sinonimos = []
    for syn in wordnet.synsets(palabra, lang='spa'):
        for lemma in syn.lemmas(lang='spa'):
            sinonimos.append(lemma.name())
    return sinonimos

def calcularSimilitud(ticket1, ticket2):
    #print("Ticket solo", ticket1)   
    #print("Ticket solo", ticket2)
    preticket1 = preprocess_ticket(ticket1)
    preticket2 = preprocess_ticket(ticket2)
    #print("Preticket", preticket1)
    #print("Preticket", preticket2)
    texto1 = remove_stopwords(preticket1)
    texto2 = remove_stopwords(preticket2)
    #print("Sin stop ", set(texto1))
    #print("Sin stop ", set(texto2))
    text1_tokens = nltk.word_tokenize(' '.join(texto1))
    text2_tokens = nltk.word_tokenize(' '.join(texto2))
    #print("Token", text1_tokens)
    #print("Token", text2_tokens) 
    
    # Calcular la similitud semántica entre los sentidos
    #similitud = ' '.join(text1_tokens).wup_similarity(' '.join(text2_tokens))
    #return similitud

    #text1_synonyms = [obtener_sinonimo(word) for word in text1_tokens] 
    #text2_synonyms = [obtener_sinonimo(word) for word in text2_tokens]
    #print("Sinonimos", text1_synonyms)
    #print("Sinonimos", text2_synonyms)

    #text1_synonyms_flat = [syn for sublist in text1_tokens for syn in sublist]
    #text2_synonyms_flat = [syn for sublist in text2_tokens for syn in sublist]
    
    #print("Sinonimos flat", text1_synonyms_flat)    
    #print("Sinonimos flat", text2_synonyms_flat)

    texts = [' '.join(text1_tokens), ' '.join(text2_tokens)]
    #vectorizer = CountVectorizer()
    #X = vectorizer.fit_transform(texts)

    # Calcular la similitud coseno
    #similarity = cosine_similarity(X[0:1], X)
    #print(similarity)
    #return similarity[0][1]
    
    #print(text1_synonyms_flat, text2_synonyms_flat)
    #texts = [texto1, texto2]
    ''' 
    model = Word2Vec(texts, window=5, min_count=1, workers=4)
    
    similarity = 0.0
    for word1 in text1_tokens:
        for word2 in text2_tokens:
            if word1 in model.wv and word2 in model.wv:
                similarity += model.wv.similarity(word1, word2)
    similarity = similarity / (len(text1_tokens) * len(text2_tokens))
    return 1 - similarity

    '''
    similarity = 1 - jaccard_distance(set(text1_tokens), set(text2_tokens))
    return similarity


def cargarArray(jql, jql2):    
    jira = JIRA(options={'server': server}, basic_auth= (email, api_token))
    jira_issues_rebotes = jira.search_issues(jql,maxResults=0) 
    jira_issues_rebotes2 = jira.search_issues(jql2,maxResults=0) 
    
    dataTodas = {}
    dataTodas['todas'] = [] 

    dataTodas2 = {}
    dataTodas2['todas'] = [] 

    mensaje = ""  

    for issue in jira_issues_rebotes:
            try:
                dataTodas['todas'].append({
                'key': issue.key,
                'status' : str(issue.fields.status.name),                
                'summary': str(issue.fields.summary  ),
                'text': str(issue.fields.description  ),
                'component': str(issue.fields.components[0])}) 
            except:
                 dataTodas['todas'].append({
                'key': issue.key,
                'status' : str(issue.fields.status.name), 
                'summary': str(issue.fields.summary  ),
                'text': str(issue.fields.description  ),
                'component': str(issue.fields.components[0])})  

    for issue in jira_issues_rebotes2:
            try:
                dataTodas2['todas'].append({
                'key': issue.key,
                'status' : str(issue.fields.status.name),
                'summary': str(issue.fields.summary  ), 
                'text': str(issue.fields.description  ),
                'component': str(issue.fields.components[0])}) 
            except:
                 dataTodas2['todas'].append({
                'key': issue.key,
                'status' : str(issue.fields.status.name), 
                'summary': str(issue.fields.summary  ),
                'text': str(issue.fields.description  ),
                'component': str(issue.fields.components[0])}) 

    for j in dataTodas['todas']:
        comienzaAnalisis = True
        for i in dataTodas2['todas']:
            if not j.get('key', None) == i.get('key', None): 
                visto = False
                if j.get('component', None) == i.get('component', None):
                    similarity = calcularSimilitud( j.get('summary',None) , i.get('summary', None)  )
                    
                    if(similarity * 100  > 24):
                        if(comienzaAnalisis):
                            mensaje = "OJO! Para el Jira " + j.get('key', None) + " parece que hay algunos tickets que pueden hablar de lo mismo:"
                            client.chat_postMessage(channel='#pruebamati',text= mensaje )
                            comienzaAnalisis = False
                    
                        print(f"- " + i.get('key', None) + "(" + "{0:.0f}%".format(similarity * 100) + ")")
                        mensaje = "- " + i.get('key', None)
                        client.chat_postMessage(channel='#pruebamati',text= mensaje )
                        visto = True 
                        # mensaje = mensaje + " " +  i.get('key', None) + "(" + str(similarity * 100) + "%)" +  i.get('component', None)
                

                    if not visto:
                        similarity = calcularSimilitud( j.get('text',None) , i.get('text', None)  )

                        if(similarity * 100  > 24):
                            if(comienzaAnalisis):
                                mensaje = "OJO! Para el Jira " + j.get('key', None) + " parece que hay algunos tickets que pueden hablar de lo mismo:"
                                client.chat_postMessage(channel='#pruebamati',text= mensaje )
                                print(f"OJO! Para el Jira {j.get('key', None)} parece que hay algunos tickets similares:")
                                comienzaAnalisis = False
                    
                            print(f"- " + i.get('key', None) + "(" + "{0:.0f}%".format(similarity * 100) + ")")
                            mensaje = "- " + i.get('key', None)
                            client.chat_postMessage(channel='#pruebamati',text= mensaje )
                        # mensaje = mensaje + " " +  i.get('key', None) + "(" + str(similarity * 100) + "%)" +  i.get('component', None)
                
    #print(mensaje)
    #client.chat_postMessage(channel='#pruebamati',text= mensaje )
    


def obtenerTesteadoDesarrollado(dia, sprint, semanasParaAtras, web, mobile):     
    dataTotal = {}
    dataTotal['todo'] = [] 
    jql = 'created >= -2d AND project = RT AND issuetype = Bug ORDER BY created DESC' 
    jql2 = 'created >= -360d AND project = RT AND issuetype = Bug ORDER BY created DESC'

    #jql = 'Key in (RT-10549, RT-10456, RT-10926, RT-10354)' 
    #jql2 = 'Key in (RT-10549, RT-10456, RT-10926, RT-10354)' 
    cargarArray(jql, jql2)
 
   
# Settings
email = 'matias.vega@real-trends.com'           # Jira username
api_token = "ATATT3xFfGF0HIxsCT3LmVwtLZuEChBCRu_AOHu5jPglDMbfxbnMlgCim1ENimMA14TwPoIid68tOfz1CM7ra92EGAzDMGrjZ-7atuIaZGXrPxMCoWun2LdI-JqRri1GWWFK7zYWpNMwAFgNfT5vriXvLSPmwH07zrBO6pMOjlrKPsAVTJLiitg=6BC9A935"
server = 'https://realtrends.atlassian.net/'     # Jira server URL 

# Activo desde cuando quiero ejecutar el programa y cuantas semanas para atras quiero tomar el calculo
semanas = dt.datetime(2023, 2, 26, 1, 0)  # Lo quiero ejecutar desde ahora  
obtenerTesteadoDesarrollado(semanas , 92, 26 , True, True)


