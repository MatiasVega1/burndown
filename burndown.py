from jira import JIRA
from datetime import timedelta
import datetime as dt

import xlsxwriter
import pandas as pd

def last_day(d, day_name):
    days_of_week = ['sunday','monday','tuesday','wednesday',
                        'thursday','friday','saturday']
    target_day = days_of_week.index(day_name.lower())
    delta_day = target_day - d.isoweekday()
    if delta_day >= 0: delta_day -= 7 # go back 7 days
    return d + timedelta(days=delta_day)

def cargarArray(jql):    
    jira = JIRA(options={'server': server}, basic_auth= (email, api_token))
    jira_issues_rebotes = jira.search_issues(jql,maxResults=0) 
    
    dataTodas = {}
    dataTodas['todas'] = [] 
    cantidad = 0
    puntos = 0

    for issue in jira_issues_rebotes:
            try:
                dataTodas['todas'].append({
                'key': issue.key,
                'status' : str(issue.fields.status.name), 
                'label': str(issue.fields.labels ),
                'puntos2': str(issue.fields.customfield_10014)})
            except:
                 dataTodas['todas'].append({
                'key': issue.key,
                'status' : str(issue.fields.status.name), 
                'label': str(issue.fields.labels ),
                'puntos2': 0}) 

    contSinEstimar = 0

    for j in dataTodas['todas']:
            if(j.get('puntos2', None) != "None"):
                #print(j.get('key'), " puntos: ",float(j.get('puntos2', None) ))                
                puntos = puntos + float(j.get('puntos2', None))
                cantidad += 1
            elif(j.get('puntos2', None) == "None"):
                cantidad += 1
                contSinEstimar += 1

    #rint("Ya paso el for")
    return  cantidad, puntos

def obtenerTesteadoDesarrollado(dia, sprint, semanasParaAtras, web, mobile):    
    print("Arranco")
    cont = 0  
    proximo = dia
    
    #Create Excel file
    row = 0
    col = 1 
    
    workbook = xlsxwriter.Workbook('sprint' + sprint + '.xlsx')

    header = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D8E4BC'})
    center = workbook.add_format({'align': 'center'})
    #formRebote = workbook.add_format({'bg_color': '#e08b8b' })
    #formOk = workbook.add_format({'bg_color': '#5fe371' })
    #formTotal = workbook.add_format({'bg_color': '#5fcfe3' })
    #formDesarrollado =  workbook.add_format({'bg_color': '#d15fe3' })

    #Suma las columnas
    worksheet = workbook.add_worksheet('Summary')
    estados = ('To Do','In Progress', 'Blocked', 'Review', 'Review Approved', 'TO MERGE',  'Ready for Test' , 'Testing', 'Done', 'Resolved')
       
    for e in estados:
            worksheet.write(row, col, e) 
            col += 1  
    row += 1 

    dataTotal = {}
    dataTotal['todo'] = [] 

    cantidadTickets = 0
    cantidadPdHWorked = 0 
    cantidadPdHTesteados = 0
    backlogTerminadoNoRework = 0 
    
    while(cont < 15): 
        y = dia  + timedelta(days= cont) 
        worksheet.write(row, 0, y.strftime("%Y/%m/%d"))  

        col = 1
       
        for e in estados:
            jql = 'project = RT AND Sprint = "RT Meli Sprint #' + sprint + '" and status was "' + e + '" ON "'+ y.strftime("%Y/%m/%d") + ' 19:00" and type IN ("Feature","Bug","Deuda Técnica")  ORDER BY issuetype DESC'
            
            cantTestWebRebote, puntosTestWebRebote = cargarArray(jql)

            worksheet.write(row, col, puntosTestWebRebote) 


            cantidadTickets += cantTestWebRebote
            #print("Escribio",puntosTestWebRebote )
            col += 1
        row += 1 

        cont = cont + 1
    
    print("Cantidad de Tickets:", cantidadTickets)
    workbook.close() 
    return 1
   
# Settings
email = 'matias.vega@real-trends.com'           # Jira username
api_token = "" 
server = 'https://realtrends.atlassian.net/'     # Jira server URL 

# Activo desde cuando quiero ejecutar el programa y cuantas semanas para atras quiero tomar el calculo
semanas = dt.datetime(2023, 2, 26, 1, 0)  # Lo quiero ejecutar desde ahora 
#delta = timedelta(days=5) 
#print(semanas.strftime("%Y/%m/%d"))
obtenerTesteadoDesarrollado(semanas , 92, 26 , True, True) 
print("Termino")