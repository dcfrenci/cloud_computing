from flask import Flask, render_template
from file_firestore import *

import datetime
from datetime import timedelta

app = Flask(__name__)
db_dao = Classe_firestore()

@app.route('/mappa', methods=['GET']) 
def mappa():
    t = {}
    h = {}
    documents = db_dao.get_elements()
    for day in [x.strftime("%Y-%m-%d") for x in [datetime.datetime.today() + timedelta(days=d) for d in range(6, -1, -1)]]:
        for doc in documents:
            if doc.startswith(day):
                d = db_dao.get_element_by_name(doc)
                if day in t.keys():
                    t[day] += d['durata']
                    h[day] += (d['durata'] * len(d['vittime']))
                else:
                    t[day] = d['durata']
                    h[day] = (d['durata'] * len(d['vittime']))
    today = datetime.datetime.today().strftime("%d-%m-%Y")
    today_f = datetime.datetime.today().strftime("%Y-%m-%d")
    today_h = t[today_f] if today_f in t.keys() else 0
    return render_template("mappa_della_follia.html", day_list=[datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%d-%m-%Y") for d in t.keys()], hour_list=h.values(), today=today, today_h=today_h, mh_wasted=sum(t.values()), zip=zip)

@app.route('/mappa/<data>', methods=['GET'])
def mappa_data(data):
    data = datetime.datetime.strptime(data, "%d-%m-%Y").strftime("%Y-%m-%d")
    riunioni_list = []
    today_h = 0
    longest = 0
    dannato = ""
    for doc in db_dao.get_elements():
        if doc.startswith(data):
            d = db_dao.get_element_by_name(doc)
            riunioni_list.append(d)
            today_h += d['durata']
            if d['durata'] > longest:
                longest = d['durata']
                dannato = d['colpevole']
    return render_template("sala_riunioni_42.html", riunioni_list=riunioni_list, today_h=today_h, dannato=dannato)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)