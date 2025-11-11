#!/usr/bin/env python3
"""
Cópia reorganizada: organiza resultados dentro de parametros_aleatorios/resultados
"""
import os
import shutil
from datetime import datetime

BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resultados')
os.makedirs(BASE_DIR, exist_ok=True)

def organize_results():
    folders = {
        "1_PRINCIPAIS": "Gráficos mais importantes para análise",
        "2_COMPLEMENTARES": "Análises complementares e detalhadas",
        "3_DADOS": "Arquivos JSON com dados brutos"
    }
    for folder, desc in folders.items():
        folder_path = os.path.join(BASE_DIR, folder)
        os.makedirs(folder_path, exist_ok=True)
        with open(os.path.join(folder_path, "README.md"), "w") as f:
            f.write(f"# {folder}\n\n{desc}\n\n")

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

    for folder, files in file_mapping.items():
        folder_path = os.path.join(BASE_DIR, folder)
        for file in files:
            src = os.path.join(BASE_DIR, file)
            dst = os.path.join(folder_path, file)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                print(f"✅ {file} → {folder}")

    create_index_file(BASE_DIR)
    print(f"\n🎯 Organização concluída!\n📁 Pasta principal: {BASE_DIR}")


def create_index_file(base_dir):
    index_content = f"""# 📊 RESULTADOS DA SIMULAÇÃO MULTI-AGENTE

**Data de Execução**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🏆 GRÁFICOS PRINCIPAIS (Pasta 1_PRINCIPAIS)

- multi_agent_cloud_storage_complete_analysis.png
- scalability_analysis.png

## 📈 GRÁFICOS COMPLEMENTARES (Pasta 2_COMPLEMENTARES)

- performance_analysis_detailed.png
- cloud_storage_analysis.png

## 📄 DADOS BRUTOS (Pasta 3_DADOS)

- simulation_results_detailed.json
- performance_analysis_results.json
- simulation_results.json

---
**Gerado automaticamente em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**
"""
    with open(os.path.join(base_dir, "INDEX.md"), "w") as f:
        f.write(index_content)
    print("📋 Arquivo INDEX.md criado com guia completo")


if __name__ == "__main__":
    organize_results()
