from flask import Flask, render_template
from file_firestore import *
import datetime 
from datetime import date, timedelta

app = Flask(__name__)
db_dao = Classe_firestore()


def last_week():
    today = datetime.datetime.today()
    return [x.strftime("%d")+ "-" + x.strftime("%m") + "-" + x.strftime("%Y") for x in [today - timedelta(days=d) for d in range(6, -1, -1)]]

@app.route('/mensa', methods=['GET']) 
def get_last_week():
    documents = db_dao.get_elements()
    date_list = []
    pasti_list = []
    for d in last_week():
        date_pasti = []
        for doc in documents:
            if doc.endswith(d):
                date_list.append(d)
                date_pasti.append(db_dao.get_element_by_name(doc)["pasti"])
        if len(date_pasti) > 0:
            pasti_list.append(sum(date_pasti))
    return render_template("report.html", date_list=set(date_list), pasti_list=pasti_list, zip=zip)

@app.route('/mensa/<data>', methods=['GET'])
def nome_della_funzione(data):
    documents = db_dao.get_elements()
    asili_list = []
    pasti_list = []
    for doc in documents:
        if doc.endswith(data):
            asili_list.append(doc[:-len("_00-00-0000")])
            pasti_list.append(db_dao.get_element_by_name(doc)["pasti"])
    return render_template("details.html", date=data, ordini=sum(pasti_list), asili_list=asili_list, pasti_list=pasti_list, zip=zip)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)