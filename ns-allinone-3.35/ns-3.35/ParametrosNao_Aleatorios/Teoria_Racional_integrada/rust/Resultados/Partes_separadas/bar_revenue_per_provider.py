# bar_revenue_per_provider.py
import json, pandas as pd, matplotlib.pyplot as plt
with open("racional_resultados.json") as f:
    data = json.load(f)
buyers = pd.DataFrame(data["buyers"]); providers = pd.DataFrame(data["providers"]); matches = pd.DataFrame(data["matches"])
accepted = matches[matches["accepted"]==True]
price_map = providers.set_index("id")["price"].to_dict()
rev = {}
for _, r in accepted.iterrows():
    pid = r["provider_id"]; bid = r["buyer_id"]
    buyer_storage = buyers[buyers["id"]==bid]["storage"].values[0]
    rev[pid] = rev.get(pid, 0) + price_map.get(pid,0) * buyer_storage
pd.Series(rev).sort_index().plot(kind="bar")
plt.title("Receita estimada por provedor (matches aceitas)")
plt.xlabel("provider_id"); plt.ylabel("receita (R$)")
plt.savefig("bar_revenue_per_provider.png", bbox_inches="tight")