from jira import JIRA
from datetime import *

def estaCerrado(status):
    if( status == 'Finalizada' or 
        status == 'Cerrada' or 
        status == 'Rejected' or 
        status == 'Resuelta' or 
        #El status freezado aún no defini si lo quiero sumar o no (por ahora, si)
        status == 'Freezado'): 
        return True
    else:
        return False
     
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

    #print(jira_issues)

    for issue in jira_issues_rebotes:
            dataTodas['todas'].append({
            'key': issue.key,
            'status' : str(issue.fields.status.name),
            'epica': str(issue.fields.customfield_10033 ),
            'label': str(issue.fields.labels ),
            'puntos2': str(issue.fields.customfield_10014 )})     

    for j in dataTodas['todas']:
            if(j.get('puntos2', None) != "None"):
                #print(j.get('key'))
                cantidad = cantidad + float(j.get('puntos2', None))

    return cantidad

def obtenerTesteadoDesarrollado(dia, semanasParaAtras, web, mobile):
    
    cont = 0 
    puntosTestTotal = 0
    puntosDevTotal = 0
    puntosTest = 0 
    puntosDev = 0 
    primeraVez = True
    ultimaVez = True
    proximo = dia
  
    while(cont < semanasParaAtras): 
        y = proximo  - timedelta(days=7)
        #print("Proximo: ", proximo)
        #print("y: ", y)
        strDias = "(\"" + y.strftime("%Y/%m/%d") + "\",\"" + proximo.strftime("%Y/%m/%d") + "\")"
        #print(strDias)

        if(web):
            testWebjql = 'project = RT and type IN ("feature", "bug") and (status changed FROM "Testing" TO "Done" by (6005c74fbd160e00750be7bd, 60fef89b0b454a00689d838c, 62266ef18a4bb60068f4a686)  DURING ' + strDias + ' OR status changed FROM "Testing" TO "To Do" by (6005c74fbd160e00750be7bd, 60fef89b0b454a00689d838c, 62266ef18a4bb60068f4a686) DURING ' + strDias + ') ORDER BY created DESC'
        
        if(mobile):
            testMobilejql = 'project = MOB and type IN ("feature", "bug") and (status changed FROM "Testing" TO "Done" by (6005c74fbd160e00750be7bd, 60fef89b0b454a00689d838c, 62266ef18a4bb60068f4a686)  DURING ' + strDias + ' OR status changed FROM "Testing" TO "To Do" by (6005c74fbd160e00750be7bd, 60fef89b0b454a00689d838c, 62266ef18a4bb60068f4a686) DURING ' + strDias + ') ORDER BY created DESC'
        
        if(web):
            devWebjql = 'project = RT and type IN ("feature", "bug") AND status was in ("To Do","In progress") during ' + strDias + ' AND status was in (review) during ' + strDias + ' ORDER BY assignee ASC, created DESC'
        
        if(mobile):
            devMobilejql = 'project = MOB and type IN ("feature", "bug") AND status was in ("To Do","In progress") during ' + strDias + ' AND status was in (review) during ' + strDias + ' ORDER BY assignee ASC, created DESC'

        
        proximo = y  
        #print("Proximo:", proximo)
        if(web):
            puntosTestWeb = cargarArray(testWebjql)
            puntosDevWeb = cargarArray(devWebjql)
        else:
            puntosTestWeb = 0
            puntosDevWeb = 0
        
        if(mobile):
            puntosTestMobile = cargarArray(testMobilejql)
            puntosDevMobile = cargarArray(devMobilejql) 
        else:
            puntosTestMobile = 0
            puntosDevMobile = 0
        
        if(not primeraVez):
            puntosTest = puntosTestWeb + puntosTestMobile
            puntosDev = puntosDevWeb + puntosDevMobile
        
    
        #print("Puntos Test:", puntosTest)
        #print("Puntos Dev:", puntosDev)

        if(ultimaVez and not primeraVez):
          print("Últimos Puntos QA: ", puntosTest)
          print("Últimos Puntos Dev: ", puntosDev)
          ultimaVez = False 

        primeraVez = False
        puntosTestTotal = puntosTestTotal + puntosTest 
        puntosDevTotal = puntosDevTotal + puntosDev
        cont = cont + 1
        print("Semana: ", cont)
    
    print("Promedio: ")
    print (puntosTestTotal / semanasParaAtras -1)
    print (puntosDevTotal / semanasParaAtras -1)
    return 1
   
# Settings
email = 'matias.vega@real-trends.com'           # Jira username
api_token = ""       # Jira API token
server = 'https://realtrends.atlassian.net/'     # Jira server URL 

# Activo desde cuando quiero ejecutar el programa y cuantas semanas para atras quiero tomar el calculo
semanas = datetime.now() # Lo quiero ejecutar desde ahora 
delta = timedelta(days=6) 
print(semanas.strftime("%Y/%m/%d"))
obtenerTesteadoDesarrollado(semanas + delta , 30, False, True)
