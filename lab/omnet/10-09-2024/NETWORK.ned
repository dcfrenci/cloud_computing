import org.omnetpp.queueing.Source;
import org.omnetpp.queueing.Router;
import org.omnetpp.queueing.Queue;
import org.omnetpp.queueing.Delay;
import org.omnetpp.queueing.Sink;

network NETWORK {
    parameters:
        double mu = default(10);
        double lambda = default(10);
        double fl = default(0.5);

        double l_lambda = lambda * fl;
        double c_lambda = lambda * (1 - fl);

        lsrc.interArrivalTime = 1s * exponential(1 / l_lambda);
        csrc.interArrivalTime = 1s * exponential(1 / c_lambda);
        
        lsrv.serviceTime = 1s * exponential(1 / mu);
        csrv.serviceTime = 1s * exponential(0.07);
        cdelay.delay = 1s * exponential(1 / mu);

    submodules:
        lsrc     : Source;
        csrc     : Source;
        lsrv    : Queue;
        csrv    : Queue;
        cdelay  : Delay;
        sink    : Sink;
        csink   : Sink;

    connections:
        lsrc.out --> lsrv.in++;
        lsrv.out --> sink.in++;

        csrc.out --> csrv.in++;
        csrv.out --> cdelay.in++;
        cdelay.out --> csink.in++;

}