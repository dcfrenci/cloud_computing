# Guide gcp
Questa guida consiste in una schematizzazione dei passaggi e delle procedure richieste per il corretto svolgimento della prove di laboratorio per il corso "Applicazioni e sistemi cloud".

## Structure
La guida è composta da quattro macro sezioni con introdotte da una sezione dedicata alla creazione del progetto. Risulta così organizzata:
* [Firestore](firestore)
* [RESTful API](restful-api)
* [Web application](web-application)
* [Pub/Sub](pub/sub)

## Project
Il primo passo è creare un **ambiente virtuale** e **selezionarlo** all'interno dell'ide. All'interno del terminale di Code eseguiamo i seguenti comandi
```bash
python3 -m venv .venv
```
Attiviamo l'ambiente virtuale che abbiamo appena creato (venv)
```bash
source .venv/bin/activate
```

### requirements.txt
Creiamo il file **requirements.txt**
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


## Create the gcloud project
Definiamo il `PROJECT_ID` come variabile globale e in modo che sia univoco a livello globale
```bash
export PROJECT_ID=MY_PROJECT
echo $PROJECT_ID
```
Creiamo il progetto e lo settiamo come default
```bash
gcloud projects create ${PROJECT_ID} --set-as-default
```

## Link the billing account
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
gcloud billing project link ${PROJECT_ID} --billing-account YOUR_BILLING_ACCOUNT
```
Per verificare se il collegamento è stato eseguito con successo, eseguendo il seguente comando dovremmo avere per la voce `billingEnable == True`.
```bash
gcloud billing projects describe ${PROJECT_ID}
```
Attiviamo tutti i services di cui avremo bisogno in seguito
```bash
gcloud services enable appengine.googleapis.com cloudbuild.googleapis.com storage.googleapis.com
```











# Firestore
Il database che utilizzeremo all'interno della nostra applicazione è Firestore. Per prima cosa **creiamo il database** all'interno della google platform, scegliendo se vogliamo un nome specifico
```html
https://console.cloud.google.com/firestore/databases?hl=it&project=PROJECT_ID
```
## Structure
Prima di fare il deployment del database è necessario creare alcuni file necessari per il suo corretto funzionamento.
* db.json --> Usato per inizializzare il database con dei dati
* file_firestore.py --> Usato per gestire la creazione/modifica/eliminazione dei dati

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
        colors_ref=self.db.collection('COLLECTION_NAME')
        colors_ref.document(DOCUMENT_NAME).set({KEY1: PARM1, KEY2: PARM2, KEY3: PARM3})

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

## Deploy
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











# RESTful API
Dalla lettura del file **dettagli_api.yaml** fornito, estraiamo i *metodi* da implementare, i *codici* ad esse associati, le *definizioni* delle resource ed i vari *path*.

## Structure
Per eseguire il deployment di API RESTful dobbiamo definire i seguenti file:
* api.py    --> Usato per gestire metodi HTTP/Codici/Paths
* api.yaml  --> Usato per definire il deployment dell'app su gcloud

### api.py
Utilizziamo questo file per definire i metodi HTTP a cui l'API può rispondere e i vari codici che dovranno essere restituiti. Definiamo per prima cosa gli import:
```python
from flask import Flask, request
from flask_restful import Resource, Api
```
Optional: 
```python
from flask_cors import CORS
```
Creiamo l'app con Flask
```python
app = Flask(__name__)
CORS(app)
api=Api(app)

# Indicato all'interno di dettagli_api.yaml
basePath = '/api/v1'
```
Dalla lettura del file **dettagli_api.yaml** deduciamo i path e le relative risorse. Creiamo quindi una classe per ogni risorsa che abbiamo identificato:
```python
class Risorsa_uno(Resource):
    def get(self, NOME_PARAMETRO):
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
api.add_resource(ColorResource, f'{basePath}/path/<string:NOME_PARAMETRO>')
```
Ecco un esempio in cui il path possiede solamente un metodo e non è presente alcun parametro:
```python
class Risorsa_due(Resource):
    def get(self):
        return obj_list, 200

api.add_resource(ColorList, f'{basePath}/path')
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
service: api

# Definiscono come il server gestisce i metadata delle richieste HTTP
handlers:
- url: /static
  static_dir: static

- url: /.*
  secure: always
  script: auto
