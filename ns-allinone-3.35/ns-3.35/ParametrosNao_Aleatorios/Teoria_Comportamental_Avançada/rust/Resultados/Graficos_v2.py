import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Estilo consistente com Graficos.py
sns.set_style("whitegrid")

print("Carregando comportamental_resultados.json...")
with open('comportamental_resultados.json', 'r') as f:
    data = json.load(f)

# DataFrames
df_buyers = pd.DataFrame(data['buyers'])
df_providers = pd.DataFrame(data['providers'])
df_decisions = pd.DataFrame(data['decisions'])

# Merge para análises conjuntas
if not df_decisions.empty:
    df_analysis = pd.merge(df_decisions, df_buyers, left_on='buyer_id', right_on='id', suffixes=('_decision', '_buyer'))
    df_analysis = pd.merge(df_analysis, df_providers, left_on='provider_id', right_on='id', suffixes=('_analysis', '_provider'))
else:
    df_analysis = pd.DataFrame()

print("Dados carregados e preparados.")

# Pasta de saída nova
output_dir = "graficos_analise_comportamental_v2"
os.makedirs(output_dir, exist_ok=True)
print(f"Diretório '{output_dir}' pronto.")

# 1) Provider Landscape (mesmo visual)
print("Gerando Gráfico v2-1: provider_landscape_v2.png")
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_providers, x='reputation', y='price', s=100, alpha=0.7, label='Provedores')
plt.title('Cenário de Mercado (v2): Preço vs Reputação', fontsize=16)
plt.xlabel('Reputação (0-1) -> Mais Alta é Melhor', fontsize=12)
plt.ylabel('Preço por GB (R$)', fontsize=12)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
plt.savefig(os.path.join(output_dir, 'provider_landscape_v2.png'))
plt.close()

# 2) Buyer Perception (value_fn vs ref_point e storage)
if not df_analysis.empty:
    print("Gerando Gráfico v2-2: buyer_perception_v2.png")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    sns.regplot(data=df_analysis, x='ref_point', y='value_fn', ax=ax1,
                line_kws={"color":"red","lw":2}, scatter_kws={"alpha":0.7,"s":50})
    ax1.set_title('Valor Percebido vs Orçamento (v2)', fontsize=14)
    ax1.set_xlabel('Orçamento (ref_point)', fontsize=12)
    ax1.set_ylabel('Valor Percebido (value_fn)', fontsize=12)
    ax1.grid(True, linestyle='--', alpha=0.5)

    sns.regplot(data=df_analysis, x='storage', y='value_fn', ax=ax2,
                line_kws={"color":"blue","lw":2}, scatter_kws={"alpha":0.7,"s":50})
    ax2.set_title('Valor Percebido vs Armazenamento (v2)', fontsize=14)
    ax2.set_xlabel('Armazenamento (GB)', fontsize=12)
    ax2.set_ylabel('Valor Percebido (value_fn)', fontsize=12)
    ax2.grid(True, linestyle='--', alpha=0.5)

    plt.suptitle('Percepção de Valor do Comprador (v2)', fontsize=16, y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'buyer_perception_v2.png'))
    plt.close()

# 3) Distribuições de parâmetros (v2)
print("Gerando Gráfico v2-3: parameter_distributions_v2.png")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

sns.histplot(df_buyers['ref_point'], kde=True, ax=axes[0, 0], bins=15, color='blue')
axes[0, 0].set_title('Distribuição dos Orçamentos (ref_point) (v2)')
axes[0, 0].set_xlabel('ref_point (R$)')
axes[0, 0].set_ylabel('Número de Compradores')

sns.histplot(df_buyers['storage'], kde=True, ax=axes[0, 1], bins=15, color='green')
axes[0, 1].set_title('Distribuição do Armazenamento (storage) (v2)')
axes[0, 1].set_xlabel('Storage (GB)')
axes[0, 1].set_ylabel('Número de Compradores')

sns.histplot(df_providers['price'], kde=True, ax=axes[1, 0], bins=15, color='red')
axes[1, 0].set_title('Distribuição dos Preços dos Provedores (v2)')
axes[1, 0].set_xlabel('Preço por GB (R$)')
axes[1, 0].set_ylabel('Número de Provedores')

sns.histplot(df_providers['reputation'], kde=True, ax=axes[1, 1], bins=15, color='purple')
axes[1, 1].set_title('Distribuição da Reputação dos Provedores (v2)')
axes[1, 1].set_xlabel('Reputação (0-1)')
axes[1, 1].set_ylabel('Número de Provedores')

plt.suptitle('Distribuições de Parâmetros (v2 - Não Uniformes)', fontsize=16, y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'parameter_distributions_v2.png'))
plt.close()

# 4) Novos gráficos: Taxa de Aceitação e Matches por Provedor
if not df_decisions.empty:
    print("Gerando Gráfico v2-4: acceptance_stats_v2.png")
    # Aceitos por provedor
    accepted = df_decisions[df_decisions['accepted'] == True]
    counts = accepted['provider_id'].value_counts().sort_index()
    plt.figure(figsize=(10,6))
    sns.barplot(x=counts.index.astype(str), y=counts.values, palette="viridis")
    plt.title('Matches Aceitas por Provedor (v2)')
    plt.xlabel('Provider ID')
    plt.ylabel('Matches Aceitas')
    plt.grid(True, axis='y', linestyle='--', alpha=0.5)
    plt.savefig(os.path.join(output_dir, 'accepted_per_provider_v2.png'))
    plt.close()

    # Taxa de aceitação total
    total = len(df_decisions)
    acc_rate = counts.sum() / total if total > 0 else 0.0
    with open(os.path.join(output_dir, 'summary.txt'), 'w') as f:
        f.write(f"acceptance_rate: {acc_rate:.3f}\n")

print("\n--- Geração de Gráficos v2 Concluída ---")
