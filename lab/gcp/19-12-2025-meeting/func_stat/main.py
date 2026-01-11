from google.cloud import firestore
from flask import Flask, request
import datetime

db = firestore.Client(database="meeting")

def HTTP_FUNCTION(request):
    path = request.path
    pages = path.split('/')

    return 'STRING'

def EVENT_FUNCTION(data, context):
    document = data["value"]
    value = context.params["KEY"]
    document_name = context.resource.split('/')[-1]
    
    d = datetime.datetime.strptime(document['data'], "%Y-%m-%d").strftime("%m-%Y")
    
    c = db.collection('productivity_nightmare').document(d).get()
    partecipanti = document['vittime']
    partecipanti.append(document['colpevole'])
    dic = {}
    if c.exists:
        dic = c.to_dict()
        for partecipante in partecipanti:
            if partecipante in dic[d].keys():
                dic['dipendenti'][partecipante]['ore_riunioni'] += document['durata']
                dic['dipendenti'][partecipante]['efficienza'] = dic['dipendenti'][partecipante]['ore_riunioni'] / 160
            else:
                dic['dipendenti'][partecipante] = {"riunioni_organizzate": 0, "ore_riunioni": document['durata'], "efficienza": document['durata'] / 160}
            if dic['colpevole'] == partecipante:
                dic['dipendenti'][partecipante]['riunioni_organizzate'] += 1

    else:
        dic['mese'] = d.strftime("%B")
        dic['dipendenti'] = []
        for partecipante in partecipanti:
            dic['dipendenti'].append({partecipante: {"riunioni_organizzate": 0, "ore_riunioni": document['durata'], "efficienza": document['durata'] / 160}})
            if dic['colpevole'] == partecipante:
                    dic['dipendenti'][partecipante]['riunioni_organizzate'] += 1


    db.collection('productivity_nightmare').document(d).set(dic)
    