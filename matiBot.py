from jira import JIRA 
import slack


SLACK_TOKEN = ""

client = slack.WebClient(token=SLACK_TOKEN)

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
api_token = "-7atuIaZGXrPxMCoWun2LdI-"
server = 'https://realtrends.atlassian.net/'     # Jira server URL 

# Activo desde cuando quiero ejecutar el programa y cuantas semanas para atras quiero tomar el calculo
semanas = dt.datetime(2023, 2, 26, 1, 0)  # Lo quiero ejecutar desde ahora  
obtenerTesteadoDesarrollado(semanas , 92, 26 , True, True)


