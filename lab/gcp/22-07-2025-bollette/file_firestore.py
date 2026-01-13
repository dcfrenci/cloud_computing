from google.cloud import firestore
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta


def get_year(date):
    return datetime.strptime(date, '%d-%m-%Y').strftime("%Y")

def get_month(date):
    return datetime.strptime(date, '%d-%m-%Y').strftime("%m")

def get_day(date):
    return datetime.strptime(date, '%d-%m-%Y').strftime("%d")

class Classe_firestore(object):
    def __init__(self):
        self.db = firestore.Client(database="bollette")
        self.populate_db('db.json')
        self.calculate_bollette()
    
    # Aggiunta di nuovi dati
    def add_element(self, DOCUMENT_NAME, data):
        colors_ref=self.db.collection('letture')
        colors_ref.document(DOCUMENT_NAME).set(data)

    # Richiesta per un singolo dato
    def get_element_by_name(self, DOCUMENT_NAME):
        c = self.db.collection('letture').document(DOCUMENT_NAME).get()
        rv = c.to_dict() if c.exists else None
        return rv
    
    # Richiesta per tutti i dati
    def get_elements(self):
        return [str(c.id) for c in self.db.collection('letture').stream()]
    
    def delete_element_by_name(self, DOCUMENT_NAME):
        self.db.collection('letture').document(DOCUMENT_NAME).delete()

    # Per popolare il db ogni volta che creiamo un oggetto 
    def populate_db(self, filename):
        with open(filename) as f:
            data_list = json.load(f)
            for data in data_list:
                self.add_element(data['data'], data)


    def add_bollette(self, DOCUMENT_NAME, data):
        colors_ref=self.db.collection('bollette')
        colors_ref.document(DOCUMENT_NAME).set(data)

    def get_bollette(self):
        return [str(c.id) for c in self.db.collection('bollette').stream()]
    
    def get_bolletta_by_name(self, DOCUMENT_NAME):
        c = self.db.collection('bollette').document(DOCUMENT_NAME).get()
        rv = c.to_dict() if c.exists else None
        return rv

    def calculate_bollette(self):
        letture = {}
        for doc in self.get_elements():
            d = self.get_element_by_name(doc)
            data = d['data']
            year, month, day = get_year(data), get_month(data), get_day(data)
            if year in letture.keys():
                if month in letture[year].keys():
                    letture[year][month][day] = d['value']
                else:
                    letture[year][month] = {day: d['value']}
            else:
                letture[year] = {month: {day: d['value']}}


        bollette = {}
        for year in letture.keys():
            for month in letture[year].keys():            
                bollette[year] = {'consumi': sum(letture[year][month].values())}
                bollette[year]['ultima_lettura'] = list(letture[year][month].keys())[-1]
                name = datetime.strptime(month + "-" + year, "%m-%Y") + relativedelta(months=1)
                bollette[year]['data'] = month + "-" + year

                self.add_bollette(name.strftime("%m-%Y"), bollette[year])