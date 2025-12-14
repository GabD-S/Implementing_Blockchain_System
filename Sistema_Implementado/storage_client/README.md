# Storage Client (Rust)

Este é um cliente Rust standalone para interagir com o contrato inteligente `storage_market`.

## Pré-requisitos

1. **Nó Substrate Local**: Certifique-se de que seu nó `substrate-contracts-node` está rodando em `ws://127.0.0.1:9944`.
2. **Contrato Implantado**: O contrato `storage_market` deve estar implantado na rede.

## Configuração

Antes de rodar, você precisa atualizar o endereço do contrato no arquivo `src/main.rs`.

1. Abra `src/main.rs`.
2. Localize a linha:
   ```rust
   let contract_addr_str = "5F7B9x..."; 
   ```
3. Substitua `"5F7B9x..."` pelo endereço real do seu contrato (AccountId) que foi gerado durante o deploy (ex: via `cargo contract instantiate` ou UI).

## Como Rodar

Execute o seguinte comando na pasta `storage_client`:

```bash
cargo run
```

## O que ele faz?

1. Conecta ao nó local.
2. Usa a conta `Alice` (dev) para assinar transações.
3. Chama a função `register_provider` do contrato.
4. Chama a função `create_deal` do contrato.
