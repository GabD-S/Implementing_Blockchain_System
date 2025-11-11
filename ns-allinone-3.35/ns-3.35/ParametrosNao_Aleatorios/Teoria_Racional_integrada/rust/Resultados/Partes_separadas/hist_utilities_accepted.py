# hist_utilities_accepted.py
import json, pandas as pd, matplotlib.pyplot as plt
with open("racional_resultados.json") as f:
    data = json.load(f)
matches = pd.DataFrame(data["matches"])
accepted = matches[matches["accepted"]==True]
plt.hist(accepted["utility"].values, bins=8)
plt.title("Distribuição de utilidades nas matches aceitas")
plt.xlabel("utility"); plt.ylabel("contagem")
plt.savefig("hist_utilities_accepted.png", bbox_inches="tight")