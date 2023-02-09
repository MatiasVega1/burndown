from jira import JIRA
from datetime import *

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

def obtenerTesteadoDesarrollado(dia, semanasParaAtras, web, mobile):    
    cont = 0  
    proximo = dia

    #Create Excel file
    row = 0
    col = 0
    
    workbook = xlsxwriter.Workbook('planilla.xlsx')

    header = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D8E4BC'})
    center = workbook.add_format({'align': 'center'})
    formRebote = workbook.add_format({'bg_color': '#e08b8b' })
    formOk = workbook.add_format({'bg_color': '#5fe371' })
    formTotal = workbook.add_format({'bg_color': '#5fcfe3' })
    formDesarrollado =  workbook.add_format({'bg_color': '#d15fe3' })
    
    #Suma las columnas
    worksheet = workbook.add_worksheet('Summary')
    worksheet.write(row, col, 'Inicio', header)
    worksheet.write(row, col + 1, 'Fin', header) 
    worksheet.write(row, col + 2, '# Tk. Web Rebotados' ,header) 
    worksheet.write(row, col + 3, 'Ptos. Web Rebotados' ,header) 
    worksheet.write(row, col + 4, '# Tk. Web Ok' ,header) 
    worksheet.write(row, col + 5, 'Ptos. Web Ok' ,header) 

    
    worksheet.write(row, col + 6, '# Tk. Web Test Total' ,header) 
    worksheet.write(row, col + 7, 'Ptos. Web Test Total' ,header) 

    worksheet.write(row, col + 8, '# Tk. Web Desarrollados' ,header) 
    worksheet.write(row, col + 9, 'Ptos. Web Desarrollados' ,header) 

    worksheet.write(row, col + 10, '# Tk. Mobile Rebotados' ,header) 
    worksheet.write(row, col + 11, 'Ptos. Mobile Rebotados' ,header) 
    worksheet.write(row, col + 12, '# Tk. Mobile Ok' ,header) 
    worksheet.write(row, col + 13, 'Ptos. Mobile Ok' ,header)  

    worksheet.write(row, col + 14, '# Tk. Mobile Test Total' ,header) 
    worksheet.write(row, col + 15, 'Ptos. Mobile Test Total' ,header)  

    worksheet.write(row, col + 16, '# Tk. Mobile Desarrollados' ,header) 
    worksheet.write(row, col + 17, 'Ptos. Mobile Desarrollados' ,header) 

    row += 1
    

    dataTotal = {}
    dataTotal['todo'] = [] 
    
    while(cont < semanasParaAtras): 
        y = proximo  - timedelta(days=7)
        strDias = "(\"" + y.strftime("%Y/%m/%d") + "\",\"" + proximo.strftime("%Y/%m/%d") + "\")" 
        #print(strDias)

        worksheet.write(row, col, y.strftime("%Y/%m/%d")) 
        worksheet.write(row, col + 1, proximo.strftime("%Y/%m/%d"))

        if(web):
            testWebjqlRebote = 'project = RT and status changed FROM "Testing" TO "To Do" by (6005c74fbd160e00750be7bd, 60fef89b0b454a00689d838c, 62266ef18a4bb60068f4a686) DURING ' + strDias + ' ORDER BY created DESC'
            testWebJqlOk = 'project = RT and status changed FROM "Testing" TO "Done" by (6005c74fbd160e00750be7bd, 60fef89b0b454a00689d838c, 62266ef18a4bb60068f4a686) DURING ' + strDias + '  ORDER BY created DESC'
            webDesarrollado = 'project = RT AND status changed from "To Do" to "In progress" during ' + strDias + ' and status changed from "In progress" to "Review" during ' + strDias + ' and status NOT IN ("In progress")  ORDER BY status DESC, created DESC'
        
        if(mobile):
            testMobilejqlRebote = 'project = MOB and status changed FROM "Testing" TO "To Do" by (6005c74fbd160e00750be7bd, 60fef89b0b454a00689d838c, 62266ef18a4bb60068f4a686) DURING ' + strDias + ' ORDER BY created DESC'
            testMobileJqlOk = 'project = MOB and status changed FROM "Testing" TO "Done" by (6005c74fbd160e00750be7bd, 60fef89b0b454a00689d838c, 62266ef18a4bb60068f4a686) DURING ' + strDias + '  ORDER BY created DESC'
            mobileDesarrollado = 'project = MOB AND status changed from "To Do" to "In progress" during ' + strDias + ' and status changed from "In progress" to "Review" during ' + strDias + ' and status NOT IN ("In progress")  ORDER BY status DESC, created DESC'

        proximo = y  
        
        if(web):
            cantTestWebRebote, puntosTestWebRebote = cargarArray(testWebjqlRebote)
            cantTestWebOk, puntosTestWebOk = cargarArray(testWebJqlOk)
            cantWebDesarrollado, puntosWebDesarrollado = cargarArray(webDesarrollado)
        else:
            cantTestWebRebote, puntosTestWebRebote = 0
            cantTestWebOk, puntosTestWebOk = 0
            cantWebDesarrollado, puntosWebDesarrollado = 0
        

        if(mobile):
            cantTestMobileRebote, puntosTestMobileRebote = cargarArray(testMobilejqlRebote)
            cantTestMobileOk, puntosTestMobileOk = cargarArray(testMobileJqlOk)
            cantMobileDesarrollado, puntosMobileDesarrollado = cargarArray(mobileDesarrollado)
        else:
            cantTestMobileRebote, puntosTestMobileRebote = 0
            cantTestMobileOk, puntosTestMobileOk = 0
            cantMobileDesarrollado, puntosMobileDesarrollado = 0
         
        worksheet.write(row, col + 2, cantTestWebRebote, formRebote )
        worksheet.write(row, col + 3, puntosTestWebRebote, formRebote )
        worksheet.write(row, col + 4, cantTestWebOk, formOk )
        worksheet.write(row, col + 5, puntosTestWebOk, formOk )
        
        worksheet.write(row, col + 6, cantTestWebOk + cantTestWebRebote, formTotal )
        worksheet.write(row, col + 7, puntosTestWebOk + puntosTestWebRebote , formTotal )

        worksheet.write(row, col + 8, cantWebDesarrollado, formDesarrollado ) 
        worksheet.write(row, col + 9, puntosWebDesarrollado, formDesarrollado )

        worksheet.write(row, col + 10, cantTestMobileRebote, formRebote )
        worksheet.write(row, col + 11, puntosTestMobileRebote, formRebote )
        worksheet.write(row, col + 12, cantTestMobileOk, formOk )
        worksheet.write(row, col + 13, puntosTestMobileOk, formOk ) 

        
        worksheet.write(row, col + 14, cantTestMobileOk + cantTestMobileRebote, formTotal )
        worksheet.write(row, col + 15, puntosTestMobileOk + puntosTestMobileRebote, formTotal ) 

        worksheet.write(row, col + 16, cantMobileDesarrollado, formDesarrollado ) 
        worksheet.write(row, col + 17, puntosMobileDesarrollado, formDesarrollado )  

        row += 1  
        cont = cont + 1
    
    workbook.close() 
    return 1
   
# Settings
email = 'matias.vega@real-trends.com'           # Jira username
api_token = ""       # Jira API token
server = 'https://realtrends.atlassian.net/'     # Jira server URL 

# Activo desde cuando quiero ejecutar el programa y cuantas semanas para atras quiero tomar el calculo
semanas = datetime.now() # Lo quiero ejecutar desde ahora 
delta = timedelta(days=3) 
print(semanas.strftime("%Y/%m/%d"))
obtenerTesteadoDesarrollado(semanas + delta , 10 , True, True) 