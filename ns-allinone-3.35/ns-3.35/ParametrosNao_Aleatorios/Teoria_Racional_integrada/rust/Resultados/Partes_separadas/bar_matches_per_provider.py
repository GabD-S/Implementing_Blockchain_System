# bar_matches_per_provider.py
import json, pandas as pd, matplotlib.pyplot as plt
with open("racional_resultados.json") as f:
    data = json.load(f)
matches = pd.DataFrame(data["matches"])
providers = pd.DataFrame(data["providers"])
accepted = matches[matches["accepted"]==True]
counts = accepted["provider_id"].value_counts().sort_index()
counts.plot(kind="bar")
plt.title("Número de matches aceitas por provedor")
plt.xlabel("provider_id"); plt.ylabel("aceitas (contagem)")
plt.savefig("bar_matches_per_provider.png", bbox_inches="tight")