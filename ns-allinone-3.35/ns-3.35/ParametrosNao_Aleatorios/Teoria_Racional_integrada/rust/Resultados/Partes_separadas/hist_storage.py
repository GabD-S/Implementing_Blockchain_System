# hist_storage.py
import json, pandas as pd, matplotlib.pyplot as plt
with open("racional_resultados.json") as f:
    data = json.load(f)
buyers = pd.DataFrame(data["buyers"])
plt.hist(buyers["storage"].values, bins=8)
plt.title("Distribuição de storage demand (GB)")
plt.xlabel("storage (GB)"); plt.ylabel("contagem")
plt.savefig("hist_storage.png", bbox_inches="tight")