from flask import Flask, render_template
from file_firestore import *
from datetime import datetime, timedelta

app = Flask(__name__)
db_dao = Classe_firestore()


@app.route('/bollette', methods=['GET'])
def nome_della_funzione():
    bollette = db_dao.get_bollette()
    bollette.sort(key=lambda x: datetime.strptime(x, "%m-%Y"))
    return render_template("last_year_bollette.html", bollette=bollette[-12:])


@app.route('/bollette/<data>', methods=['GET'])
def fun(data):
    bolletta = db_dao.get_bolletta_by_name(data)
    bolletta_l = "01-" + data
    data = bolletta['data']
    mese = datetime.strptime(data, "%m-%Y").strftime("%B")
    data_l = bolletta['ultima_lettura'] + "-" + data
    value = db_dao.get_element_by_name(data_l)['value']
    consumi = bolletta['consumi']

    return render_template("bolletta.html", bolletta=bolletta_l, mese=mese, data=data_l, value=value, consumi=consumi)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)