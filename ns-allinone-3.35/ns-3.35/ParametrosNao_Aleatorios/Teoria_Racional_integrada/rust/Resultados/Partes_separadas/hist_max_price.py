# hist_max_price.py
import json, pandas as pd, matplotlib.pyplot as plt
with open("racional_resultados.json") as f:
    data = json.load(f)
buyers = pd.DataFrame(data["buyers"])
plt.hist(buyers["max_price"].values, bins=8)
plt.title("Distribuição de max_price (R$/GB)")
plt.xlabel("max_price (R$/GB)"); plt.ylabel("contagem")
plt.savefig("hist_max_price.png", bbox_inches="tight")