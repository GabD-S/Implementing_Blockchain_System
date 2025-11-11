# Parâmetros Aleatórios – Organização e Escopo

Esta pasta agrupa os scripts e resultados da fase que utiliza **parâmetros aleatórios** para simular a negociação de armazenamento em nuvem por agentes (buyers, providers e network).

Estrutura:
- `simulacao/` – scripts de simulação e análises (cópias reorganizadas)
- `organizacao/` – script para organizar saídas geradas
- `resultados/` – saídas (.json, .png) geradas pelos scripts
- `docs/README.md` – documento detalhado sobre distribuições, limitações e sugestões

Como executar (exemplos):

```bash
# Simulação principal (gera JSON e gráficos na pasta resultados/)
python3 parametros_aleatorios/simulacao/advanced_multi_agent_simulator.py

# Análise de performance e escalabilidade
python3 parametros_aleatorios/simulacao/performance_analysis.py

# Análise simples
python3 parametros_aleatorios/simulacao/analyze_results.py

# Organizar artefatos em subpastas
python3 parametros_aleatorios/organizacao/organize_results.py
```

Para explicações detalhadas sobre os **parâmetros aleatórios** usados e as **limitações** do método, consulte `docs/README.md`.