```

## Deploy
```bash
gcloud app create --project=${PROJECT_ID}
```

```bash
gcloud app describe --project=${PROJECT_ID}
```







# Web application
L'obiettivo è quello di creare un'interfaccia web per visualizzare i dati all'interno del database.

## Structure
Per poter eseguire il deployment di questa web app dobbiamo crerare i seguenti file:
* templates/    --> Cartella in cui raggruppiamo tutti i template HTML
* static/       --> Cartella in cui raggruppiamo tutti i file statici
* main.py       --> Usato per gestire tutta l'applicazione
* app.yaml      --> Usato per definire il deployment su gcloud

### templates/
Creiamo la cartella **templates** al cui interno inseriremo i file HTML che andranno a costituire i template della pagine dell'applicazione web. Per poter inserire delle strutture dinamiche si fa utilizzo di parametri che vengono passati come argomento quando si renderizzano i template. Seguono alcune strutture utili.

Grazie al parametro `LIST_PARAM` possiamo creare delle strutture dinamiche. In questo caso la struttura risulta cliccabile grazie `<a>...</a>` e ci reindirizza al link `/PATH/{{c}}` dove *c* è un elemento della lista.
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
Crea un WTForm con le label e i valori associati che sono specificati nella sua definizione (vedi dopo).
```html
<html>
    <body>
        <form method="POST">
            Create new color:
            <div>{{form.name.label}}: {{form.name}}</div>
            <div>{{form.red.label}}: {{form.red}}</div>
            <div>{{form.green.label}}: {{form.green}}</div>
            <div>{{form.blue.label}}: {{form.blue}}</div>
            <button>{{form.submit}}</button>
        </form>
    </body>
</html>
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
    name =  StringField('Name', [validators.Length(min=1, max=255)])
    red =   IntegerField('Red', [validators.NumberRange(min=0, max=255)])
    submit= SubmitField('Submit')
```

Creiamo la Web application
```python
app = Flask(__name__)
object_dao = Classe_firestore()
```
Definiamo quindi le funzioni che gestiscono i metodi dell'applicazione (**GET, POST, PUT, DELETE**). Ogni funzione dichiara che tipo di metodi può gestire attraverso `methods=[LISTA_METODI]. La funzione dovrà poi eseguire un return sul render del template HTML inserendo come parametri quelli richiesti da quello specifico template. 

Questo deve essere fatto **per ogni path** da cui possiamo ricevere richieste.
```python
@app.route('/path', methods=['GET']) 
def nome_della_funzione():
    return render_template("TEMPLATE_HTML", PARAMETRI...)

@app.route('/path/<PARAM>', methods=['GET', 'POST'])
def nome_della_funzione(PARAM):
    if request.method == 'POST':
        cform = Classeform(request.form)
        object_dao.add_color(cform.name.data, cform.red.data)
        
        return redirect("/path/" + cform.name.data, code=302)
    
    element = object_dao.get_element_by_name(PARAM)

    if request.method == 'GET':
        cform=Classeform(obj=Struct(**element))
        cform.name.data = PARAM
    return render_template("TEMPLATE_HTML", PARAMETRI...)
```
Il secondo path che dobbiamo gestire risulta essere variabile poiché è presente un parametro dopo una parte che che rimane costante `/path/<PARAM>`. Questo dovrà essere inserito come parametro della nostra funzione (**scritto nello stesso modo**) in modo da poterlo utilizzare.

Per il metodo **GET** sfruttiamo la classe `Struct` che permette di inizializzare il form con i dati del colore `s_color`.
```python
class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)
```

### app.yaml
Come per la sezione RESTful API questo file verrà utilizzato da gcloud per specificare come fare il deployment della nostra web app. La differenza principale risiede nel cambiamento dell'**entry point** (main:app --> seleziono come *app* quella definita nel *main.py*) e nel nome del **service**.
```yaml
runtime: python313

instance_class: F1
automatic_scaling:
  max_instances: 1

entrypoint: gunicorn main:app
service: default

handlers:
- url: /static
  static_dir: static
- url: /.*
  secure: always
  script: auto
```

## Deploy
Ripetiamo lo stesso deployment che abbiamo utilizzato per l'API:
```bash
gcloud app create --project=${PROJECT_ID}
```

```bash
gcloud app describe --project=${PROJECT_ID}
```










# PubSub 
## Structure
## Deploy