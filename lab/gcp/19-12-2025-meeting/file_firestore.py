from google.cloud import firestore
import json

class Classe_firestore(object):
    def __init__(self):
        self.db = firestore.Client(database="meeting")
        self.populate_db('db.json')
    
    # Aggiunta di nuovi dati
    def add_element(self, dic):
        colors_ref=self.db.collection('meeting_crimes')
        colors_ref.document(dic['data'] + "_" + dic['colpevole']).set({"data": dic['data'], "colpevole": dic['colpevole'], "vittime": dic['vittime'], "durata": dic['durata'], "orario_inizio": dic['orario_inizio']})

    # Richiesta per un singolo dato
    def get_element_by_name(self, DOCUMENT_NAME):
        c = self.db.collection('meeting_crimes').document(DOCUMENT_NAME).get()
        rv = c.to_dict() if c.exists else None
        return rv
    
    # Richiesta per tutti i dati
    def get_elements(self):
        return [str(c.id) for c in self.db.collection('meeting_crimes').stream()]
    
    def get_elements_obj(self):
        return [c for c in self.db.collection('meeting_crimes').stream()]
    
    def delete_element_by_name(self, DOCUMENT_NAME):
        self.db.collection('meeting_crimes').document(DOCUMENT_NAME).delete()

    # Per popolare il db ogni volta che creiamo un oggetto 
    def populate_db(self, filename):
        with open(filename) as f:
            data_list = json.load(f)
            for data in data_list:
                self.add_element(data)
