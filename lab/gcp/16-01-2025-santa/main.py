from flask import Flask, render_template, request
from file_firestore import *
from wtforms import Form, StringField, EmailField, SubmitField, validators

class Registration(Form):
    firstName =  StringField('Nome', [validators.DataRequired()])
    lastName =  StringField('Cognome', [validators.DataRequired()])
    email = EmailField('Email address', [validators.DataRequired(), validators.Email()])
    submit= SubmitField('Conferma inserimento')

class Finder(Form):
    email = EmailField('Email address', [validators.DataRequired(), validators.Email()])
    submit= SubmitField('Conferma richiesta')

app = Flask(__name__)
db_dao = Classe_firestore()


@app.route('/secretsanta', methods=['GET', 'POST'])
def function_base():
    return render_template("add_member.html", rform=Registration(), fform=Finder(), message_reg=None, message_find=None)


@app.route('/secretsanta/registration', methods=['POST'])
def function_specific():
    rform = Registration(request.form)
    d = db_dao.email_validate(rform.email.data)
    message = ""
    if d is not None:
        message = "Partecipante già inserito."
    else: 
        message = "Partecipante inserito: " + rform.firstName.data + " " + rform.lastName.data + " " + rform.email.data
        data = {"giver": {"email": rform.email.data, "firstName": rform.firstName.data, "lastName": rform.lastName.data}, "receiver": {}}    
        db_dao.add_element(data)
    return render_template("add_member.html", rform=Registration(), fform=Finder(), message_reg=message, message_fin=None)
    

@app.route('/secretsanta/finder', methods=['POST'])
def function_finder():
    fform=Finder(request.form)
    d = db_dao.email_validate(fform.email.data)
    message = ""
    if d is None:
        message = "Partecipante non trovato."
    else:
        message = "Il partecipante " + d['giver']['firstName'] + " " + d['giver']['lastName'] + " " + d['giver']['email'] + " dovrà fare il regalo a " + d['receiver']['firstName'] + " " + d['receiver']['lastName']
    return render_template("add_member.html", rform=Registration(), fform=Finder(), message_reg=None, message_fin=message)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)