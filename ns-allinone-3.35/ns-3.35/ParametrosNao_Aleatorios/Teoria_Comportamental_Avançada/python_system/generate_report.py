#!/usr/bin/env python3
"""Generate a metrics report mapping produced artifacts to Metricas.md criteria."""
import os, json, glob

RESULTS_DIR = os.path.join(os.getcwd(), 'resultados')

def main():
    aggregated = os.path.join(RESULTS_DIR, 'aggregated_results.json')
    data = {}
    if os.path.exists(aggregated):
        with open(aggregated) as f:
            data = json.load(f)

    lines = []
    lines.append('# Relatório de Métricas (conforme Metricas.md)')
    lines.append('')
    lines.append('## Performance e Capacidade')
    lines.append('- TPS: ver `tps_vs_nodes.png` e JSON `aggregated_results.json`.')
    lines.append('- Latência de confirmação: ver `latency_cdf.png` e `latency_vs_txrate.png`.')
    lines.append('- Tempo de propagação: derivado de `ns3.delay` por cenário, grafo `forks_vs_propagation.png`.')
    lines.append('')
    lines.append('## Escalabilidade e Carga')
    lines.append('- TPS vs nº de nós: `tps_vs_nodes.png`.')
    lines.append('- Variação de carga (tx/s) vs latência: `latency_vs_txrate.png`.')
    lines.append('')
    lines.append('## Consistência e Segurança (heurístico)')
    lines.append('- Taxa de forks (heurística): `forks_vs_propagation.png`.')
    lines.append('- Reorgs não simulados no nível de protocolo — requer integração runtime. (Limitação)')
    lines.append('')
    lines.append('## Uso de Recursos (estimado)')
    lines.append('- Banda vs throughput: `bandwidth_vs_throughput.png`.')
    lines.append('- CPU vs carga: `cpu_vs_load.png`.')
    lines.append('- Memória por nó: disponível em `aggregated_results.json` (chave resources).')
    lines.append('')
    lines.append('## Qualidade de Serviço')
    lines.append('- Disponibilidade vs tempo (nós confiáveis 0.99): `availability_vs_time.png`.')
    lines.append('')
    lines.append('## Descentralização')
    lines.append('- Distribuição de capacidade (providers) não plotada aqui; pode-se estender com histograma a partir de `matching`.')
    lines.append('')
    lines.append('## Gráficos adicionais')
    lines.append('- Heatmap (tamanho do bloco x intervalo): `heatmap_blocksize_interval.png`.')
    lines.append('- Escalabilidade do negócio (usuários): `scalability_users.png`.')
    lines.append('')
    lines.append('## Artefatos gerados')
    for img in sorted(glob.glob(os.path.join(RESULTS_DIR, '*.png'))):
        lines.append(f'- {os.path.basename(img)}')

    with open(os.path.join(RESULTS_DIR, 'RELATORIO_METRICAS.md'), 'w') as f:
        f.write('\n'.join(lines))
    print('RELATORIO_METRICAS.md gerado em', RESULTS_DIR)

if __name__ == '__main__':
    main()
