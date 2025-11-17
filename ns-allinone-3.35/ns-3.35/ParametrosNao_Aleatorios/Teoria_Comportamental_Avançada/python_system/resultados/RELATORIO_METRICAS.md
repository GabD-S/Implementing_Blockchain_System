# Relatório de Métricas (conforme Metricas.md)

## Performance e Capacidade
- TPS: ver `tps_vs_nodes.png` e JSON `aggregated_results.json`.
- Latência de confirmação: ver `latency_cdf.png` e `latency_vs_txrate.png`.
- Tempo de propagação: derivado de `ns3.delay` por cenário, grafo `forks_vs_propagation.png`.

## Escalabilidade e Carga
- TPS vs nº de nós: `tps_vs_nodes.png`.
- Variação de carga (tx/s) vs latência: `latency_vs_txrate.png`.

## Consistência e Segurança (heurístico)
- Taxa de forks (heurística): `forks_vs_propagation.png`.
- Reorgs não simulados no nível de protocolo — requer integração runtime. (Limitação)

## Uso de Recursos (estimado)
- Banda vs throughput: `bandwidth_vs_throughput.png`.
- CPU vs carga: `cpu_vs_load.png`.
- Memória por nó: disponível em `aggregated_results.json` (chave resources).

## Qualidade de Serviço
- Disponibilidade vs tempo (nós confiáveis 0.99): `availability_vs_time.png`.

## Descentralização
- Distribuição de capacidade (providers) não plotada aqui; pode-se estender com histograma a partir de `matching`.

## Gráficos adicionais
- Heatmap (tamanho do bloco x intervalo): `heatmap_blocksize_interval.png`.
- Escalabilidade do negócio (usuários): `scalability_users.png`.

## Artefatos gerados
- availability_vs_time.png
- bandwidth_vs_throughput.png
- cpu_vs_load.png
- forks_vs_propagation.png
- heatmap_blocksize_interval.png
- latency_cdf.png
- latency_vs_txrate.png
- scalability_users.png
- throughput_timeseries.png
- tps_vs_nodes.png