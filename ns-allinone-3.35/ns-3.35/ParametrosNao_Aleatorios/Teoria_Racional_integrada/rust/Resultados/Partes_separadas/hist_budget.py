# hist_budget.py
import json, pandas as pd, matplotlib.pyplot as plt
with open("racional_resultados.json") as f:
    data = json.load(f)
buyers = pd.DataFrame(data["buyers"])
plt.hist(buyers["budget"].values, bins=8)
plt.title("Distribuição de budgets dos compradores")
plt.xlabel("budget (R$)"); plt.ylabel("contagem")
plt.savefig("hist_budget.png", bbox_inches="tight")