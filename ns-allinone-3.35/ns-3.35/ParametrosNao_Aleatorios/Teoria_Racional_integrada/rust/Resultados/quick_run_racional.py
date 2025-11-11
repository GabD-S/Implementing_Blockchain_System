#!/usr/bin/env python3
"""
quick_run_racional.py
Runs a core subset of plots (histograms + provider scatter) for fast inspection.
Refactored for better visuals.
"""
import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  # Importado
import imageio
import numpy as np

DATA_PATH = Path("racional_resultados.json")
# --- Diretório de Saída Atualizado ---
OUT_DIR = Path("PR_Q")  # ATUALIZADO
OUT_DIR.mkdir(exist_ok=True, parents=True)

# --- Adicionado Estilo Seaborn ---
sns.set_style("whitegrid")

if not DATA_PATH.exists():
    print(f"Arquivo {DATA_PATH} não encontrado.")
    exit(1)
with open(DATA_PATH, "r") as f:
    data = json.load(f)

buyers = pd.DataFrame(data.get("buyers", []))
providers = pd.DataFrame(data.get("providers", []))
matches = pd.DataFrame(data.get("matches", []))

# --- Função save_fig Atualizada ---
def save_fig(fig, p):
    fig.tight_layout()  # Adicionado para melhor espaçamento
    fig.savefig(p)
    plt.close(fig)

print(f"Salvando gráficos rápidos em: {OUT_DIR}")

# --- Gráficos Atualizados com Seaborn ---

# 1. Histograma de Budgets
if not buyers.empty and "budget" in buyers:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(data=buyers, x="budget", kde=True, ax=ax, bins=15, color='blue')
    ax.set_title("Distribuição de Budgets (ref_point)", fontsize=16)
    ax.set_xlabel("Budget (R$)", fontsize=12)
    ax.set_ylabel("Number of Buyers", fontsize=12)  # Updated from 'Count'
    ax.grid(True, linestyle='--', alpha=0.5)
    save_fig(fig, OUT_DIR/"hist_budget.png")
    print("wrote hist_budget.png")
else:
    print("Skipping hist_budget.png (dados ausentes)")

# 2. Histograma de Storage
if not buyers.empty and "storage" in buyers:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(data=buyers, x="storage", kde=True, ax=ax, bins=15, color='green')
    ax.set_title("Distribuição de Armazenamento (storage)", fontsize=16)
    ax.set_xlabel("Storage Demand (GB)", fontsize=12)
    ax.set_ylabel("Number of Buyers", fontsize=12)  # Updated from 'Count'
    ax.grid(True, linestyle='--', alpha=0.5)
    save_fig(fig, OUT_DIR/"hist_storage.png")
    print("wrote hist_storage.png")
else:
    print("Skipping hist_storage.png (dados ausentes)")

# 3. Scatter Plot de Provedores
if not providers.empty and "capacity" in providers and "price" in providers:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=providers, x="capacity", y="price", size="capacity",
                    sizes=(50, 250), alpha=0.7, ax=ax, legend='auto')
    ax.set_title("Provedores: Preço vs. Capacidade", fontsize=16)
    ax.set_xlabel("Capacity (GB)", fontsize=12)
    ax.set_ylabel("Number of Providers", fontsize=12)  # Updated from 'Count'
    ax.grid(True, linestyle='--', alpha=0.5)
    save_fig(fig, OUT_DIR/"providers.png")
    print("wrote providers.png")
else:
    print("Skipping providers.png (dados ausentes)")

print("--- Quick run concluído ---")