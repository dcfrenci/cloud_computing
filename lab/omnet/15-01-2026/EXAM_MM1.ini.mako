[General]
ned-path = .;../queueinglib
network = NETWORK
repeat = 10
sim-time-limit = 1000s
**.vector-recording = false


[Config CONF_PARTE_1]
**.prob = 5.0
**.router.randomGateIndex=(uniform(0, 10.0) <= 5.0 ? 0 : 1)
**.sink1.lifeTime.result-recording-modes =+ mean
**.sink2.lifeTime.result-recording-modes =+ mean
**.sinkgl.lifeTime.result-recording-modes =+ mean

% for J in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]:
[Config CONF_PARTE_2_P_${"%03d" % int(J * 100)}]
**.prob = ${J}
**.router.randomGateIndex=(uniform(0, 10.0) <= ${J} ? 0 : 1)
**.sink1.lifeTime.result-recording-modes =+ mean
**.sink2.lifeTime.result-recording-modes =+ mean
**.sinkgl.lifeTime.result-recording-modes =+ mean
% endfor

[Config CONF_PARTE_3]
**.prob = 3.125
**.router.randomGateIndex=(uniform(0, 10.0) <= 3.125 ? 0 : 1)
**.sink1.lifeTime.result-recording-modes =+ mean
**.sink2.lifeTime.result-recording-modes =+ mean
**.sinkgl.lifeTime.result-recording-modes =+ mean
