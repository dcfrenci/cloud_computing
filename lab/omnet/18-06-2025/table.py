import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import t
import math
from plots import * 


def evaluate_ic(std_dev, confidence_level, n_replicas):
    df = n_replicas - 1
    alpha = 1 - (confidence_level / 100)
    q = 1 - (alpha / 2)
    t_critical = t.ppf(q, df)
    ic = t_critical * (std_dev / math.sqrt(n_replicas))
    return ic


print(f"Parte 1 ================================")
data = np.loadtxt("results/analysis_1.data")

tr1, tr2, trgl = data[1] * 1000, data[3] * 1000, data[5] * 1000
st1, st2, stgl = data[2], data[4], data[6]
c1, c2, cgl = evaluate_ic(st1, 67, 10) * 1000, evaluate_ic(st2, 67, 10) * 1000, evaluate_ic(stgl, 67, 10) * 1000

print(f"srv1    --> Tr = {tr1:.1f} +- {c1:.1f} ms")
print(f"srv2    --> Tr = {tr2:.1f} +- {c2:.1} ms")
print(f"Global  --> Tr = {trgl:.1f} +- {cgl:.1f} ms")


print(f"Parte 2 ================================")
data = np.loadtxt("results/analysis_2.data")

p, tr1, tr2, trgl = data[0] / 10, data[1] * 1000, data[3] * 1000, data[5] * 1000

print(f"p --> {p}")
print(f"Tr1 --> {tr1:.1f}")
print(f"Tr2 --> {tr2:.1f}")
print(f"TrG --> {trgl:.1f}")


print(f"Parte 3 ================================")
data = np.loadtxt("results/analysis_3.data")

for row in data:
    p, tr1, tr2, trgl = row[0] / 10, row[1] * 1000, row[3] * 1000, row[5] * 1000
    st1, st2, stgl = row[2], row[4], row[6]
    c1, c2, cgl = evaluate_ic(st1, 67, 10) * 1000, evaluate_ic(st2, 67, 10) * 1000, evaluate_ic(stgl, 67, 10) * 1000

    print(f"p = {p:.2f},   |   Tr1 = {tr1:.1f} +- {c1:.1f} ms,   |   Tr2 = {tr2:.1f} +- {c2:.1f} ms,   |   TrG = {trgl:.1f} +- {cgl:.1f} ms")




fig, ax = plt.subplots()
ax.set(xlabel='$p$', ylabel='Time [s]')

p = [row[0] for row in data]
t1 = [row[1] for row in data]
t2 = [row[3] for row in data]
tgl = [row[5] for row in data]
    


plot_line(ax, 'o--', None, 'Response Time 1', p, t1)
plot_line(ax, 'o--', None, 'Response Time 2', p, t2)
plot_line(ax, 'o--', None, 'Response Time Global', p, tgl)

plt.legend()
plt.savefig('sample.png')

plt.show()