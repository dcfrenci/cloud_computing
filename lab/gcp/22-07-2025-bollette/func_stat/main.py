from google.cloud import firestore
from datetime import datetime
from dateutil.relativedelta import relativedelta

db = firestore.Client(database="bollette")

def get_year(date):
    return datetime.strptime(date, '%d-%m-%Y').strftime("%Y")

def get_month(date):
    return datetime.strptime(date, '%d-%m-%Y').strftime("%m")

def get_day(date):
    return datetime.strptime(date, '%d-%m-%Y').strftime("%d")

def EVENT_FUNCTION(data, context):
    document = data['value']['fields']
    old_document = data['oldValue']['fields'] if len(data['oldValue']) != 0 else None 

    consumi = 0
    
    print("TESTING: DOCUMENT")
    print(document)
    print("TESTING: DOCUMENT")
    print(old_document)

    if old_document is not None:
        consumi -= old_document['consumi']
        
    consumi += document['consumi']
    

    value = context.params['KEY']
    document_name = context.resource.split('/')[-1]

    # update / create bolletta

    year, month, day = get_year(document['data']), get_month(document['data']), get_day(document['data'])
    data = datetime.strptime(month + "-" + year, "%m-%Y")
    name = data + relativedelta(months=1)
    bolletta = db.collection('bollette').document(name.strftime("%m-%Y")).get()
    
    if bolletta.exists:
        bolletta = bolletta.to_dict()
        
        if day > bolletta['ultima_lettura']:
            bolletta['ultima_lettura'] = day
        bolletta['consumi'] = consumi

    else: 
        bolletta = {'consumi': consumi, 'data': data.strftime("%m-%Y"), 'ultima_lettura': day}

    db.collection('bollette').document(name.strftime("%m-%Y")).put(bolletta)
