from flask import Flask, request
from flask_restful import Resource, Api
from file_firestore import *
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
api=Api(app)
db_dao = Classe_firestore()

# Indicato all'interno di dettagli_api.yaml
basePath = '/api/v1'

class Mensa(Resource):
    def validate(data):
        if len(data) != 'DD-MM-YYYY':
            return False
        p = [int(l) for l in str.split(data, '-')]
        if len(p) != 3:
            return False
        return 0 < p[0] < 32 and 0 < p[1] < 13 and 0 < p[2]
            

    def get(self, data):
        if not self.validate(data):
            return None, None, 400
        documents = [doc for doc in db_dao.get_elements() if doc.endswith(data)]
        tot_pasti = 0
        asili_list = []
        for doc in documents:
            tot_pasti += db_dao.get_element_by_name(doc)["pasti"]
            asili_list.append(doc[:len(doc)-len(data)])

        return tot_pasti, asili_list, 200

    # nome asilo != None and n° pasti > 0 
    def post(self, data):
        if not self.validate(data):
            return 400
        d = request.json
        if not isinstance(d["asilo"], (str)) or len(d["asilo"]) < 1:
            return None, 409
        if db_dao.get_element_by_name(d["asilo"] + '_' + data) is not None:
            return None, 409
        if not isinstance(d["pasti"], (int)) or d["pasti"] < 1:
            return None, 400
        db_dao.add_element(d["asilo"] + '_' + data, d["pasti"])
        return None, 201

    def put(self, data):
        if not self.validate(data):
            return 400
        d = request.json
        if not isinstance(d["asilo"], (str)) or len(d["asilo"]) < 1:
            return None, 400
        if not isinstance(d["pasti"], (int)) or d["pasti"] < 1:
            return None, 400
        if db_dao.get_element_by_name(d["asilo"] + '_' + data) is None:
            return None, 404
        db_dao.add_element(d["asilo"] + '_' + data, d["pasti"])
        return None, 200
    
    
api.add_resource(Mensa, f'{basePath}/mensa/<string:data>')

class Clean(Resource):
    def post(self):
        for doc in db_dao.get_elements():
            db_dao.delete_element_by_name(doc)
        return None, 200

api.add_resource(Clean, f'{basePath}/clean')

