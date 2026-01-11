from google.cloud import firestore
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

db = firestore.Client(database="mensa")

def update_report(data, context):
    print("TESTINGGGGGGG")
    data = data['value']
    print(data)

    return 
    c_ref = db.collection('riepiloghi')
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

@app.route('/trend/<data>', methods=['GET']) 
def get_trend(data):
    document = db.collection('riepiloghi').document(data).get()
    if not document.exists:
        return {}, 400
    document = document.to_dict()
    return {"trend": document["trend"]}, 200


@app.route('/api/v1/trend/<data>', methods=['GET'])
def get_api_trend(data):
    document = db.collection('riepiloghi').document(data).get()
    if not document.exists:
        return {}, 400
    document = document.to_dict()
    return {"trend": document["trend"]}, 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)