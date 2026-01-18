import org.omnetpp.queueing.Source;
import org.omnetpp.queueing.Router;
import org.omnetpp.queueing.Queue;
import org.omnetpp.queueing.Delay;
import org.omnetpp.queueing.Sink;

network NETWORK {

    parameters:

        double lambda = default(200);
        int N = default(10);
        double mu = default(10);
        double c = default(1.5);
        
        src.interArrivalTime = 1s * exponential(1 / lambda);
        
        srv[*].serviceTime = 1s * exponential(1 / mu);


    submodules:
        src     : Source;
        router  : Router;
        srv[N]  : Queue;
        sink    : Sink;

    connections:
        src.out --> router.in++;
        for i=0..N-1{
            router.out++ --> srv[i].in++;
            srv[i].out --> sink.in++;
        }
}