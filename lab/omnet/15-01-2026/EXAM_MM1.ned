import org.omnetpp.queueing.Source;
import org.omnetpp.queueing.Router;
import org.omnetpp.queueing.Queue;
import org.omnetpp.queueing.Clone;
import org.omnetpp.queueing.Sink;

network NETWORK {

    parameters:
        double mu1 = default(25);
        double mu2 = default(40);
        double lambda = default(40);
        double prob = default(5.0);

        src.interArrivalTime = 1s * exponential(1 / lambda);

        srv1.serviceTime = 1s * exponential(1 / mu1);
        srv2.serviceTime = 1s * exponential(1 / mu2);


    submodules:
        src     : Source;
        router  : Router;
        srv1    : Queue;
        srv2    : Queue;
        clone1  : Clone;
        clone2  : Clone;
        sink1   : Sink;
        sink2   : Sink;
        sinkgl  : Sink;

    connections:
        src.out --> router.in++;
        
        router.out++ --> srv1.in++;
        srv1.out --> clone1.in++;
        clone1.out++ --> sink1.in++;
        clone1.out++ --> sinkgl.in++;

        router.out++ --> srv2.in++;
        srv2.out --> clone2.in++;
        clone2.out++ --> sink2.in++;
        clone2.out++ --> sinkgl.in++;
}