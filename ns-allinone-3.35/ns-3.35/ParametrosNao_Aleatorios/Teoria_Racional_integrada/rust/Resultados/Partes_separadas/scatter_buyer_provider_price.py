# scatter_buyer_provider_price.py
import json, pandas as pd, matplotlib.pyplot as plt
with open("racional_resultados.json") as f:
    data = json.load(f)
buyers = pd.DataFrame(data["buyers"]); providers = pd.DataFrame(data["providers"]); matches = pd.DataFrame(data["matches"])
accepted = matches[matches["accepted"]==True]
price_map = providers.set_index("id")["price"].to_dict()
accepted["provider_price"] = accepted["provider_id"].map(price_map)
plt.scatter(accepted["max_price"].values, accepted["provider_price"].values)
plt.title("buyer max_price vs provider price (matches aceitas)")
plt.xlabel("buyer max_price (R$/GB)"); plt.ylabel("provider price (R$/GB)")
plt.savefig("scatter_buyer_maxprice_providerprice.png", bbox_inches="tight")