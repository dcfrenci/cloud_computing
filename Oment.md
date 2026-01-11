# Guide omnet
Questa guida consiste in una schematizzazione dei passaggi e delle procedure richieste per il corretto svolgimento della prove di laboratorio per il corso "Applicazioni e sistemi cloud".

## Index
* [Network definition](#1---network-definition)
* [Parse results](#2---parse-results)
* [Analyze results](#3---analyze-results)

## Setting the enviroment
Per prima cosa ci si posizioni all'interno della cartella dove omnet è installato `.../omnet--version/`. Si attivi l'enviroment e ci si posizioni nella cartella dove si svolgerà l'esercizio.
```bash
. setenv
cd samples/queuenet/
```
Definiamo poi il `FILE_NAME` che sarà utilizzato per creare automaticamente i file **FILE_NAME.ned**, **FILE_NAME.ini.mako** e **FILE_NAME.ini**.
```bash
export FILE_NAME=YOUR_FILE_NAME
echo FILE_NAME = ${FILE_NAME}
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
# 1 - Network definition
In questa sezione saranno definiti i file per condurre le simulazioni, partendo dalla definizione della network che si utilizzerà.

## 1.1 - Structure
* FILE.ned          --> Usato per definire la struttura della network (i componenti e come sono connessi) e i parametri dell'esercizio
* FILE.ini.mako     --> Usato per definire le configurazioni oggetto di simulazione

Creiamo i file `.ned` e `.ini.mako`:
```bash
code ${FILE_NAME}.ned
code ${FILE_NAME}.ini.mako
```

### FILE.ned
I componenti che possono essere utilizzati sono:
* [Source](#source): corrisponde alla sorgente del traffico che poi verrà distribuito ai vari server.
* [Router](#router): ha il compito di distribuire il traffico tra i vari server seguendo una particolare politica.
* [Queue](#queue): viene posta prima del server e viene utilizzata per valutare il tempo in cui le task restano in attesa prima di essere processati.
* [Delay](#delay): è un tempo fisso che viene applicato ad ogni task per simulare delle operazioni. 
* [Sink](#sink): corrisponde all'output della network e viene utilizzato per calcolare alcune statistiche di performance.

Per una descrizione più accurata di tutti i dettagli per i componenti si utilizzi [link](#components)

Si crei quindi il FILE.ned e si inseriscano i seguenti import rimuovendo i componenti che non saranno utilizzati.
```ned
import org.omnetpp.queueing.Source;
import org.omnetpp.queueing.Router;
import org.omnetpp.queueing.Queue;
import org.omnetpp.queueing.Delay;
import org.omnetpp.queueing.Sink;
```
Si aggiunga poi la network definendone il nome e specificando **parameters**, **submodules** e **connections**:
* **Parameters** si inseriscono tutti i parametri dell'esercizio tenendo conto di quei valori sono temporali e quindi vanno definiti moltiplicandone il valore per `1s`, definendo in questo modo l'unità di misura.
* **Submodules** si definiscino tutti componenti utilizzati, associando il nome (scelto da noi) alla tipologia corrispondente. 
* **Connections** si definiscono le connessioni tra i componenti. Per sapere quando inserire `++` si verifichi la [descrizione specifica](#components) del componente.
```ned
network NETWORK {

    parameters:
        int N = default(10)
        int K = default(10);
        double rho = default(0.8);
        double mu = default(10);
        double lambda = mu * rho;
        
        srv.capacity = K;
        # Usiamo 1s per definire l'unità di misura 
        srv.serviceTime = 1s * exponential(1 / mu);
        src.interArrivalTime = 1s * exponential(1 / lambda);

    submodules:
        src     : Source;
        router  : Router;
        srv[N]  : Queue;
        delay[N]: Delay;
        sink[N] : Sink;

    connections:
        src.out --> router++;
        for i=0...N-1{
            router.out++ --> srv[i].in++;
            srv[i].out --> delay[i].in++;
            delay[i].out --> sink[i].in++;
        }
}
```
All'interno del file è possibile definire dei for con struttura `for INDICE=START...END-1`. 

### FILE.ini.mako
Si definisce il FILE.ini.mako che viene utilizzato per creare tutte le configurazioni da testare. Si definisce la configurazione `General` in cui è essenziale il parametro `repeat = ...` che specifica il numero di volte per cui la configurazione verrà ripetuta (vale per tutte le configurazioni all'inteno del file). 
```mako
[General]
ned-path = .;../queueinglib
network = NETWORK
repeat = 5
cpu-time-limit = 60s
sim-time-limit = 10000s
**.vector-recording = false
```
Si definiscono poi le configurazioni specifiche inserendo al loro interno tutti i parametri necessari, ovvero tutti quei parametri che vogliamo siano conservati all'interno della simulazione. Si definiscono inoltre anche tutti i dettagli dei componenti specifici dell'esercizio, indicando quali salvare e come farlo. Per sapere quali sono i parametri dei componenti si utilizza la [sezione](#components).

Si può sfuttare la dicitura `extends=NOME_CONFIGURAZIONE` se si vuole creare una configurazione partendo da una già creata, specificando solamente i nuovi parametri da aggiungere. All'interno di ogni configurazione si utilizza la dicitura `**.SUBMODULE.ATTRIBUTO` dove il `SUBMODULE` è il nome che avevamo dato ad un componente, mentre con `ATTRIBUTO` si specifica l'attributo del componente che si vuole settare. Per accedere ai parametri definiti nel FILE.ned basta utilizzare `**.NOME_PARAMETRO` se però si trova nel nome della configurazione dobbiamo scrivere `NOME_PARAMETRO`.
```mako
[Config NOME_CONFIGURAZIONE]
extends = EXT_NOME_CONFIGURAZIONE
**.lambda = 200
**.srv[*].queueLenght.result-recording-modes = + histogram
**.router.randomGateIndex=(uniform(0, 10.0) <= 6.0 ? 0 : 1)
```
Grazie all'utilizzo dei cicli **for** è possibile definire più configurazioni ed utilizzare i gli elementi su cui il for esegue i cicli tramite `${INDICE}`. 
```mako
% for J in [0, 1, 2, 3, 4, 5]:
[Config NOME_CONFIGURAZIONE_${J}]
**.mu = ${J}

% endfor
```

## 1.2 - Commands
Una volta che abbiamo definito i file correttamente si procede grazie allo script **update_template.py** a creare il `FILE.ini` che utilizza `FILE.ned` e `FILE.ini.mako`. 
```bash
python3 ../../omnet_analyzer/update_template.py
```
Per verificare se la network è stata correttamente si può utilizzare il seguente comando dove `K` rappresenta la run specifica associata ad una particolare configurazione.
```bash
./queuenet -f ${FILE_NAME}.ini NOME_CONFIGURAZIONE -rK
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
# 2 - Parse results
Questa sezione si occupa della creazione dei results attraverso la simulazione delle configurazioni specificate. 

## 2.1 - Commands
Utilizzando il seguente comando e specificando `FILE.ini` viene creato il make file `Runfile` con all'interno tutte le configurazioni, il numero di run che devono essere eseguite, e tutte le dipendenze.  
```bash
python3 ../../omnet_analyzer/make_runfile.py -f ${FILE_NAME}.ini
```
Utilizzando il comando make vengono eseguite tutte le simulazioni e i risultati saranno inseriti in `results/`
```bash
make -j $(nproc) -f Runfile
```
In caso d'errori sarà necessario apportare correzioni e in tal caso risultano utili i comandi aggregati:
```bash
python3 ../../omnet_analyzer/update_template.py
python3 ../../omnet_analyzer/make_runfile.py -f ${FILE_NAME}.ini
make -j $(nproc) -f Runfile
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
# 3 - Analyze results
## 3.1 - Structure
Per analizzare i risultati abbiamo bisogno:
* configFILE.json --> Usato per estrarre i dati desiderati dalla cartella `results/`

Per creare il file usiamo
```bash
code config${FILE_NAME}.json
```

### configFile.json
All'interno del file definiamo le strutture:
* **scenario_schema**: si definiscono i parametri da selezionare
* **metrics**: si definiscono i parametri dei moduli da selezionare
* **histograms**: si definisce l'origine dei dati per l'histogram
* **analyses**: si definisce il nome dell'analyses e viene utilizzato per creare i file .data/histogram 
    * Definisce un histogram:
        * *outfile*: nome del file di output
        * *scenario*: 
        * *histogram*: 
    * Definisce una tabella:
        * *outfile*: nome del file di output
        * *scenario*: 
        * *metrics*: 


## 3.2 - Commands
Grazie a questo comando si utilizza il file `configFILE.json` per estrarre i dati dai *files.sca* e salvarli all'interno del nostro database. 
```bash
parse_data.py -c config${FILE_NAME}.json -d database.db -r rusults/NOME*.sca
```
Per visualizzare il database che abbiamo creato usiamo: 
```bash
sqlitebrowser database.db
```



# Anaylize data
Crea i file .data che abbiamo specificato all'interno del .json (in *analyses*), al cui interno sarà presente una tabella con i dati organizzati seguendo sempre le specifiche del .json.
```bash
analyze_data.py -c configNOME.json -d DATABASE.db
```









# Components
Segue una definizione dettagliata dei principali componenti che possono essere utilizzati all'interno di Omnet. 

## Source
Questo modulo si occupa della generazione di jobs. Si può specificarene il numero, l'oradio di inizio e di fine e l'intervallo tra la generazione dei job. La generazione dei job termina quando si produce il numero di job impostati o quando si raggiunge il limite di tempo.
```ned
simple Source
{
    parameters:
        @group(Queueing);
        @signal[created](type="long");
        @statistic[created](title="the number of jobs created";record=last;interpolationmode=none);
        @display("i=block/source");
        int numJobs = default(-1);               // number of jobs to be generated (-1 means no limit)
        volatile double interArrivalTime @unit(s); // time between generated jobs
        string jobName = default("job");         // the base name of the generated job (will be the module name if left empty)
        volatile int jobType = default(0);       // the type attribute of the created job (used by classifers and other modules)
        volatile int jobPriority = default(0);   // priority of the job
        double startTime @unit(s) = default(interArrivalTime); // when the module sends out the first job
        double stopTime @unit(s) = default(-1s); // when the module stops the job generation (-1 means no limit)
    gates:
        output out;
}
```
Visibile anche con il comando seguente eseguito dalla cartella di installazione di omnet:
```bash
cat samples/queueinglib Source.ned
```

## Router
Questo modulo si occupa dell'invio dei messaggi ai suoi output seguendo l'algoritmo specificato.
```ned
simple Router
{
    parameters:
        @group(Queueing);
        @display("i=block/routing");
        string routingAlgorithm @enum("random","roundRobin","shortestQueue","minDelay") = default("random");
        volatile int randomGateIndex = default(intuniform(0, sizeof(out)-1));    // the destination gate in case of random routing
    gates:
        input in[];
        output out[];
}
```
Visibile anche con il comando seguente eseguito dalla cartella di installazione di omnet:
```bash
cat samples/queueinglib Router.ned
```

## Queue
Questo modulo rappresenta una coda con un server build-in (@statistic[busy]).
```ned
simple Queue
{
    parameters:
        @group(Queueing);
        @display("i=block/activeq;q=queue");
        @signal[dropped](type="long");
        @signal[queueLength](type="long");
        @signal[queueingTime](type="simtime_t");
        @signal[busy](type="bool");
        @statistic[dropped](title="drop event";record=vector?,count;interpolationmode=none);
        @statistic[queueLength](title="queue length";record=vector,timeavg,max;interpolationmode=sample-hold);
        @statistic[queueingTime](title="queueing time at dequeue";record=vector?,mean,max;unit=s;interpolationmode=none);
        @statistic[busy](title="server busy state";record=vector?,timeavg;interpolationmode=sample-hold);

        int capacity = default(-1);    // negative capacity means unlimited queue
        bool fifo = default(true);     // whether the module works as a queue (fifo=true) or a stack (fifo=false)
        volatile double serviceTime @unit(s);
    gates:
        input in[];
        output out;
}
```
Visibile anche con il comando seguente eseguito dalla cartella di installazione di omnet:
```bash
cat samples/queueinglib Queue.ned
```

## Delay
Questo modulo ha il compito di rallentare i messaggi di un tempo predefinito. Il tempo di ritardo può essere determinato come fisso o può essere una distribuzione. L'ordine dei messaggi in arrivo e in uscita **non è** potrebbe non essere lo stesso.
```
simple Delay
{
    parameters:
        @group(Queueing);
        @signal[delayedJobs](type="long");
        @statistic[delayedJobs](title="number of delayed jobs";record=vector?,timeavg,max;interpolationmode=sample-hold);
        @display("i=block/delay");
        volatile double delay @unit(s); // the requested delay time (can be a distribution)
    gates:
        input in[];                     // the incoming message gates
        output out;                     // outgoing message gate
}
```
Visibile anche con il comando seguente eseguito dalla cartella di installazione di omnet:
```bash
cat samples/queueinglib Delay.ned
```

## Sink
Questo modulo ha il compito di distruggere (o opzionalmente di salvare) i pacchetti e di raccogliere le statistiche. 
```
simple Sink
{
    parameters:
        @group(Queueing);
        @display("i=block/sink");
        @signal[lifeTime](type="simtime_t");
        @signal[totalQueueingTime](type="simtime_t");
        @signal[totalDelayTime](type="simtime_t");
        @signal[totalServiceTime](type="simtime_t");
        @signal[queuesVisited](type="long");
        @signal[delaysVisited](type="long");
        @signal[generation](type="long");
        @statistic[lifeTime](title="lifetime of arrived jobs";unit=s;record=vector,mean,max;interpolationmode=none);
        @statistic[totalQueueingTime](title="the total time spent in queues by arrived jobs";unit=s;record=vector?,mean,max;interpolationmode=none);
        @statistic[totalDelayTime](title="the total time spent in delay nodes by arrived jobs";unit=s;record=vector?,mean,max;interpolationmode=none);
        @statistic[totalServiceTime](title="the total time spent  by arrived jobs";unit=s;record=vector?,mean,max;interpolationmode=none);
        @statistic[queuesVisited](title="the total number of queues visited by arrived jobs";record=vector?,mean,max;interpolationmode=none);
        @statistic[delaysVisited](title="the total number of delays visited by arrived jobs";record=vector?,mean,max;interpolationmode=none);
        @statistic[generation](title="the generation of the arrived jobs";record=vector?,mean,max;interpolationmode=none);
        bool keepJobs = default(false); // whether to keep the received jobs till the end of simulation
    gates:
        input in[];
}
```
Visibile anche con il comando seguente eseguito dalla cartella di installazione di omnet:
```bash
cat samples/queueinglib Sink.ned
```










# file.ned

```ned
import org.omnetpp.queueing.Queue;
import org.omnetpp.queueing.Source;
import org.omnetpp.queueing.Sink;

network NETWORK {

    parameters:
        int K = default(10);
        double rho = default(0.8);
        double mu = default(10);
        double lambda = mu * rho;
        
        srv.capacity = K;
        # Usiamo 1s per definire l'unità di misura 
        srv.serviceTime = 1s * exponential(1 / mu);
        src.interArrivalTime = 1s * exponential(1 / lambda);

    submodules:
        src: Source;
        srv: Queue;
        sink: Sink;

    connections:
        src.out --> srv.in++;
        srv.out --> sink.in++;
    
}
```
Per sapere quali sono i parametri per un determinato oggetto possiamo utilizzare il suo file .ned che si trova nel path `samples/queuinglib/NOME_DEL_FILE`

Per sapere se nelle connections dobbiamo usare `.++` dobbiamo sempre guardare il file .ned del modulo e per quelli che presentano un input/output con un array dobbiamo metterli, altrimenti no. 


# file.ini.mako
```ini
[General]
ned-path = .;../queueinglib
network = NETWORK
repeat = 5
cpu-time-limit = 60s
sim-time-limit = 10000s
**.vector-recording = false

%for K in [5, 7, 10, -1]:

%for rho in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.85. 0.88, 0.9]:
[Config CONF_rho${"%03d" % int(rho * 100)}_K${K if K > 0 else "inf"}]

**.srv.queueLenght.result-recording-modes = + histogram
**.sink.lifeTime.result-recording-modes = + histogram
**.K = ${K}
**.rho = ${rho}

# Per specificare la politica di balancing del router
**.Balance="Default"
# Per bilanciare in modo differente il traffico (60% uno e 40% l'altro in questo caso)
**.r.randomGateIndex=(uniform(0, 10.0) <= 6.0 ? 0 : 1)

%endfor
%endfor


[Config CONF_2]
extends = NOME_CONF_DA_ESTENDERE

```

** significa qualsiasi oggetto con qualsisi indentazione



# Comandi

```bash
update_template.py
```
Dove K specifica la run desiderata (nell'esempio possiamo sceglire un numero J: `0<J<5`)
```bash
./queuenet -f FILE.ini NOME_CONFIGURAZIONE -rK
```

Per verificare quali dati sono stati prodotti
```bash
less results/NOME_CONFIGURAZIONE.TIPOLOGIA
```
* .sca file: contiene i dati scalari 
* .vec file: contiene i vettori
* .vci file: indice ai vettori, per migliorare le performance 


# Estrazione dei dati dai results prodotti





Questo comando prende tutte le configurazione per il numero di run che abbiamo impostato dal NOME_FILE.ini e crea un nuovo file Runfile che si comporta come un make file (si specifica come fare la compilazione dei file) in cui vengono inseriti anche tutte le dipendenze.
```bash
make_runfile.py -f NOME_FILE.ini
```
Dato che all'interno di Runfile abbiamo inserito tutte le dipendenze possiamo usare il comando make con l'opzione -j per lanciare in parallelo l'esecuzione su tutti i core.
```bash
make -j $(nproc) -f Runfile
```



# Parse results 
Il risultato di tutte le simulazioni vengono inseriti nella cartella results. 

### configNOME.json
* 
```json
{
    "scenario_schema": {
        "Balance": {"pattern": "**.Balance", "type": "varchar"},
        "lambda1": {"pattern": "**.lambda1", "type": "real"},
        "lambda2": {"pattern": "**.lambda2", "type": "real"},
        "mu1": {"pattern": "**.mu1", "type": "real"},
        "mu2": {"pattern": "**.mu2", "type": "real"}
    },
    "metrics": {
        "PQueue1": {"module": "**.sink1", "scalar_name": "queuesVisited:mean" ,"aggr": ["none"]},
        "ServiceTime1": {"module": "**.sink1", "scalar_name": "totalServiceTime:mean" ,"aggr": ["none"]},
        "WaitingTime1": {"module": "**.sink1", "scalar_name": "totalQueueingTime:mean" ,"aggr": ["none"]},
        "ResponseTime1": {"module": "**.sink1", "scalar_name": "lifeTime:mean" ,"aggr": ["none"]},
        "PQueue2": {"module": "**.sink2", "scalar_name": "queuesVisited:mean" ,"aggr": ["none"]},
        "ServiceTime2": {"module": "**.sink2", "scalar_name": "totalServiceTime:mean" ,"aggr": ["none"]},
        "WaitingTime2": {"module": "**.sink2", "scalar_name": "totalQueueingTime:mean" ,"aggr": ["none"]},
        "ResponseTime2": {"module": "**.sink2", "scalar_name": "lifeTime:mean" ,"aggr": ["none"]}
    },
    "histograms": {
        "SinkTime1": {"module": "**.sink1", "histogram_name": "lifeTime:histogram"},
        "SinkTime2": {"module": "**.sink2", "histogram_name": "lifeTime:histogram"}
    },
    "analyses": {
        "Hist_LB_US1": {
            "outfile": "results/MM1_LB_Unbalanced_Source_Nobal1.data",
            "scenario": {"mu1": "5.0", "mu2": "5.0", "lambda1": "4.5", "lambda2": "2.0", "Balance":"NoBal"},
            "histogram": "SinkTime1"
        },        
        "Hist_LB_US2": {
            "outfile": "results/MM1_LB_Unbalanced_Source_Nobal2.data",
            "scenario": {"mu1": "5.0", "mu2": "5.0", "lambda1": "4.5", "lambda2": "2.0", "Balance":"NoBal"},
            "histogram": "SinkTime2"
        }
    }
}
```

Usando questo comando andiamo ad utilizzare il file .json per estrarre i dati dal file.sca e andarli a salvare all'interno del nostro database. 

```bash
parse_data.py -c configMM1.json -d DATABASE.db -r rusults/NOME*.sca
```
Per visualizzare il database che abbiamo creato usiamo: 
```bash
sqlitebrowser DATABASE.db
```


# Anaylize data
Crea i file .data che abbiamo specificato all'interno del .json (in *analyses*), al cui interno sarà presente una tabella con i dati organizzati seguendo sempre le specifiche del .json.
```bash
analyze_data.py -c configNOME.json -d DATABASE.db
```



