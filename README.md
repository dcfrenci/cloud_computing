# Guide gcp
Questa guida consiste in una schematizzazione dei passaggi e delle procedure richieste per il corretto svolgimento della prove di laboratorio per il corso "Applicazioni e sistemi cloud".

## Index
La guida è composta da quattro macro sezioni con introdotte da una sezione dedicata alla creazione del progetto. Risulta così organizzata:
* [Project](#1---project)
    * [Structure](#11---structure)
        * [requirements.txt](#requirementstxt)
        * [.gcloudignore](#gcloudignore)
        * [.gitignore](#gitignore)
    * [Create the gcloud project](#12---create-the-gcloud-project)
    * [Link the billing account](#13---link-the-billing-account)
    * [Create the app on gcloud](#14---create-the-app-on-gcloud)
* [Firestore](#2---firestore)
    * [Structure](#21---structure)
        * [db.json](#dbjson)
        * [file_firestore.py](#file_firestorepy)
    * [Deploy](#22---deploy)
* [RESTful API](#3---restful-api)
    * [Structure](#31---structure)
        * [api.py](#apipy)
        * [api.yaml](#apiyaml)
    * [Deploy](#32---deploy)
* [Web application](#4---web-application)
    * [Structure](#41---structure)
        * [templates/](#templates)
        * [main.py](#mainpy)
        * [app.yaml](#appyaml)
    * [Deploy](#42---deploy)
* [Pub/Sub](#5---pub/sub)
    * [Structure](#51---structure)
    * [Deploy](#52---deploy)
* [Function](#6---function)
    * [Structure](#61---structure)
    * [Deploy](#62---deploy)

# 1 - Project
Il primo passo è creare un **ambiente virtuale** e **selezionarlo** all'interno dell'ide. All'interno del terminale di Code eseguiamo i seguenti comandi
```bash
python3 -m venv .venv
```
Attiviamo l'ambiente virtuale che abbiamo appena creato (venv)
```bash
source .venv/bin/activate
```

## 1.1 - Structure
Si creino i seguenti file:
* requirements.txt  --> Per definire le librerie necessarie
* .gcloudignore     --> Per specificare i file da **non** caricare su gcloud
* .gitingnore       --> Per specificare i file da **non** caricare su github
Per creare velocemente i file:
```bash
code requirements.txt .gcloudignore .gitignore
```

### requirements.txt
Creiamo il file **requirements.txt**.
```
Flask==3.1.2
Flask-RESTful==0.3.10
google-cloud-firestore==2.22.0
WTForms==3.2.1
gunicorn==23.0.0

flask-cors==6.0.2
```
Installiamo i requirements specificati all'interno di requirements.txt
```bash
pip install -r requirements.txt
```

### .gcloudignore
Creiamo il file **.gcloudignore** che verrà utilizzato in seguito per escludere tutti i file che non devono essere caricati su gcloud.
```
.git
.gitignore

# Python pycache:
__pycache__/

# virtual env
.venv/
# Ignored by the build system
/setup.cfg
credentials.json
```

### .gitignore
Creiamo il file **.gitignore**.
```
credentials.json
.venv/
__pycache__/
```

## 1.2 - Create the gcloud project
Definiamo il `PROJECT_ID` come variabile globale e in modo che sia univoco a livello globale
```bash
export PROJECT_ID=MY_PROJECT
echo $PROJECT_ID
```
Creiamo il progetto e lo settiamo come default
```bash
gcloud projects create ${PROJECT_ID} --set-as-default
```

## 1.3 - Link the billing account
Definiamo il `NAME` come variabile globale
```bash
export NAME=USER_NAME
echo $NAME
```
```bash
gcloud iam service-accounts create ${NAME}
```
Per visualizzare il billing account utilizziamo il seguente comando selezionando il valore sotto **ACCOUNT_ID** come proprio billing account:
```bash
gcloud billing accounts list
```
```bash
gcloud billing projects link ${PROJECT_ID} --billing-account YOUR_BILLING_ACCOUNT
```
Per verificare se il collegamento è stato eseguito con successo, eseguendo il seguente comando dovremmo avere per la voce `billingEnable == True`.
```bash
gcloud billing projects describe ${PROJECT_ID}
```
Attiviamo tutti i services di cui avremo bisogno in seguito
```bash
gcloud services enable appengine.googleapis.com cloudbuild.googleapis.com storage.googleapis.com firestore.googleapis.com
```

## 1.4 - Create the app on gcloud
Creiamo l'applicazione su gcloud
```bash
gcloud app create --project=${PROJECT_ID}
gcloud app describe --project=${PROJECT_ID}
```
###
###
###
###
###
###
###
###
###
###
###
# 2 - Firestore
Il database che utilizzeremo all'interno della nostra applicazione è Firestore. Per prima cosa **creiamo il database** all'interno della google platform, scegliendo se vogliamo un nome specifico
```html
https://console.cloud.google.com/firestore/databases?hl=it&project=PROJECT_ID
```
## 2.1 - Structure
Prima di fare il deployment del database è necessario creare alcuni file necessari per il suo corretto funzionamento.
* db.json --> Usato per inizializzare il database con dei dati
* file_firestore.py --> Usato per gestire la creazione/modifica/eliminazione dei dati
Per creare velocemente i file:
```bash
code db.json file_firestore.py
```

### db.json
La struttura è caratteristica di ogni esercizio, tuttavia corrisponde con una lista di dizionari `[{...}, {...}, {...}]`. Segue un esempio:
```json
[
	 {"name": "red", "red": 255, "green": 0, "blue": 0},
	 {"name": "green", "red": 0, "green": 255, "blue": 0},
	 {"name": "blue", "red": 0, "green": 0, "blue": 255},
]
```

### file_firestore.py
Questo file viene utilizzato per definire i metodi che si utilizzeranno per scambiare informazioni con il database. Come prima cosa si inseriscono i seguenti import: 
```python
from google.cloud import firestore
import json
```
Definiamo la classe che andrà a interporsi tra le richieste e il database. All'interno definiamo poi il database specificando il `NOME_SCELTO` se diverso dal default altrimenti è possibile lasciare vuoto.
```python
class Classe_firestore(object):
    def __init__(self):
        self.db = firestore.Client(database="NOME_SCELTO")
        self.populate_db('db.json')
    
    # Aggiunta di nuovi dati
    def add_element(self, DOCUMENT_NAME, PARM1, PARM2, PARM3):
        c = self.db.collection('COLLECTION_NAME')
        c.document(DOCUMENT_NAME).set({KEY1: PARM1, KEY2: PARM2, KEY3: PARM3})

    # Richiesta per un singolo dato
    def get_element_by_name(self, DOCUMENT_NAME):
        c = self.db.collection('COLLECTION_NAME').document(DOCUMENT_NAME).get()
        rv = c.to_dict() if c.exists else None
        return rv
    
    # Richiesta per tutti i dati
    def get_elements(self):
        #rv=[]
        #for c in self.db.collection('COLLECTION_NAME').stream():
        #    rv.append(str(c.id))
        #return rv
        return [str(c.id) for c in self.db.collection('COLLECTION_NAME').stream()]
    
    def delete_element_by_name(self, DOCUMENT_NAME):
        self.db.collection('COLLECTION_NAME').document(DOCUMENT_NAME).delete()

    # Per popolare il db ogni volta che creiamo un oggetto 
    def populate_db(self, filename):
        with open(filename) as f:
            data_list = json.load(f)
            for data in data_list:
                self.add_element(data)
```

## 2.2 - Deploy
Abilitiamo il servizio su gcloud 
```bash
gcloud services enable firestore.googleapis.com
```
Verifichiamo che il `PROJECT_ID` e il `NAME` siano corretti
```bash
echo PROJECT_ID = ${PROJECT_ID}
echo NAME = ${NAME}
```
Creiamo un service account che viene utilizzato per effettuare le chiamate alle API di Google.
```bash
gcloud projects add-iam-policy-binding ${PROJECT_ID} --member "serviceAccount:${NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role "roles/owner"
```
Creiamo una chiave crittografata (.json) per impersonare il service account.
```bash
touch credentials.json 
gcloud iam service-accounts keys create credentials.json --iam-account ${NAME}@${PROJECT_ID}.iam.gserviceaccount.com 
```
All'interno del terminale che utilizzeremo per eseguire i test e lanciare la nostra applicazione in locale andiamo a eseguire il seguente comando che crea una variabile d'ambiente con la **posizione di creddentials.json**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/credentials.json"
```
###
###
###
###
###
###
###
###
###
###
###
# 3 - RESTful API
Dalla lettura del file **dettagli_api.yaml** fornito, estraiamo i *metodi* da implementare, i *codici* ad esse associati, le *definizioni* delle resource ed i vari *path*.

## 3.1 - Structure
Per eseguire il deployment di API RESTful dobbiamo definire i seguenti file:
* api.py    --> Usato per gestire metodi HTTP/Codici/Paths
* api.yaml  --> Usato per definire il deployment dell'app su gcloud
Per creare velocemente i file:
```bash
code api.py api.yaml
```

### api.py
Utilizziamo questo file per definire i metodi HTTP a cui l'API può rispondere e i vari codici che dovranno essere restituiti. Definiamo per prima cosa gli import:
```python
from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS
from file_firestore import *
```
Creiamo l'app con Flask
```python
app = Flask(__name__)
CORS(app)
api=Api(app)
db_dao = Classe_firestore()

# Indicato all'interno di dettagli_api.yaml
basePath = '/api/v1'
```
Dalla lettura del file **dettagli_api.yaml** deduciamo i path e le relative risorse. Creiamo quindi *una classe per ogni path* che abbiamo identificato inserendo i *metodi* e ritornando `None, Codice` quando non è specificato lo `schema` altrimenti ritornando un dizionario con la struttura specificata all'interno della definizione.
```python
def validate(d):
    # Check presence of parameters
    for key in ['key_list']:
        if key not in d.keys():
            return False
    
    # Check values

    return True


class Resource_UNO(Resource):
    def get(self, NOME_PARAMETRO):
        # Per ottenere i dati all'interno della request -> Otteniamo un dizionario
        REQUEST_DATA=request.json
        return obj, codice(200, 400)
    
    def post(self, NOME_PARAMETRO):
        return None, codice(200, 400)

    def put(self, NOME_PARAMETRO):
        return None, codice(200, 400)

    def delete(self, NOME_PARAMETRO):
        return None, codice(200, 400)
```
Per ciascuna classe eseguiamo il collegamento con il path corretto all'esterno della classe indicando il nome del parametro (se presente nel path).
```python
api.add_resource(Resource_UNO, f'{basePath}/path/<string:NOME_PARAMETRO>')
```
Ecco un esempio in cui il path possiede solamente un metodo e non è presente alcun parametro:
```python
class Resource_DUE(Resource):
    def get(self):
        return obj, 200

api.add_resource(Resource_DUE, f'{basePath}/path')
```

### api.yaml
Questo file si occupa della creazione dell'app flusk su gcloud. 
```yaml
# Versione di python
runtime: python313

# Limitare lo scaling
instance_class: F1
automatic_scaling:
  max_instances: 1

# Specifica quale app utilizzare per creare il servizio (es. api:app -> seleziona app da api.py)
entrypoint: gunicorn api:app
# Specifica il nome del servizio
service: default

# Definiscono come il server gestisce i metadata delle richieste HTTP
handlers:
- url: /static
  static_dir: static

- url: /.*
  secure: always
  script: auto
```

## 3.2 - Deploy
```bash
gcloud app deploy api.yaml
```

## 3.3 - Testing
Per fare il testing inseriamo all'interno di **api.py** il codice seguente e possiamo fare il test usando swagger ([link](editor.swagger.io)).
```python
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
```
In un altro terminale si esegua il file (dopo aver eseguito `source .venv/bin/activate`) **tester_yaml.py** che eseguirà in modo automatico tutti i test definiti all'interno di **tests.yaml**.
###
###
###
###
###
###
###
###
###
###
###
# 4 - Web application
L'obiettivo è quello di creare un'interfaccia web per visualizzare i dati all'interno del database.

## 4.1 - Structure
Per poter eseguire il deployment di questa web app dobbiamo crerare i seguenti file:
* templates/    --> Cartella in cui raggruppiamo tutti i template HTML
* static/       --> Cartella in cui raggruppiamo tutti i file statici
* main.py       --> Usato per gestire tutta l'applicazione
* app.yaml      --> Usato per definire il deployment su gcloud
Per creare velocemente i file:
```bash
mkdir templates
code main.py app.yaml
```

### templates/
Creiamo la cartella **templates** al cui interno inseriremo i file HTML che andranno a costituire i template della pagine dell'applicazione web. Per poter inserire delle strutture dinamiche si fa utilizzo di parametri che vengono passati come argomento quando si renderizzano i template. Seguono alcune strutture utili.

Grazie al parametro `LIST_PARAM` possiamo creare delle strutture dinamiche. In questo caso la struttura risulta cliccabile grazie `<a>...</a>` e ci reindirizza al link `/PATH/{{c}}` dove *c* è un elemento della lista. Se vogliamo utilizzare delle funzioni come `zip()` queste devono essere passate come argomento al template.
```html
<html>
    <body>
        <ul>
			{% for c in LIST_PARAM %}
				<li><a href="/PATH/{{c}}">{{c}}</a></li>
			{% endfor %}
		</ul>
    </body>
</html>
```
Questa struttura crea una box utilizzando i parametri `r`, `g`, `b` per determinarne il colore. Il termine `&nbsp` viene utilizzato per creare una riga e non viene renderizzato come testo.
```html
<html>
    <body>
        <div class="color-box" style="background-color: rgb({{r}}, {{g}}, {{b}})">&nbsp</div>
    </body>
</html>
```
Questa struttura crea un WTForm con le label e i valori associati che sono specificati nella sua definizione (vedi dopo).
```html
<html>
    <body>
        <form method="POST">
            Create new color:
            <div>{{form.name.label}}: {{form.name}}</div>
            <div>{{form.red.label}}: {{form.red}}</div>
            <button>{{form.submit}}</button>
        </form>
    </body>
</html>
```
Se abbiamo più di un form all'interno della stessa pagina si deve utilizzare il parametro `name="PARAM` e `action="/path"`, seguendo questa struttura:
```html
<html>
    <body>
        <form method="POST" name="rform" action="/secretsanta/classeform">
            Inserisci nome, cognome, email per unirti al secret santa:
            <div>{{rform.firstName.label}}: {{rform.firstName}}</div>
            <div>{{rform.lastName.label}}: {{rform.lastName}}</div>
            <div>{{rform.email.label}}: {{rform.email}}</div>
            <button>{{rform.submit}}</button>
        </form>

        <form method="POST" name="fform" action="/secretsanta/registration">
            Per sapere a chi dovrai fare il regalo inserisci la tua email:
            <div>{{fform.email.label}}: {{fform.email}}</div>
            <button>{{fform.submit}}</button>
        </form>
    </body>
</html>
```
Questa struttura crea una tabella dove di definiscono prima le colonne all'interno `<thead>` e poi le righe in `<tbody>`. Si utilizza:
* `<tr>` --> Definisce una riga
* `<th>` --> Definisce una cella con testo in **grassetto** e centrato automaticamente
* `<td>` --> Definisce una cella con testo semplice
```html
<html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.1.3/dist/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
    </head>
    <body>
        <table class="table text-center">
            <thead>
                <tr>
                    <th scope="col">Colonna 1</th>
                    <th scope="col">Colonna 2</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <th scope="row">Cella 1 per riga 1</th>
                    <td style="text-align: center">Cella 2 per riga 2</td>
                    <td style="text-align: center"><a href="/PATH/{{c}}">{{c}}</a></td>
                </tr>
            </tbody>
        </table>
    </body>
</html>
```
Per aggiungere componenti in base a delle condizioni si può utilizzare **if di jinja**.
```html

<html>
    <body>
        {% if giorno == today %} 
            <tr class="table-primary">Verificata</tr> 
        {% else %} 
            <tr>Non verificata</tr>
        {% endif %}
    </body>
</html>
```

Questo componente permette di migliorare la UI e talvolta risulta essere necessario aggiungerlo per visualizzare delle classi css.
```html
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.1.3/dist/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
</head>
```
Per altre strutture consultare la documentazione di **bootstrap** [link](https://www.google.com/search?q=bootstrap).

### main.py
Importiamo all'interno del file le seguenti dipendenze. Se non è necessario effettuare delle redirezioni possiamo rimuovere `redirect`.
```python
from flask import Flask, render_template, request, redirect
```
Importiamo dal file, dove gestiamo il database, le funzioni che ci permettono di lavorare con i dati. In questo caso `file_firestore.py`.
```python
from file_firestore import *
```

**Se dobbiamo utilizzare dei WTForm** aggiungiamo, selezionando le tipologie di field di cui abbiamo bisogno tramite i seguenti imports:
```python
from wtforms import Form, StringField, IntegerField, SubmitField, validators
```
Per utilizzare i WTForm dichiariamo una classe che eredita da Form in cui spefichiamo i nomi e la tipologia di field e validators per i dati che saranno inseriti al loro interno.
```python
class Classeform(Form):
    name =  StringField('Name', [validators.DataRequired()])
    red =   IntegerField('Red', [validators.NumberRange(min=0, max=255)])
    submit= SubmitField('Submit')

class Registration(Form):
    email = EmailField('Email address', [validators.DataRequired(), validators.Email()])
    submit= SubmitField('Conferma inserimento')
```

Creiamo la Web application
```python
app = Flask(__name__)
db_dao = Classe_firestore()
```
Definiamo quindi le funzioni che gestiscono i metodi dell'applicazione (**GET, POST, PUT, DELETE**). Ogni funzione dichiara che tipo di metodi può gestire attraverso `methods=[LISTA_METODI]. La funzione dovrà poi eseguire un return sul render del template HTML inserendo come parametri quelli richiesti da quello specifico template. 

Questo deve essere fatto **per ogni path** da cui possiamo ricevere richieste.
```python
@app.route('/path', methods=['GET']) 
def function_base():
    return render_template("TEMPLATE_HTML", PARAMETRI...)

@app.route('/path/<PARAM>', methods=['GET', 'POST'])
def function_specific(PARAM):
    if request.method == 'POST':
        cform = Classeform(request.form)
        db_dao.add_element(cform.name.data, cform.red.data)
        
        return redirect("/path/" + cform.name.data, code=302)
    
    element = db_dao.get_element_by_name(PARAM)

    if request.method == 'GET':
        cform=Classeform(obj=Struct(**element))
        cform.name.data = PARAM
    return render_template("TEMPLATE_HTML", PARAMETRI...)
```
Il secondo path che dobbiamo gestire risulta essere variabile poiché è presente un parametro dopo una parte che che rimane costante `/path/<PARAM>`. Questo dovrà essere inserito come parametro della nostra funzione (**scritto nello stesso modo**) in modo da poterlo utilizzare.

Per il metodo **GET** sfruttiamo la classe `Struct` che permette di inizializzare il form con i dati del colore `s_color`. Verranno inizializzati solamente i campi con le chiavi combacianti.
```python
class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)
```
Se si devono inserire due WTForm all'interno della stessa pagina si devono creae due metodi che rispondono a due path differenti.
```python
@app.route('/secretsanta/classeform', methods=['POST'])
def function_specific():
    rform = Classeform(request.form)
    return render_template("add_member.html", rform=Classeform(), fform=Registration())
    

@app.route('/secretsanta/Registration', methods=['POST'])
def function_finder():
    fform=Registration(request.form)
    return render_template("add_member.html", rform=Classeform(), fform=Registration())
```

### app.yaml
Come per la sezione RESTful API questo file verrà utilizzato da gcloud per specificare come fare il deployment della nostra web app. La differenza principale risiede nel cambiamento dell'**entry point** (main:app --> seleziono come *app* quella definita nel *main.py*) e nel nome del **service**.
```yaml
runtime: python313

instance_class: F1
automatic_scaling:
  max_instances: 1

entrypoint: gunicorn main:app
service: web

handlers:
- url: /static
  static_dir: static
- url: /.*
  secure: always
  script: auto
```

## 4.2 - Deploy
Ripetiamo lo stesso deployment che abbiamo utilizzato per l'API:
```bash
gcloud app deploy app.yaml
```

## 4.3 - Testing
Per eseguire il test della web application inseriamo in **main.py**:
```python
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
```
###
###
###
###
###
###
###
###
###
###
###
# 5 - PubSub

## 5.1 - Structure
* publisher.py --> Usato per definire il publisher che andrà a creare i messaggi sul topic
* subscriber.py --> Usato per una configurazione **pull**
* pubsub.py --> Usato per una configurazione **push**
    * requirements.txt  --> Per definire le librerie necessarie
    * .gcloudignore     --> Per specificare i file da **non** caricare su gcloud
    * app.yaml          --> Per specificare come fare il deployment su gcloud

Si distinguono due possibili configurazioni:
* **Pull**: è colui che è iscritto al topic a chiedere se sono presenti dei nuovi messaggi. 
* **Push**: è il "topic" che invierà una notifica a coloro che sono iscritti al topic quando è presente un nuovo messaggio.

Per creare i file della tipologia **pull**:
```bash
mkdir pub_sub
cd pub_sub
code publisher.py subscriber.py 
```

```bash
mkdir pub_sub
cd pub_sub
code publisher.py pubsub.py requirements.txt .gcloudignore app.yaml 
```

### publisher.py
Da creare sia in caso di pull che di push.
```python
import os
from google.cloud import firestore
from google.cloud import pubsub_v1

update_interval = 10

topic_name = os.environ['TOPIC'] if 'TOPIC' in os.environ.keys()  else 'TOPIC'
project_id = os.environ['PROJECT_ID'] if 'PROJECT_ID' in os.environ.keys()  else 'PROJECT_ID'

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_name)

def notify(PARAM):

    data={'key': 'value', 'key2': 'value2'}
    res = publisher.publish(topic_path, json.dumps(data).encode('utf-8'))

    print(data, res)

if __name__=='__main__':
    while True:
        notify(PARAM)
        time.sleep(update_interval)
```

### subscriber.py
```python
import os
from google.cloud import pubsub_v1
from google.cloud import firestore

subscription_name=os.environ['SUBSCRIPTION_NAME'] if 'SUBSCRIPTION_NAME' in os.environ.keys() else 'SUBSCRIPTION_NAME'
project_id = os.environ['PROJECT_ID'] if 'PROJECT_ID' in os.environ.keys()  else 'PROJECT_ID'

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_name)

db = firestore.Client("NOME_DATABASE")

def save_temperature(data):
    dt = datetime.datetime.fromtimestamp(data['timestamp'])
    docname = dt.strftime('%Y%m%d')
    print(docname, data['temperature'])
    db.collection('temperature').document(docname).set({str(data['timestamp']): data['temperature']}, merge=True)


def callback(message):
    message.ack()
    try:
        save_temperature(json.loads(message.data.decode('utf-8')))
    except:
        pass

if __name__=='__main__':    
    pull = subscriber.subscribe(subscription_path, callback=callback)
    try:
        pull.result()
    except:
        pull.cancel()
```

### pubsub.py 
Definiamo un Web Hook 
```python
import os
from google.cloud import firestore
from google.cloud import pubsub_v1

app = Flask(__name__)
app.config['PUBSUB_VERIFICATION_TOKEN'] = os.environ['PUBSUB_VERIFICATION_TOKEN']

db = firestore.Client(database="NOME_DATABASE")


@app.route('/pubsub/push', methods=['POST'])
def pubsub_push():
    print('Received pubsub push')
    if request.args.get('token', '') != app.config['PUBSUB_VERIFICATION_TOKEN']:
        return 'Invalid request', 400

    envelope = json.loads(request.data.decode('utf-8'))
    
    return 'OK', 200
```
### requirements.txt
```
Flask==3.1.2
google-cloud-firestore==2.22.0
google-cloud-pubsub==2.34.0
gunicorn==23.0.0
```

### .gcloudignore
```
.git
.gitignore

# Python pycache:
__pycache__/

# virtual env
.venv/
# Ignored by the build system
/setup.cfg
credentials.json
```

### app.yaml
```yaml
runtime: python313
handlers:
- url: /.*
  script: auto
env_variables:
  PUBSUB_VERIFICATION_TOKEN: 'TOKEN'
  PROJECT_ID: 'PROJECT_ID'
  TOPIC: 'TOPIC'
```

## 5.2 - Deploy
Definiamo il nome del topic da creare:
```bash
export TOPIC=TOPIC_NAME
echo TOPIC = ${TOPIC}
```
Verifichiamo che tutte le variabili globali siano corrette.
```bash
export TOKEN=123token
echo TOKEN = ${TOKEN}
export SUBSCRIPTION_NAME=SUBSCRIPTION_NAME
echo SUBSCRIPTION_NAME = ${SUBSCRIPTION_NAME}
```
Creiamo il topic con il nome definito nella variabile globale `TOPIC`.
```bash
gcloud pubsub topics create ${TOPIC}
```
Se dobbiamo fare il deployment di una **configurazione pull**:
```bash
gcloud pubsub subscriptions create ${SUBSCRIPTION_NAME} --topic ${TOPIC} --push-endpoint "https://${PROJECT_ID}.appspot.com/pubsub/push?token=${TOKEN}" --ack-deadline 10
```
Se invece dobbiamo fare il deployment di una **configurazione push**:
```bash
gcloud app deploy app.yaml
```

## 5.3 - Testing

###
###
###
###
###
###
###
###
###
###
###
# 6 - Function
Le function sono delle **Action** che vengono eseguite in risposta al verificarsi di un determinato **Event**. Affinché un evento determini esecuzione di una funzione, questo deve essere stato colletato tramite un **Trigger**. Il nostro obiettivo sarà quello di creare la funzione (action) e collegarla tramite un trigger all'osservazione di uno specifico evento. 

## 6.1 - Structure
Si devono quindi creare questi file:
* func_stat/            --> Cartella che conterrà tutti i file legati alla function
    * requirements.txt  --> Definisce le librerie necessarie
    * .gcloudignore     --> Definisce i file da non caricare su gcloud
    * main.py           --> Usato per gestire tutte le funzionalità
Per creare velocemente i file:
```bash
mkdir func_stat
cd func_stat
code requirements.txt .gcloudignore main.py
```

### requirements.txt
Creiamo il file **requirements.txt**:
```
google-cloud-firestore==2.22.0

# Se contiene una HTTP function 
flask==2.3.3
```

### .gcloudignore
Creiamo il file **.gcloudignore**:
```
.git
.gitignore

__pycache__/
.venv/

/setup.cfg
credentials.json
```

### main.py
Aggiungiamo gli import al file **main.py**. 
```python
from google.cloud import firestore
```
Per la definizione della Function dobbiamo comprendere la sua tipologia:
* **HTTP Function**: questo tipo di function accetta solamente un oggetto request e restituisce un string/HTML. Tutte le informazioni sulla richiesta sono contenute all'interno dell'oggetto request (Request è un oggetto di Flask --> Dovremo includerlo). 
* **Event-driven Function (Gen 1)**: questo tipo di function accetta due parametri data e context e sono utilizzate solitamente da eventi come Pub/Sub o Firestore.
* Cloud Functions (Gen 2) --> **Non fatte**: questo di function unisce i parametri data e context delle Event-driven function basando il processo su un Function network e sulle Cloud run. 

Nel caso di **HTTP Function** dovremo gestire il traffico delle richieste che HTTP che arrivano alla function. Se dobbiamo rispondere solamente ad una request di tipo specifico usiamo `request.method==GET` o se solamente ad un path speficifico usiamo `.path`. 
```python
from flask import Flask, request

db = firestore.Client(database="NOME_DATABASE")

def HTTP_FUNCTION(request):
    if request.method == 'GET':

    path = request.path
    pages = path.split('/')

    return 'STRING'
```
Nel caso di **Event-driven Function** sappiamo che data è un dizionario a cui possiamo accedere usando le chiavi `oldValue`, `updateMask` e `value`, con la seguente struttura:
```python
{
	"oldValue": { // Update and Delete operations only
		Document object with pre-operation document snapshot
	},
	"updateMask": { // Update operations only
		DocumentMask object that lists changed fields.
	},
	"value": {
		Document object with post-operation document snapshot
	}
}
```
```python
db = firestore.Client(database="NOME_DATABASE")

def EVENT_FUNCTION(data, context):

    if not context.event_type.endwith(".create"):
        # Create event
        return 
    if not context.event_type.endwith(".update"):
        # Update event
        return 
    if not context.event_type.endwith(".delete"):
        # Delete event
        return 

    document = data['value']
    value = context.params['KEY']
    document_name = context.resource.split('/')[-1]

    new_value = data['value'] if len(data["value"]) != 0 else None
    old_value = data['oldValue'] if len(data["oldValue"]) !=0 else None
    if new_value and not old_value: # document added
        pass
    elif not new_value and old_value: # document removed
        pass
    else: # document updated
        pass

```
Il metodo `.params["KEY"]` viene usato per accedere al dizionario creato dall'uso delle wildcard (.../temp/{day} --> Usiamo 'day' come KEY), mentre grazie `.resource.split('/')[-1]` possiamo ottenere dal path completo il nome del documento.

## 6.2 - Deploy
**Tutti** i seguenti comandi saranno da eseguire mentre ci troviamo all'interno della cartella **func_stat/**. Verifichiamo se le varibili d'ambiente `PROJECT_ID` e `NAME` sono ancora valide:
```bash
echo PROJECT_ID = ${PROJECT_ID}
echo NAME = ${NAME}
```
**Se non sono più valide** le settiamo attraverso i seguenti comandi: 
```bash
export PROJECT_ID=MY_PROJECT
echo $PROJECT_ID
```
```bash
export NAME=USER_NAME
echo $NAME
```
Creiamo le credenziali e le salviamo in credentials.json
```bash
gcloud projects add-iam-policy-binding ${PROJECT_ID} --member "serviceAccount:${NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role "roles/owner"
touch credentials.json 
gcloud iam service-accounts keys create credentials.json --iam-account ${NAME}@${PROJECT_ID}.iam.gserviceaccount.com 
```
Esportiamo le credenziali:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/credentials.json"
```
Attiviamo il service per le function su gcloud
```bash
gcloud services enable cloudfunctions.googleapis.com
```
Il procedimento del deployment da qui in avanti è specifico rispetto al tipo di Function che andiamo a svolgere. Distinguiamo quindi il deplyment per le HTTP Function e quelle Event-driven.

### HTTP Function
Definiamo il nome della funzione che dovrà essere invocata dalla richiesta HTTP:
```bash
export FUNCTION=NOME_FUNZIONE
echo FUNCTION = ${FUNCTION}
```
Definiamo il runtime che dovrà essere utilizzato:
```bash
export RUNTIME=python310
echo RUNTIME = ${RUNTIME}
```
Possiamo quindi eseguire il deploy della HTTP function dove con `--no-gen2` specifichiamo che è una function *gen 1*.
```bash
export FUNCTION=get_status
gcloud functions deploy ${FUNCTION} --runtime ${RUNTIME} --trigger-http –allow-unauthenticated --docker-registry=artifact-registry --no-gen2
```
Per eseguire il testing possiamo utilizzare l'indirizzo HTTP della funzione a cui aggiungiamo il path che vogliamo verificare. Usando il seguente comando possiamo ottenere una descrizione della function che contiene anche il suo indirizzo HTTP.
```bash
gcloud functions describe ${FUNCTION}
```

### Event driven Function
Per prima cosa dobbiamo definire le seguenti variabili globali:
```bash
export FUNCTION=NOME_FUNZIONE
echo FUNCTION = ${FUNCTION}
```
```bash
export RUNTIME=python310
echo RUNTIME = ${RUNTIME}
```
```bash
export DATABASE=NOME_DATABASE
echo DATABASE = ${DATABASE}
```
```bash
export COLLECTION=COLLECTION_NAME
echo COLLECTION = ${COLLECTION}
```
Verifichiamo di aver impostato correttamente tutte le variabili globali:
```bash
echo FUNCTION   = ${FUNCTION}
echo RUNTIME    = ${RUNTIME}
echo DATABASE   = ${DATABASE}
echo COLLECTION = ${COLLECTION}
```
Decidiamo che tipo di eventi vogliamo osservare `--trigger-event="..."`:
* `--trigger-event="providers/cloud.firestore/eventTypes/document.create`: quando viene creato un nuovo documento.
* `--trigger-event="providers/cloud.firestore/eventTypes/document.update`: quando un documento che esiste già viene modificato.
* `--trigger-event="providers/cloud.firestore/eventTypes/document.delete`: quando viene rimosso un documento.
* `--trigger-event="providers/cloud.firestore/eventTypes/document.write`: quando un documento viene creato e aggiornato.

Definiamo il path delle risorse da osservare per generare gli eventi. La struttura del path è così composta: `projects/[PROJECT_ID]/databases/[DATABASE_ID]/documents/[PATH_AL_DOCUMENTO]`. Definendo `PATH_AL_DOCUMENTO` come `.../COLLECTION/NOME_DOC` andiamo però ad osservare solo quel documento specifico. Per osservare i cambiamenti all'interno di una collection dobbiamo usare le **wildcard**. Definiamo quindi `PATH_AL_DOCUMENTO` come `.../COLLECTION/{NAME}` dove `NAME` è soltanto un segnaposto e corrisponderà alla **key** del dizionario che verrà usata per ottenere il nome del documento su cui è stato osservato l'evento. 

Usando le wildcard in questo modo possiamo osservare i cambiamenti *solo* per i documenti al "livello" specificato, mentre se vogliamo osservare anche i cambiamenti più in profondità (*utile per le subcollection*) inseriamo nella wildcard `.../{NAME==**}`. Bisogna tenere a mente che l'osservabilità viene comunque sempre fatta sui documenti, ovvero sono sempre loro che determinano lo scatenarsi di un evento.

Con questo comando andiamo eseguire il deploy della funzione `$(FUNCTION)`, usando `$(RUNTIME)`, osservando i cambiamenti sul path specificato.
```bash
gcloud functions deploy ${FUNCTION} --runtime ${RUNTIME} --trigger-event "providers/cloud.firestore/eventTypes/document.write" --trigger-resource "projects/${PROJECT_ID}/databases/${DATABASE}/documents/${COLLECTION}/{KEY}" --docker-registry=artifact-registry --no-gen2
```
Per verificare se la Function è correttamente funzionante si utilizzi la funzione *Esplora log* sulla suite gcloud.

