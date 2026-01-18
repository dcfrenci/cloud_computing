[General]
ned-path = .;../queueinglib
network = NETWORK
repeat = 5
sim-time-limit = 10000s
**.vector-recording = false

[Config CONF_1]
**.srv[*].busy.result-recording-modes =+ mean
**.sink.lifeTime.result-recording-modes =+ mean
**.mu = 10
**.c = 1.5
**.N = 34


[Config CONF_2]
**.srv[*].busy.result-recording-modes =+ mean
**.sink.lifeTime.result-recording-modes =+ mean
**.mu = 15
**.c = 2.5
**.N = 19


% for J in [25, 30, 35, 40, 45, 50]:
[Config TERZA_${J}]
**.srv[*].busy.result-recording-modes =+ mean
**.sink.lifeTime.result-recording-modes =+ mean
**.mu = 10
**.c = 1.5
**.N= ${J}
% endfor


% for J in [25, 30, 35, 40, 45, 50]:
[Config TERZA_${J}]
**.srv[*].busy.result-recording-modes =+ mean
**.sink.lifeTime.result-recording-modes =+ mean
**.mu = 15
**.c = 2.5
**.N= ${J}
% endfor
