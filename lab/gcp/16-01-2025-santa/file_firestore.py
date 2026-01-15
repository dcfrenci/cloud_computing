from google.cloud import firestore
import json
import copy



class Classe_firestore(object):
    def __init__(self):
        self.db = firestore.Client(database="santa")
        self.populate_db('db.json')
    
    # Aggiunta di nuovi dati
    def add_element_complete(self, DOCUMENT_NAME, data):
        collection = self.db.collection('secret_santa')
        collection.document(DOCUMENT_NAME).set(data)

    def add_element(self, data):
        doc = self.get_elements()
        last_member_name = sorted(doc, key=lambda x: int(x.split('_')[-1]))[-1]
        last_member = self.get_element_by_name(last_member_name)
        data['receiver'] = copy.deepcopy(last_member['receiver'])
        last_member['receiver'] = data['giver']
        self.db.collection('secret_santa').document(last_member_name).set(last_member)
        i = int(last_member_name.split('_')[-1]) + 1
        self.db.collection('secret_santa').document("partecipante_" + str(i)).set(data)

    # Richiesta per un singolo dato
    def get_element_by_name(self, DOCUMENT_NAME):
        c = self.db.collection('secret_santa').document(DOCUMENT_NAME).get()
        rv = c.to_dict() if c.exists else None
        return rv
    
    # Richiesta per tutti i dati
    def get_elements(self):
        return [str(c.id) for c in self.db.collection('secret_santa').stream()]
    
    def delete_element_by_name(self, DOCUMENT_NAME):
        self.db.collection('secret_santa').document(DOCUMENT_NAME).delete()

    # Per popolare il db ogni volta che creiamo un oggetto 
    def populate_db(self, filename):
        with open(filename) as f:
            data_list = json.load(f)
            for data, i in zip(data_list, range(len(data_list))):
                self.add_element_complete("partecipante_" + str(i), data)

    def email_validate(self, email):
        docs = self.get_elements()
        for doc in docs:
            d = self.get_element_by_name(doc)
            if d['giver']['email'] == email:
                return d
        return None