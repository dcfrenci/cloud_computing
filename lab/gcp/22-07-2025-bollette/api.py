from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS
from file_firestore import *
from datetime import datetime

app = Flask(__name__)
CORS(app)
api=Api(app)
db_dao = Classe_firestore()

# Indicato all'interno di dettagli_api.yaml
basePath = '/api/v1'

def date_from_str(d):
    try: return datetime.strptime(d, '%d-%m-%Y')
    except: return None

def validate(dic):
    for key in ['value']:
        if key not in dic.keys():
            print("KEY_NOT")
            return False

    if not isinstance(dic['value'], int):
        print("VALUE_NOT")
        return False

    if date_from_str(dic['data']) is None:
        print("DATE_NOT")
        return False

    return True

class Resource_Gas(Resource):

    def get(self, data):
        if date_from_str(data) is None:
            return None, 400
        
        if db_dao.get_element_by_name(data) is None:
            l = sorted(db_dao.get_elements(), key=lambda x: datetime.strptime(x, "%d-%m-%Y"))
            l = list(filter(lambda y: datetime.strptime(y, "%d-%m-%Y") < datetime.strptime(data, "%d-%m-%Y"), l))[-2:]
            value = 0
            if len(l) != 2:
                value = datetime.strptime(l[0], "%d-%m-%Y").strftime("%d")
            else:
                c1, c2 = datetime.strptime(l[0], "%d-%m-%Y").day, datetime.strptime(l[0], "%d-%m-%Y").day
                t1, t2, tx = datetime.strptime(l[0], "%d-%m-%Y"), datetime.strptime(l[1], "%d-%m-%Y"), datetime.strptime(data, "%d-%m-%Y")
                value = c2 - ((c2 - c1) / (t2 - t1).total_seconds()) * (tx - t2).total_seconds()
            obj = {"value" : value, "isInterpolated": True}
            return obj, 200
        
        d = db_dao.get_element_by_name(data)
        obj = {"value" : d['value'], "isInterpolated": True}
        return obj, 200
    
    def post(self, data):
        dic = request.json
        dic['data'] = data

        print(dic)

        if not validate(dic):
            return None, 400
        
        if db_dao.get_element_by_name(dic['data']) is not None:
            return None, 409
        
        db_dao.add_element(dic['data'], {'value': dic['value']})

        obj = {"value" : dic['value'], "isInterpolated": True}
        return obj, 201
    
api.add_resource(Resource_Gas, f'{basePath}/gas/<string:data>')

class Resource_Clean(Resource):
    def get(self):
        for doc in db_dao.get_elements():
            db_dao.delete_element_by_name(doc)
        return None, 200

api.add_resource(Resource_Clean, f'{basePath}/clean')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)