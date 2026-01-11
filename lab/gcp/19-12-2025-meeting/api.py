from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS
from file_firestore import *

from datetime import datetime
from operator import attrgetter

app = Flask(__name__)
CORS(app)
api=Api(app)
db_dao = Classe_firestore()

# Indicato all'interno di dettagli_api.yaml
basePath = '/api/v1'


def date_from_str(d):
    """converte 'gg-mm-YYYY' in oggetto datetime"""
    try:
        return datetime.strptime(d, '%d-%m-%Y')
    except:
        return None
    
def str_from_date(d):
    """converte oggetto datetime in 'gg-mm-YYYY'"""
    return d.strftime('%d-%m-%Y')

def time_from_str(t):
    """converte 'HH:MM' in oggetto time"""
    try:
        return datetime.strptime(t, '%H:%M').time()
    except:
        return None

def calculate_end_time(start_time, duration):
    """Calcola l'orario di fine dato l'orario di inizio e la durata"""
    try:
        # Converti in minuti
        start_minutes = start_time.hour * 60 + start_time.minute
        end_minutes = start_minutes + int(duration * 60)
        # Converti di nuovo in time
        end_hour = end_minutes // 60
        end_minute = end_minutes % 60
        return time_from_str(str(end_hour) + ":" + str(end_minute))
    except ValueError:
        return None

def parse_month(month_str):
    """Converte un mese da MM-YYYY a datetime"""
    try:
        return datetime.strptime(month_str, '%m-%Y')
    except ValueError:
        return None
    
def occupied(dic):
    start = time_from_str(dic['orario_inizio'])
    end = calculate_end_time(start, dic['durata'])
    for document in db_dao.get_elements():
        if document == dic['data'] + "_" + dic['colpevole']:
            continue
        if document.startswith(dic['data']):
            p = db_dao.get_element_by_name(document)
            p_start = time_from_str(p['orario_inizio'])
            p_end = calculate_end_time(p_start, p['durata'])
            if p_start <= start < p_end or p_start < end < p_end:
                return True
    return False

def validate(dictionary):
    # Dati mancanti
    for key in ['colpevole', 'vittime', 'durata', 'orario_inizio']:
        if key not in dictionary.keys():
            return False
    
    # Correttezza dei dati
    if not isinstance(dictionary['colpevole'], str) or len(dictionary['colpevole']) == 0:
        print("COLPEVOLE_NOT_OK")
        return False
    
    if len(dictionary['vittime']) + 1 >= 20 or len([vittima for vittima in dictionary['vittime'] if not isinstance(vittima, str)]) != 0:
        print("VITTIME_NOT_OK")
        return False
    
    if not isinstance(dictionary['durata'], float) and not isinstance(dictionary['durata'], int) or dictionary['durata'] % 0.5 != 0 or dictionary['durata'] < 0.5 or dictionary['durata'] > 8:
        print("DURATA_NOT_OK")
        return False
    
    if not isinstance(dictionary['orario_inizio'], str) or len(dictionary['orario_inizio']) != len("HH:MM") or time_from_str(dictionary['orario_inizio']) is None:
        print("ORARIO_NOT_OK")
        return False
    
    if dictionary['data'] is None:
        print("DATA_NOT_OK")
        return False
    
    return True


class Resource_room(Resource):
    
    def get(self, data):
        data = date_from_str(data).strftime("%Y-%m-%d")
        riunioni = {}
        totale_ore = 0
        dannato_del_giorno = ""
        dannato_ore = 0
        for document in db_dao.get_elements():
            if document.startswith(data):
                d = db_dao.get_element_by_name(document)
                riunioni[d['orario_inizio']] = d
                totale_ore += d['durata']
                if d['durata'] > dannato_ore:
                    dannato_ore = d['durata']
                    dannato_del_giorno = d['colpevole']
                    
        obj = {"data": data, "totale_ore": totale_ore, "dannato_del_giorno": dannato_del_giorno, "riunioni": list(riunioni.values())}
        return obj, 200
    
    def post(self, data):
        dic = request.json
        dic['data'] = date_from_str(data).strftime("%Y-%m-%d")
        
        if not validate(dic):
            return None, 400
        
        if db_dao.get_element_by_name(dic['data'] + "_" + dic['colpevole']) is not None:
            return None, 409
        
        if occupied(dic):
            return None, 422
        if time_from_str(dic['orario_inizio']) < time_from_str("08:00"):
            return None, 422
        if calculate_end_time(time_from_str(dic['orario_inizio']), dic['durata']) > time_from_str("20:00"):
            return None, 422
        
        db_dao.add_element(dic)
        obj = {"data": dic['data'], "colpevole": dic['colpevole'], "vittime": dic['vittime'], "durata": dic['durata'], "orario_inizio": dic['orario_inizio']}
        return obj, 201

    def put(self, data):
        dic = request.json
        dic['data'] = date_from_str(data).strftime("%Y-%m-%d")
        
        if not self.validate(dic):
            return None, 400
        
        if db_dao.get_element_by_name(dic['data'] + "_" + dic['colpevole']) is None:
            return None, 404
        
        if occupied(dic):
            return None, 422
        if time_from_str(dic['orario_inizio']) < time_from_str("08:00"):
            return None, 422
        if calculate_end_time(time_from_str(dic['orario_inizio']), dic['durata']) > time_from_str("20:00"):
            return None, 422
        
        db_dao.add_element(dic)
        obj = {"data": dic['data'], "colpevole": dic['colpevole'], "vittime": dic['vittime'], "durata": dic['durata'], "orario_inizio": dic['orario_inizio']}
        return obj, 200

api.add_resource(Resource_room, f'{basePath}/room42/<string:data>')


class Resource_panic(Resource):
    def post(self):
        for doc in db_dao.get_elements():
            db_dao.delete_element_by_name(doc)
        return None, 200

api.add_resource(Resource_panic, f'{basePath}/panic')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)