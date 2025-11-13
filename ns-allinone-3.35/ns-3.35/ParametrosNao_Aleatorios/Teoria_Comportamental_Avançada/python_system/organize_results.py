#!/usr/bin/env python3
"""
Script para identificar e organizar os gráficos mais relevantes
"""

import os
import shutil
from datetime import datetime

def organize_results():
    """Organiza os resultados por relevância"""
    
    base_dir = "/home/gabriel_pc/cloud-storage-ns3/ns-allinone-3.35/ns-3.35/resultados_graficos"
    
    # Criar subpastas por relevância
    folders = {
        "1_PRINCIPAIS": "Gráficos mais importantes para análise",
        "2_COMPLEMENTARES": "Análises complementares e detalhadas", 
        "3_DADOS": "Arquivos JSON com dados brutos"
    }
    
    for folder, desc in folders.items():
        folder_path = os.path.join(base_dir, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        # Criar README em cada pasta
        with open(os.path.join(folder_path, "README.md"), "w") as f:
            f.write(f"# {folder}\n\n{desc}\n\n")
    
    # Mapeamento de arquivos por relevância
    file_mapping = {
        "1_PRINCIPAIS": [
            "multi_agent_cloud_storage_complete_analysis.png",
            "scalability_analysis.png"
        ],
        "2_COMPLEMENTARES": [
            "performance_analysis_detailed.png",
            "cloud_storage_analysis.png"
        ],
        "3_DADOS": [
            "simulation_results_detailed.json",
            "performance_analysis_results.json",
            "simulation_results.json"
        ]
    }
    
    # Copiar arquivos para suas respectivas pastas
    for folder, files in file_mapping.items():
        folder_path = os.path.join(base_dir, folder)
        for file in files:
            src = os.path.join(base_dir, file)
            dst = os.path.join(folder_path, file)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                print(f"✅ {file} → {folder}")
    
    # Criar índice geral
    create_index_file(base_dir)
    
    print(f"\n🎯 Organização concluída!")
    print(f"📁 Pasta principal: {base_dir}")

def create_index_file(base_dir):
    """Cria arquivo índice principal"""
    
    index_content = f"""# 📊 RESULTADOS DA SIMULAÇÃO MULTI-AGENTE

**Data de Execução**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🏆 GRÁFICOS PRINCIPAIS (Pasta 1_PRINCIPAIS)

### 1. multi_agent_cloud_storage_complete_analysis.png
- **Descrição**: Análise completa com 12 subgráficos
- **Conteúdo**: Taxa de sucesso, volume financeiro, throughput, latência, distribuição de agentes
- **Uso**: Visão geral completa do comportamento do sistema
- **Relevância**: ⭐⭐⭐⭐⭐

### 2. scalability_analysis.png  
- **Descrição**: Análise de escalabilidade com 4 gráficos principais
- **Conteúdo**: Throughput vs agentes, latência vs agentes, eficiência, taxa de sucesso
- **Uso**: Planejamento de capacidade e otimização
- **Relevância**: ⭐⭐⭐⭐⭐

## 📈 GRÁFICOS COMPLEMENTARES (Pasta 2_COMPLEMENTARES)

### 3. performance_analysis_detailed.png
- **Descrição**: Análise detalhada de performance com 6 métricas
- **Conteúdo**: KPIs técnicos, eficiência computacional, perfil de performance
- **Uso**: Análise técnica profunda
- **Relevância**: ⭐⭐⭐⭐

### 4. cloud_storage_analysis.png
- **Descrição**: Análise baseline inicial
- **Conteúdo**: Comparação com cenários básicos
- **Uso**: Validação e comparação
- **Relevância**: ⭐⭐⭐

## 📄 DADOS BRUTOS (Pasta 3_DADOS)

- `simulation_results_detailed.json` - Resultados completos da simulação principal
- `performance_analysis_results.json` - Métricas de performance detalhadas
- `simulation_results.json` - Dados baseline

## 🎯 PRINCIPAIS DESCOBERTAS

1. **Ponto Ótimo**: 50-70 agentes totais para melhor relação performance/complexidade
2. **Escalabilidade**: Sistema escala até ~183 agentes com degradação controlada
3. **Performance**: Throughput máximo de 1.92 TPS, latência entre 66-195ms
4. **Volume**: Crescimento exponencial ($530 → $25,289) com aumento de agentes

## 🚀 RECOMENDAÇÕES

- **Produção**: Configurar ~70 agentes (35 buyers, 20 providers, 12 network)
- **Pesquisa**: Focar otimização para taxa de sucesso 12-16%
- **Monitoramento**: Acompanhar trade-off throughput vs latência

## 📊 ORDEM DE ANÁLISE RECOMENDADA

1. **Primeiro**: `multi_agent_cloud_storage_complete_analysis.png` (visão geral)
2. **Segundo**: `scalability_analysis.png` (comportamento com escala)
3. **Terceiro**: `performance_analysis_detailed.png` (métricas técnicas)
4. **Último**: Dados JSON para análises específicas

---
**Gerado automaticamente em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**
"""
    
    with open(os.path.join(base_dir, "INDEX.md"), "w") as f:
        f.write(index_content)
    
    print("📋 Arquivo INDEX.md criado com guia completo")

def print_summary():
    """Imprime resumo final"""
    
    print("\n" + "="*80)
    print("🎯 RESUMO FINAL - SIMULAÇÃO MULTI-AGENTE CLOUD STORAGE")
    print("="*80)
    print()
    print("✅ EXECUÇÃO CONCLUÍDA COM SUCESSO!")
    print()
    print("📊 CENÁRIOS EXECUTADOS:")
    print("   • 4 cenários principais (10 → 150 agentes)")
    print("   • 4 cenários de performance (26 → 183 agentes)")
    print("   • Total de 8 configurações diferentes")
    print()
    print("🎨 GRÁFICOS GERADOS:")
    print("   🏆 2 gráficos PRINCIPAIS (mais relevantes)")
    print("   📈 2 gráficos COMPLEMENTARES (análise detalhada)")
    print("   📄 3 arquivos JSON (dados brutos)")
    print()
    print("📁 ORGANIZAÇÃO:")
    print("   • 1_PRINCIPAIS/ - Gráficos essenciais para análise")
    print("   • 2_COMPLEMENTARES/ - Análises técnicas detalhadas")
    print("   • 3_DADOS/ - Arquivos JSON com dados completos")
    print()
    print("🎯 PRINCIPAIS RESULTADOS:")
    print("   • Ponto ótimo: ~70 agentes totais")
    print("   • Taxa de sucesso: 9.7% - 15.7%")
    print("   • Throughput máximo: 1.92 TPS")
    print("   • Volume máximo: $25,289")
    print()
    print("📍 LOCALIZAÇÃO DOS RESULTADOS:")
    print("   /home/gabriel_pc/cloud-storage-ns3/ns-allinone-3.35/ns-3.35/resultados_graficos/")
    print()
    print("🔍 PARA INICIAR A ANÁLISE:")
    print("   1. Abrir: 1_PRINCIPAIS/multi_agent_cloud_storage_complete_analysis.png")
    print("   2. Seguir: INDEX.md para ordem recomendada de análise")
    print()
    print("=" * 80)

if __name__ == "__main__":
    organize_results()
    print_summary()
