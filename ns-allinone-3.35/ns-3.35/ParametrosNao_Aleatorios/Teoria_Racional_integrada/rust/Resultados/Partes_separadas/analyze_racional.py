#!/usr/bin/env python3
# analyze_racional.py
# Gere todos os gráficos e a animação a partir de racional_resultados.json
# Requisitos: pandas, matplotlib, imageio
# pip install pandas matplotlib imageio

import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import imageio

DATA_PATH = Path("racional_resultados.json")  # coloque o json no mesmo diretório
OUT_DIR = Path("plots_racional")
OUT_DIR.mkdir(parents=True, exist_ok=True)

with open(DATA_PATH, "r") as f:
    data = json.load(f)

buyers = pd.DataFrame(data.get("buyers", []))
providers = pd.DataFrame(data.get("providers", []))
matches = pd.DataFrame(data.get("matches", []))

def save_fig(fig, path):
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)

# 1) hist budgets
fig, ax = plt.subplots(figsize=(6,4))
ax.hist(buyers["budget"].values, bins=8)
ax.set_title("Distribuição de budgets dos compradores")
ax.set_xlabel("budget (R$)")
ax.set_ylabel("contagem")
save_fig(fig, OUT_DIR / "hist_budget.png")

# 2) hist storage demand
fig, ax = plt.subplots(figsize=(6,4))
ax.hist(buyers["storage"].values, bins=8)
ax.set_title("Distribuição de storage demand (GB)")
ax.set_xlabel("storage (GB)")
ax.set_ylabel("contagem")
save_fig(fig, OUT_DIR / "hist_storage.png")

# 3) hist max_price (wtp)
fig, ax = plt.subplots(figsize=(6,4))
ax.hist(buyers["max_price"].values, bins=8)
ax.set_title("Distribuição de max_price (R$/GB)")
ax.set_xlabel("max_price (R$/GB)")
ax.set_ylabel("contagem")
save_fig(fig, OUT_DIR / "hist_max_price.png")

# 4) providers scatter price vs capacity
fig, ax = plt.subplots(figsize=(6,4))
sizes = (providers["capacity"].values / providers["capacity"].max()) * 200
ax.scatter(providers["capacity"].values, providers["price"].values, s=sizes)
ax.set_title("Preço por GB dos provedores vs capacidade (GB)")
ax.set_xlabel("capacidade (GB)")
ax.set_ylabel("price (R$/GB)")
save_fig(fig, OUT_DIR / "providers_price_capacity.png")

# 5) utilities for accepted matches
accepted_matches = matches[matches["accepted"] == True].copy()
fig, ax = plt.subplots(figsize=(6,4))
ax.hist(accepted_matches["utility"].values, bins=8)
ax.set_title("Distribuição de utilidades nas matches aceitas")
ax.set_xlabel("utility")
ax.set_ylabel("contagem")
save_fig(fig, OUT_DIR / "hist_utilities_accepted.png")

# 6) matches per provider
provider_ids = providers["id"].tolist()
provider_match_counts = {pid: 0 for pid in provider_ids}
for _, r in accepted_matches.iterrows():
    pid = int(r["provider_id"])
    if pid in provider_match_counts:
        provider_match_counts[pid] += 1
counts_series = pd.Series(provider_match_counts).sort_index()
fig, ax = plt.subplots(figsize=(6,4))
ax.bar(counts_series.index.astype(str), counts_series.values)
ax.set_title("Número de matches aceitas por provedor")
ax.set_xlabel("provider_id")
ax.set_ylabel("aceitas (contagem)")
save_fig(fig, OUT_DIR / "bar_matches_per_provider.png")

# 7) buyer max_price vs provider price (for accepted matches)
prov_price_map = providers.set_index("id")["price"].to_dict()
accepted_matches["provider_price"] = accepted_matches["provider_id"].map(prov_price_map)
fig, ax = plt.subplots(figsize=(6,4))
ax.scatter(accepted_matches["max_price"].values, accepted_matches["provider_price"].values)
ax.set_title("buyer max_price vs provider price (matches aceitas)")
ax.set_xlabel("buyer max_price (R$/GB)")
ax.set_ylabel("provider price (R$/GB)")
save_fig(fig, OUT_DIR / "scatter_buyer_maxprice_providerprice.png")

# 8) revenue per provider (estimate: provider price * buyer storage)
rev_per_provider = {pid: 0.0 for pid in provider_ids}
for _, row in accepted_matches.iterrows():
    pid = int(row["provider_id"])
    buyer_id = int(row["buyer_id"])
    buyer_storage = buyers.loc[buyers["id"] == buyer_id, "storage"].values[0]
    price = prov_price_map.get(pid, 0.0)
    rev_per_provider[pid] += price * buyer_storage
rev_series = pd.Series(rev_per_provider).sort_index()
fig, ax = plt.subplots(figsize=(6,4))
ax.bar(rev_series.index.astype(str), rev_series.values)
ax.set_title("Receita estimada por provedor (matches aceitas)")
ax.set_xlabel("provider_id")
ax.set_ylabel("receita (R$)")
save_fig(fig, OUT_DIR / "bar_revenue_per_provider.png")

# 9) GIF: acumulando matches por provider passo a passo
match_list = matches.to_dict("records")
providers_sorted = sorted(provider_ids)
acc_seq = []
acc = {pid: 0 for pid in providers_sorted}
for rec in match_list:
    if rec.get("accepted") == True:
        pid = int(rec["provider_id"])
        if pid in acc:
            acc[pid] += 1
    acc_seq.append(acc.copy())

frame_paths = []
for i, state in enumerate(acc_seq):
    fig, ax = plt.subplots(figsize=(6,4))
    s = pd.Series(state).reindex(providers_sorted)
    ax.bar([str(x) for x in providers_sorted], s.values)
    ax.set_ylim(0, max(3, max(s.values)+1))
    ax.set_title(f"Matches acumuladas por provedor - passo {i+1}/{len(acc_seq)}")
    ax.set_xlabel("provider_id")
    ax.set_ylabel("aceitas acumuladas")
    p = OUT_DIR / f"frame_{i:03d}.png"
    fig.savefig(p, bbox_inches="tight")
    plt.close(fig)
    frame_paths.append(str(p))

gif_path = OUT_DIR / "acc_matches_animation.gif"
with imageio.get_writer(gif_path, mode="I", duration=0.6) as writer:
    for fp in frame_paths:
        img = imageio.imread(fp)
        writer.append_data(img)

# cleanup frames
import os
for fp in frame_paths:
    os.remove(fp)

# save CSVs and summary
buyers.to_csv(OUT_DIR / "buyers.csv", index=False)
providers.to_csv(OUT_DIR / "providers.csv", index=False)
matches.to_csv(OUT_DIR / "matches.csv", index=False)

most_match_provider = counts_series.idxmax() if not counts_series.empty else None
summary_lines = [
    f"acceptance_rate: {data.get('acceptance_rate')}",
    f"compradores: {len(buyers)}, provedores: {len(providers)}, matches: {len(matches)}",
    f"matches aceitas: {len(accepted_matches)}",
    f"provedor mais atendido: {most_match_provider} (count {counts_series.max()})",
    f"avg buyer max_price: {buyers['max_price'].mean() if 'max_price' in buyers.columns else 'n/a'}",
    f"avg provider price (accepted matches): {accepted_matches['provider_price'].mean() if not accepted_matches.empty else 'n/a'}"
]
with open(OUT_DIR / "conclusions.txt", "w") as f:
    f.write("\\n".join(summary_lines))

print('Geração finalizada. veja a pasta', OUT_DIR)
