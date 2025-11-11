import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# --- 1. Carregar e Preparar os Dados ---
print("Carregando comportamental_resultados.json...")
with open('comportamental_resultados.json', 'r') as f:
    data = json.load(f)

# Normalizar os dados em DataFrames
df_buyers = pd.DataFrame(data['buyers'])
df_providers = pd.DataFrame(data['providers'])
df_decisions = pd.DataFrame(data['decisions'])

# Juntar os dados para uma análise completa
df_analysis = pd.merge(df_decisions, df_buyers, left_on='buyer_id', right_on='id', suffixes=('_decision', '_buyer'))
df_analysis = pd.merge(df_analysis, df_providers, left_on='provider_id', right_on='id', suffixes=('_analysis', '_provider'))

print("Dados carregados e preparados.")

# Criar diretório para salvar gráficos
output_dir = "graficos_analise_comportamental"
os.makedirs(output_dir, exist_ok=True)
print(f"Diretório '{output_dir}' pronto.")

# --- 2. Bloco de Código 1: Gráfico 1 (Provider Landscape) ---
print("Gerando Gráfico 1: provider_landscape.png")
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_providers, x='reputation', y='price', s=100, alpha=0.7, label='Outros Provedores')

# Destacar o Provedor 1
provider_1 = df_providers[df_providers['id'] == 1]
plt.scatter(provider_1['reputation'], provider_1['price'],
            s=200, color='red', edgecolor='black', zorder=5,
            label='Provedor 1 (O Vencedor)')

# Adicionar rótulos de ID
for i, row in df_providers.iterrows():
    plt.text(row['reputation'] + 0.01, row['price'], f"ID: {row['id']}", fontsize=9)

plt.title('Cenário de Mercado: Preço vs. Reputação dos Provedores', fontsize=16)
plt.xlabel('Reputação (Reputation) -> Mais Alta é Melhor', fontsize=12)
plt.ylabel('Preço por GB (Price) -> Mais Baixo é Melhor', fontsize=12)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
plot_path1 = os.path.join(output_dir, 'provider_landscape.png')
plt.savefig(plot_path1)
plt.close()
print(f"Gráfico 1 salvo em: {plot_path1}")

# --- 3. Bloco de Código 2: Gráfico 2 (Buyer Perception) ---
print("Gerando Gráfico 2: buyer_perception.png")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Gráfico 2a: Valor vs. Orçamento (ref_point)
sns.regplot(data=df_analysis, x='ref_point', y='value_fn', ax=ax1,
            line_kws={"color":"red","lw":2},
            scatter_kws={"alpha":0.7,"s":50})
ax1.set_title('Valor Percebido vs. Orçamento do Comprador', fontsize=14)
ax1.set_xlabel('Orçamento (Ponto de Referência)', fontsize=12)
ax1.set_ylabel('Valor Percebido (value_fn)', fontsize=12)
ax1.grid(True, linestyle='--', alpha=0.5)

# Gráfico 2b: Valor vs. Armazenamento Solicitado
sns.regplot(data=df_analysis, x='storage', y='value_fn', ax=ax2,
            line_kws={"color":"blue","lw":2},
            scatter_kws={"alpha":0.7,"s":50})
ax2.set_title('Valor Percebido vs. Armazenamento Solicitado', fontsize=14)
ax2.set_xlabel('Armazenamento Solicitado (GB)', fontsize=12)
ax2.set_ylabel('Valor Percebido (value_fn)', fontsize=12)
ax2.grid(True, linestyle='--', alpha=0.5)

plt.suptitle('Análise da Percepção de Valor do Comprador (Todos escolheram o Provedor 1)', fontsize=16, y=1.02)
plt.tight_layout()
plot_path2 = os.path.join(output_dir, 'buyer_perception.png')
plt.savefig(plot_path2)
plt.close()
print(f"Gráfico 2 salvo em: {plot_path2}")

# --- 4. Bloco de Código 3: Gráfico 3 (Parameter Distributions) ---
print("Gerando Gráfico 3: parameter_distributions.png")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
sns.set_style("whitegrid")

# Histograma 3a: Orçamentos dos Compradores
sns.histplot(df_buyers['ref_point'], kde=True, ax=axes[0, 0], bins=15, color='blue')
axes[0, 0].set_title('Distribuição dos Orçamentos (ref_point)')
axes[0, 0].set_ylabel("Número de Compradores", fontsize=12)  # Atualizado de 'Count'

# Histograma 3b: Armazenamento dos Compradores
sns.histplot(df_buyers['storage'], kde=True, ax=axes[0, 1], bins=15, color='green')
axes[0, 1].set_title('Distribuição do Armazenamento (storage)')
axes[0, 1].set_ylabel("Número de Compradores", fontsize=12)  # Atualizado de 'Count'

# Histograma 3c: Preços dos Provedores
sns.histplot(df_providers['price'], kde=True, ax=axes[1, 0], bins=15, color='red')
axes[1, 0].set_title('Distribuição dos Preços dos Provedores')
axes[1, 0].set_ylabel("Número de Provedores", fontsize=12)  # Atualizado de 'Count'

# Histograma 3d: Reputação dos Provedores
sns.histplot(df_providers['reputation'], kde=True, ax=axes[1, 1], bins=15, color='purple')
axes[1, 1].set_title('Distribuição da Reputação dos Provedores')
axes[1, 1].set_ylabel("Número de Provedores", fontsize=12)  # Atualizado de 'Count'

plt.suptitle('Análise da Distribuição dos Parâmetros (Todos Uniformes)', fontsize=16, y=1.02)
plt.tight_layout()
plot_path3 = os.path.join(output_dir, 'parameter_distributions.png')
plt.savefig(plot_path3)
plt.close()
print(f"Gráfico 3 salvo em: {plot_path3}")

print("\n--- Geração de Gráficos Concluída ---")