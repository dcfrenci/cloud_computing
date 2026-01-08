from google.cloud import firestore
import json
from datetime import date, timedelta, datetime

class Classe_firestore(object):
    def __init__(self):
        self.db = firestore.Client(database="mensa")
        self.populate_db('db.json')

    def helper(self, dat):
        mean = 0
        for d_week in [x.strftime("%d-%m-%Y") for x in [datetime.strptime(dat, '%d-%m-%Y') - timedelta(days=d) for d in range(6, -1, -1)]]:
            v = self.get_report_by_name(d_week) 
            mean += v["pasti"] if v is not None else 0
        return mean / 7

    # Aggiunta di nuovi dati
    def add_element(self, data, pasti):
        colors_ref=self.db.collection('mense')
        colors_ref.document(data["name"] + "_" + data["data"]).set({"pasti": pasti})

        c_ref = self.db.collection('riepiloghi')
        c = c_ref.document(data["data"]).get()
        mean_week = self.helper(data["data"])
        if c.exists:
            rv = c.to_dict()
            rv["asili"].append(data["name"])
            rv["pasti"] += pasti
            rv["trend"] = ((rv["pasti"] - mean_week) / mean_week) * 100 if mean_week > 0 else 0
        else:
            trend = ((pasti - mean_week) / mean_week) * 100 if mean_week > 0 else 0
            rv = {"pasti" : pasti, "asili" : [data["name"]], "trend" : trend}
        c_ref.document(data["data"]).set(rv)

    # Richiesta per un singolo dato)
    def get_element_by_name(self, DOCUMENT_NAME):
        c = self.db.collection('mense').document(DOCUMENT_NAME).get()
        rv = c.to_dict() if c.exists else None
        return rv
    
    def get_report_by_name(self, DOCUMENT_NAME):
        c = self.db.collection('riepiloghi').document(DOCUMENT_NAME).get()
        rv = c.to_dict() if c.exists else None
        return rv
    
    # Richiesta per tutti i dati nella collection
    def get_elements(self):
        return [str(c.id) for c in self.db.collection('mense').stream()]
    
    def get_reports(self):
        return [str(c.id) for c in self.db.collection('riepiloghi').stream()]
    
    def delete_element_by_name(self, DOCUMENT_NAME):
        self.db.collection('mense').document(DOCUMENT_NAME).delete()

    # Per popolare il db ogni volta che creiamo un oggetto 
    def populate_db(self, filename):
        with open(filename) as f:
            data_list = json.load(f)
            for data in data_list:
                self.add_element(data, data["pasti"])

if __name__ == "__main__":
    obj = Classe_firestore()
    