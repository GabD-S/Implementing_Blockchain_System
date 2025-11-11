# Simulação Multi-Agente (Versão Rust)

Tradução dos scripts Python para Rust visando maior performance, reprodutibilidade e segurança de tipos.

## Estrutura

```
parametros_aleatorios/rust/
  Cargo.toml
  src/
    lib.rs          # Módulos compartilhados
    model.rs        # Estruturas e lógica de simulação
    stats.rs        # Cálculo de métricas
    bin/
      advanced_multi_agent_simulator.rs  # Cenário único
      run_scenarios.rs                   # Múltiplos cenários
      performance_analysis.rs            # Análise sintética focada
```

## Dependências Principais
- rand / rand_distr – geração de valores aleatórios e distribuições (LogNormal, Poisson, Beta via construção Gamma)
- serde / serde_json – serialização dos resultados em JSON
- chrono – timestamps básicos
- plotters (planejado) – geração futura de gráficos diretamente em Rust

## Execução

Dentro de `parametros_aleatorios/rust`:

```bash
# Rodar cenário simples
cargo run --bin advanced_multi_agent_simulator

# Rodar todos os cenários principais
cargo run --bin run_scenarios

# Rodar análise sintética de performance
cargo run --bin performance_analysis
```

Saídas são gravadas em `parametros_aleatorios/resultados/` com sufixos `_rust`.

## Diferenças em Relação ao Python
| Aspecto | Python | Rust |
|---------|--------|------|
| Seed | Não fixo | Default 42 (configurável) |
| Beta | np.random.beta | Composição Gamma para Beta |
| Poisson | np.random.poisson | rand_distr::Poisson |
| Estrutura | Scripts soltos | Crate modular (lib + bins) |
| Performance | Interpretado | Compilado otimizado |

## Próximos Passos
- Adicionar geração de gráficos com `plotters`
- Introduzir camada de contratos inteligentes fictícia
- Persistir séries temporais para análises avançadas
- Calcular intervalos de confiança (bootstrap)

## License
Segue modelo do projeto original.
