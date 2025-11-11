# providers_price_capacity.py
import json, pandas as pd, matplotlib.pyplot as plt
with open("racional_resultados.json") as f:
    data = json.load(f)
providers = pd.DataFrame(data["providers"])
sizes = (providers["capacity"].values / providers["capacity"].max()) * 200
plt.scatter(providers["capacity"].values, providers["price"].values, s=sizes)
plt.title("Preço por GB dos provedores vs capacidade (GB)")
plt.xlabel("capacidade (GB)"); plt.ylabel("price (R$/GB)")
plt.savefig("providers_price_capacity.png", bbox_inches="tight")