# Parâmetros Aleatórios na Simulação Multi-Agente de Armazenamento em Nuvem

Esta pasta concentra os scripts e resultados que usam **geração estocástica** (parâmetros aleatórios) para criar cenários de negociação entre agentes (buyers, providers e network). O objetivo é prototipar e validar a viabilidade do sistema sem ainda recorrer a dados empíricos.

## Scripts

- `simulacao/advanced_multi_agent_simulator.py` – Simulação principal multi‑cenários (compra, reputação, capacidade).
- `simulacao/performance_analysis.py` – Execuções focadas para métricas de performance/escalabilidade.
- `simulacao/analyze_results.py` – Análise simples (baseline) e gráfico compacto.
- `organizacao/organize_results.py` – Classifica e indexa artefatos gerados.

## Distribuições Utilizadas

| Parâmetro | Distribuição | Justificativa | Observação |
|-----------|--------------|---------------|------------|
| Budget (buyers) | Lognormal(μ=7.5, σ=0.5) | Representar cauda longa de orçamento | Pode gerar valores muito altos; sem limite máximo explícito |
| Storage needed (GB) | Uniforme discreta [5, 200] | Variedade simples de demandas | Sem correlação com budget |
| Max price (buyer) | Uniforme contínua [0.05, 0.30] | Diferentes sensibilidades a preço | Não calibrado em mercado real |
| Reputation threshold | Uniforme contínua [0.3, 0.8] | Diferentes níveis mínimos aceitos | Independente de necessidade ou budget |
| Capacity (provider) | Uniforme discreta [100, 5000] | Variedade de porte | Sem correlação com preço/reputação |
| Price per GB (provider) | Uniforme contínua [0.08, 0.25] | Faixa simplificada | Falta relação com custo operacional |
| Reputation inicial (provider) | Beta(α=2, β=1) | Viés a reputações mais altas | Pode superestimar qualidade média |
| Commission (network) | Uniforme contínua [0.01, 0.10] | Diferentes políticas | Não há dinâmica adaptativa |
| Tentativas por tick | Poisson(λ=transaction_rate) | Chegadas estocásticas | λ fixo por cenário |

## Mecanismos Derivados

- **Reputação**: Incremento fixo (+0.005) em sucesso; penalização (-0.01) em algumas falhas. Simplificado, não considera histórico profundo ou feedback de múltiplas dimensões.
- **Capacidade**: Reduzida integralmente na compra; não há liberação ao fim de “contrato” (modelo de contrato permanente).
- **Preço efetivo**: Não há renegociação; provider não ajusta preço conforme ocupação.
- **Network agent**: Apenas aplica comissão e não modela latência real simbólica integrada ao custo ou probabilidade de falha de broadcast.

## Limitações Atuais

1. **Reprodutibilidade reduzida**: Ausência de `seed` central. Mistura `numpy.random` e `random` do Python.
2. **Ausência de correlação**: Budget, capacidade, preço e reputação independentes → mercado pouco realista.
3. **Incrementos lineares de reputação**: Não saturam por contexto (apenas clamp em 1.0).
4. **Sem dinâmica temporal**: Parâmetros dos agentes são estáticos (não entram/saem do mercado, não reajustam preços).
5. **Modelo de falha simplificado**: Razões definidas, mas sem probabilidade externa (ex: falha de rede, latência variável afetando sucesso).
6. **Distribuições não calibradas**: Valores arbitrários; falta validação empírica ou comparação com benchmarks de provedores reais.
7. **Escalabilidade artificial**: Cenários escalam apenas contagens e `transaction_rate`; não há congestionamento ou custo computacional simulado.

## Impactos das Limitações

- Resultados servem para explorar forma e ordem de grandeza, não para previsão precisa.
- Métricas como taxa de sucesso podem estar infladas ou deprimidas conforme combinações aleatórias extremas.
- Ausência de correlação pode mascarar efeitos econômicos emergentes (ex: seleção adversa, competição de preço).

## Recomendações de Evolução

| Objetivo | Ação | Benefício |
|----------|------|-----------|
| Reprodutibilidade | Introduzir `seed` configurável | Permite comparar execuções e publicar resultados estáveis |
| Realismo Econômico | Correlacionar preço ↔ capacidade ↔ reputação | Mercado mais plausível |
| Dinâmica | Ajustar preços conforme ocupação e demanda | Feedback adaptativo |
| Contratos | Adicionar duração e liberação de capacidade | Rotatividade de recursos |
| Reputação | Basear em múltiplas métricas (atrasos, falhas) | Indicador mais informativo |
| Latência | Modelar distribuição e impacto no sucesso | Aumenta validade de resultados |
| Falhas | Incluir falhas estocásticas de rede/custo adicional | Robustez avaliada |
| Análise | Calcular intervalos de confiança (bootstrap) | Robustez estatística |

## Seed Sugerida (Exemplo de Patch Futuro)

```python
import random, numpy as np
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
```

## Estrutura dos Dados Gerados

Os arquivos JSON em `resultados/` agregam:
- `simulation_results_detailed.json`: Estatísticas por cenário (volume, sucesso, reputação média).
- `performance_analysis_results.json`: Métricas focadas de throughput, latência, eficiência.
- `simulation_results.json`: Baseline compacto.

## Aviso de Uso

Este conjunto de scripts é uma **fase exploratória**. Não utilize para tomada de decisão de negócios sem calibração posterior. Próximos passos devem incluir validação com dados históricos ou parâmetros sintéticos mais justificáveis.

---
_Gerado automaticamente. Atualize conforme evolução do modelo._
