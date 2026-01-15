from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS
from file_firestore import *

app = Flask(__name__)
CORS(app)
api=Api(app)
db_dao = Classe_firestore()

# Indicato all'interno di dettagli_api.yaml
basePath = '/api/v1'

def validate(d):
    # Check presence of parameters
    for key in ['firstName', 'lastName']:
        if key not in d.keys():
            print("BAD_KEY")
            return False
    
    # Check values
    if not isinstance(d['firstName'], str) or len(d['firstName']) == 0:
        print("BAD_FIRSTNAME")
        return False
    if not isinstance(d['lastName'], str) or len(d['lastName']) == 0:
        print("BAD_LASTNAME")
        return False
    if not isinstance(d['email'], str) or '@' not in d['email']:
        print("BAD_EMAIL")
        return False

    return True


class Resource_UNO(Resource):
    def get(self, email):
        if not isinstance(email, str) or '@' not in email:
            return {"message": "Generic error"}, 400

        d = db_dao.email_validate(email)
        if d is None:
            return {"message": "Not found"}, 404

        obj = {"fromEmail": d['giver']['email'], "fromFirstName": d['giver']['firstName'], "fromLastName": d['giver']['lastName'], "toEmail": d['receiver']['email'], "toFirstName": d['receiver']['firstName'], "toLastName": d['lastName']['email']}
        return obj, 200
    
    def post(self, email):
        d = request.json
        d['email'] = email

        if not validate(d):
            return {"message": "Generic error"}, 400

        if db_dao.email_validate(email) is not None:
            return {"message": "Conflict"}, 409
        
        data = {"giver": {"email": email, "firstName": d['firstName'], "lastName": d['lastName']}, "receiver": {}}
        
        db_dao.add_element(data)

        obj = {"firstName": d['firstName'], "lastName": d['lastName']}
        return obj, 200

api.add_resource(Resource_UNO, f'{basePath}/santa/<string:email>')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)