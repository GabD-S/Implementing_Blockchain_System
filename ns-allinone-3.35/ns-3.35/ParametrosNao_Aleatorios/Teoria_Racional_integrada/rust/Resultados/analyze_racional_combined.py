#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  # Importado
import imageio
import sys
import numpy as np

# --- Diretório de Saída Atualizado ---
DATA_PATH = Path("racional_resultados.json")
OUT_DIR = Path("PR_R")  # ATUALIZADO
OUT_DIR.mkdir(exist_ok=True, parents=True)

def load_data(path=DATA_PATH):
    with open(path, "r") as f:
        data = json.load(f)
        buyers = pd.DataFrame(data.get("buyers", []))
        providers = pd.DataFrame(data.get("providers", []))
        matches = pd.DataFrame(data.get("matches", []))
        # Garantir tipos corretos
        for df in [buyers, providers, matches]:
            if not df.empty:
                for col in df.columns:
                    if df[col].dtype == object:
                        try:
                            df[col] = pd.to_numeric(df[col], errors='ignore')
                        except Exception:
                            pass
    return buyers, providers, matches, data

# --- Função save_fig Atualizada ---
def save_fig(fig, p):
    fig.tight_layout()  # Adicionado para melhor espaçamento
    fig.savefig(p)
    plt.close(fig)

# --- Gráficos Atualizados com Seaborn ---

def hist_budget(buyers):
    if buyers.empty or "budget" not in buyers:
        print("buyers vazio ou sem coluna 'budget'")
        return
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(data=buyers, x="budget", kde=True, ax=ax, bins=15, color='blue')
    ax.set_title("Distribuição de budgets dos compradores", fontsize=16)
    ax.set_xlabel("Budget (R$)", fontsize=12)
    ax.set_ylabel("Number of Buyers", fontsize=12)  # Updated from 'Count'
    ax.grid(True, linestyle='--', alpha=0.5)
    save_fig(fig, OUT_DIR / "hist_budget.png")
    print("wrote hist_budget.png")

def hist_storage(buyers):
    if buyers.empty or "storage" not in buyers:
        print("buyers vazio ou sem coluna 'storage'")
        return
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(data=buyers, x="storage", kde=True, ax=ax, bins=15, color='green')
    ax.set_title("Distribuição de storage demand (GB)", fontsize=16)
    ax.set_xlabel("Storage Demand (GB)", fontsize=12)
    ax.set_ylabel("Number of Buyers", fontsize=12)  # Updated from 'Count'
    ax.grid(True, linestyle='--', alpha=0.5)
    save_fig(fig, OUT_DIR / "hist_storage.png")
    print("wrote hist_storage.png")

def hist_max_price(buyers):
    if buyers.empty or "max_price" not in buyers:
        print("buyers vazio ou sem coluna 'max_price'")
        return
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(data=buyers, x="max_price", kde=True, ax=ax, bins=15, color='red')
    ax.set_title("Distribuição de max_price (R$/GB)", fontsize=16)
    ax.set_xlabel("Max Price (R$/GB)", fontsize=12)
    ax.set_ylabel("Number of Buyers", fontsize=12)  # Updated from 'Count'
    ax.grid(True, linestyle='--', alpha=0.5)
    save_fig(fig, OUT_DIR / "hist_max_price.png")
    print("wrote hist_max_price.png")

def providers_scatter(providers):
    if providers.empty or "capacity" not in providers or "price" not in providers:
        print("providers vazio ou sem colunas 'capacity'/'price'")
        return
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=providers, x="capacity", y="price", size="capacity",
                    sizes=(50, 250), alpha=0.7, ax=ax, legend='auto')
    ax.set_title("Preço por GB dos provedores vs capacidade (GB)", fontsize=16)
    ax.set_xlabel("Capacity (GB)", fontsize=12)
    ax.set_ylabel("Price (R$/GB)", fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.5)
    save_fig(fig, OUT_DIR / "providers_price_capacity.png")
    print("wrote providers_price_capacity.png")

def hist_utilities_accepted(matches):
    if matches.empty or "accepted" not in matches or "utility" not in matches:
        print("matches vazio ou sem colunas 'accepted'/'utility'")
        return
    accepted = matches[matches["accepted"] == True].copy()
    if accepted.empty:
        print("Nenhuma match aceita encontrada.")
        return
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(data=accepted, x="utility", kde=True, ax=ax, bins=15, color='purple')
    ax.set_title("Distribuição de utilidades nas matches aceitas", fontsize=16)
    ax.set_xlabel("Utility", fontsize=12)
    ax.set_ylabel("Number of Matches", fontsize=12)  # Updated from 'Count'
    ax.grid(True, linestyle='--', alpha=0.5)
    save_fig(fig, OUT_DIR / "hist_utilities_accepted.png")
    print("wrote hist_utilities_accepted.png")

def bar_matches_per_provider(matches, providers):
    if matches.empty or providers.empty or "accepted" not in matches or "provider_id" not in matches or "id" not in providers:
        print("Dados insuficientes para matches por provedor.")
        return pd.Series()
    accepted = matches[matches["accepted"] == True].copy()
    provider_ids = providers["id"].tolist()
    counts = {pid: 0 for pid in provider_ids}
    for _, r in accepted.iterrows():
        pid = r.get("provider_id")
        if pid in counts:
            counts[int(pid)] += 1
    s = pd.Series(counts).sort_index()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=s.index.astype(str), y=s.values, ax=ax, palette="viridis")
    ax.set_title("Número de matches aceitas por provedor", fontsize=16)
    ax.set_xlabel("Provider ID", fontsize=12)
    ax.set_ylabel("Accepted Matches (Count)", fontsize=12)  # Updated from 'Count'
    ax.grid(True, linestyle='--', alpha=0.5, axis='y')
    save_fig(fig, OUT_DIR / "bar_matches_per_provider.png")
    print("wrote bar_matches_per_provider.png")
    return s

def scatter_buyer_provider_price(buyers, providers, matches):
    if buyers.empty or providers.empty or matches.empty:
        print("Dados insuficientes para scatter buyer/provider price.")
        return
    accepted = matches[matches["accepted"] == True].copy()
    if accepted.empty or "provider_id" not in accepted or "max_price" not in accepted:
        print("Nenhuma match aceita ou dados faltando.")
        return
    prov_price_map = providers.set_index("id")["price"].to_dict() if "id" in providers and "price" in providers else {}
    accepted["provider_price"] = accepted["provider_id"].map(prov_price_map)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.regplot(data=accepted, x="max_price", y="provider_price", ax=ax,
                line_kws={"color":"red","lw":2},
                scatter_kws={"alpha":0.7,"s":50})
    ax.set_title("buyer max_price vs provider price (matches aceitas)", fontsize=16)
    ax.set_xlabel("Buyer Max Price (R$/GB)", fontsize=12)
    ax.set_ylabel("Provider Price (R$/GB)", fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.5)
    save_fig(fig, OUT_DIR / "scatter_buyer_maxprice_providerprice.png")
    print("wrote scatter_buyer_maxprice_providerprice.png")

def bar_revenue_per_provider(buyers, providers, matches):
    if buyers.empty or providers.empty or matches.empty:
        print("Dados insuficientes para receita por provedor.")
        return
    accepted = matches[matches["accepted"] == True].copy()
    if accepted.empty or "provider_id" not in accepted or "buyer_id" not in accepted:
        print("Nenhuma match aceita ou dados faltando.")
        return
    prov_price_map = providers.set_index("id")["price"].to_dict() if "id" in providers and "price" in providers else {}
    provider_ids = providers["id"].tolist() if "id" in providers else []
    rev = {pid: 0.0 for pid in provider_ids}
    for _, r in accepted.iterrows():
        pid = r.get("provider_id")
        bid = r.get("buyer_id")
        buyer_storage = buyers.loc[buyers["id"] == bid, "storage"].values[0] if not buyers.empty and "id" in buyers and "storage" in buyers else 0.0
        rev[int(pid)] += prov_price_map.get(int(pid), 0.0) * buyer_storage
    s = pd.Series(rev).sort_index()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=s.index.astype(str), y=s.values, ax=ax, palette="magma")
    ax.set_title("Receita estimada por provedor (matches aceitas)", fontsize=16)
    ax.set_xlabel("Provider ID", fontsize=12)
    ax.set_ylabel("Revenue (R$)", fontsize=12)  # Updated from 'Count'
    ax.grid(True, linestyle='--', alpha=0.5, axis='y')
    save_fig(fig, OUT_DIR / "bar_revenue_per_provider.png")
    print("wrote bar_revenue_per_provider.png")

def main():
    # --- Adicionado Estilo Seaborn ---
    sns.set_style("whitegrid")
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--all', action='store_true', help='generate all plots')
    parser.add_argument('--plot', type=str, default=None, help='single plot name to generate')
    args = parser.parse_args()

    buyers, providers, matches, raw = load_data()
    available = [
        'hist_budget','hist_storage','hist_max_price','providers_scatter',
        'hist_utilities_accepted','bar_matches_per_provider','scatter_buyer_provider_price',
        'bar_revenue_per_provider','acc_matches_animation'
    ]

    if args.all:
        hist_budget(buyers); hist_storage(buyers); hist_max_price(buyers)
        providers_scatter(providers); hist_utilities_accepted(matches)
        s = bar_matches_per_provider(matches, providers)
        scatter_buyer_provider_price(buyers, providers, matches)
        bar_revenue_per_provider(buyers, providers, matches)
        
        # save CSVs and a short summary
        buyers.to_csv(OUT_DIR / 'buyers.csv', index=False)
        providers.to_csv(OUT_DIR / 'providers.csv', index=False)
        matches.to_csv(OUT_DIR / 'matches.csv', index=False)
        with open(OUT_DIR / 'conclusions.txt', 'w') as f:
            f.write(f"acceptance_rate: {raw.get('acceptance_rate')}\n")
            f.write(f"compradores: {len(buyers)}, provedores: {len(providers)}, matches: {len(matches)}\n")
            f.write(f"matches aceitas: {len(matches[matches['accepted']==True])}\n")
        print('all done')
        return

    if args.plot:
        name = args.plot
        if name not in available and name != 'all':
            print('unknown plot:', name)
            print('available:', available); sys.exit(1)
        if name == 'hist_budget': hist_budget(buyers)
        if name == 'hist_storage': hist_storage(buyers)
        if name == 'hist_max_price': hist_max_price(buyers)
        if name == 'providers_scatter': providers_scatter(providers)
        if name == 'hist_utilities_accepted': hist_utilities_accepted(matches)
        if name == 'bar_matches_per_provider': bar_matches_per_provider(matches, providers)
        if name == 'scatter_buyer_provider_price': scatter_buyer_provider_price(buyers, providers, matches)
        if name == 'bar_revenue_per_provider': bar_revenue_per_provider(buyers, providers, matches)
        return

    parser.print_help()

if __name__ == '__main__':
    main()