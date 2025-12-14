# 🚀 Como Rodar o Projeto

Siga os passos abaixo para executar o sistema completo:

1. **Instale o Magic Wormhole:**
    ```bash
    pip install magic-wormhole --break-system-packages
    ```
    > Isso é necessário para a transferência segura de arquivos P2P.

2. **Inicie o nó IPFS (Kubo):**
    ```bash
    ipfs daemon
    ```
    > Certifique-se de que o IPFS está instalado e inicializado (`ipfs init`).

2. **Inicie o backend Rust (provider_daemon):**
    ```bash
    cd provider_daemon
    ./target/release/provider_daemon
    ```

3. **Inicie o frontend (storage-dapp):**
    ```bash
    cd storage-dapp
    npm install # (apenas na primeira vez)
    npm run dev
    ```
    > Acesse `http://localhost:5173` no navegador.

---
# Plano de Produção: Sistema de Armazenamento Descentralizado (MVP)

Este documento descreve o roteiro de execução para o desenvolvimento de um Mínimo Produto Viável (MVP) de um sistema de armazenamento descentralizado.

**Objetivo:** Criar um sistema funcional onde arquivos são armazenados via IPFS, negociados via Smart Contracts em Rust, e acessados por uma interface Web, com uma etapa adicional de validação de rede via simulador NS-3.

---

## 🏗️ Arquitetura do Sistema

O sistema opera em três camadas distintas, eliminando a necessidade de servidores centrais para lógica de negócios.

1.  **Camada de Dados (IPFS):** Responsável pelo endereçamento e transporte de arquivos.
2.  **Camada de Confiança (Blockchain/Substrate):** Responsável pelo registro de provedores, acordos de serviço (SLA) e custódia de pagamento (Escrow).
3.  **Camada de Aplicação (Agentes):**
    * **Provedor (Backend Rust):** Daemon autônomo que escuta a blockchain e fixa (pin) arquivos.
    * **Comprador (Frontend React):** Interface para upload e contratação de serviço.

---

## FASE 1: Infraestrutura Base (O "Chão de Fábrica")

Antes de desenvolver, é necessário estabelecer a rede local.

- [x] **1.1 Configurar Nó IPFS (Kubo)**
    - Instalar `kubo` (Go-IPFS).
    - Inicializar: `ipfs init`.
    - Rodar Daemon: `ipfs daemon --enable-pubsub-experiment` (permite comunicação em tempo real).
    - *Objetivo:* Ter um nó local capaz de gerar CIDs e trocar arquivos.

- [x] **1.2 Configurar Blockchain Local (Substrate)**
    - Instalar `cargo-contract` e ferramentas do Rust.
    - Instalar `substrate-contracts-node`.
    - Rodar Nó: `substrate-contracts-node --dev`.
    - *Objetivo:* Ter uma blockchain funcional para deploy dos contratos `ink!`.

---

## FASE 2: A "Rede Independente" (Smart Contract em Rust)

Desenvolvimento da lógica de negócios centralizada no código, mas descentralizada na execução.

- [x] **2.1 Criação do Projeto**
        - Projeto criado em `Sistema_Implementado/storage_market` com `Cargo.toml` e `lib.rs` (ink!).
        - Para compilar e gerar `.contract`:
            ```bash
            cd Sistema_Implementado/storage_market
            cargo +nightly contract build
            ```

- [x] **2.2 Estrutura de Dados (`lib.rs`)**
    - Definir `StorageDeal`:
      ```rust
      struct StorageDeal {
          buyer: AccountId,
          provider: AccountId,
          file_cid: String, // O Hash do IPFS
          size: u64,
          duration: u64,
          value: Balance,
      }
      ```
    - Definir Mappings: `providers: Mapping<AccountId, ProviderProfile>` e `deals: Mapping<u32, StorageDeal>`.

- [x] **2.3 Implementação de Funções (Mensagens)**
    - `register_provider(capacity, price_per_gb)`: Registra um nó provedor.
    - `create_deal(provider_id, file_cid)`: Função `payable`. Recebe tokens e cria o acordo on-chain.
    - `withdraw_payment(deal_id)`: Permite ao provedor sacar após o período (simplificado).

- [x] **2.4 Deploy**
    - Compilar: `cargo contract build`.
    - Deploy: Usar [Contracts UI](https://contracts-ui.substrate.io/) conectado ao nó local.

---

## FASE 3: O Agente "Provedor" (Backend em Rust)

Um serviço autônomo de alta performance que substitui a intervenção humana.

- [x] **3.1 Setup do Projeto Rust**
        - Projeto criado em `Sistema_Implementado/provider_daemon`.
        - Build:
            ```bash
            cd Sistema_Implementado/provider_daemon
            cargo build --release
            ```

- [x] **3.2 Lógica de Conexão**
    - Conectar ao WebSocket do Substrate (`127.0.0.1:9944`).
    - Conectar à API HTTP do IPFS (`127.0.0.1:5001`).

- [x] **3.3 Loop de Eventos (O Coração do Agente)**
    - Inscrever-se (Subscribe) nos eventos do contrato `storage_market`.
    - Filtrar eventos do tipo `DealCreated` onde `provider_id == meu_id`.

- [x] **3.4 Execução de Serviço**
    - Ao receber evento: Extrair `file_cid`.
    - Executar comando IPFS: `api.pin_add(file_cid)`.
    - *Resultado:* O arquivo é baixado do nó do comprador e fixado no disco do provedor.
        - Rodar MVP (mock de eventos + pin IPFS):
            ```bash
            ./target/release/provider_daemon
            ```

---

## FASE 4: O Agente "Comprador" (Frontend React/TS)

Interface amigável para interação humana, utilizando bibliotecas maduras de Web3.

- [x] **4.1 Setup do Projeto**
        - Projeto criado em `Sistema_Implementado/storage-dapp` (Vite + React/TS minimal).
        - Instalar deps e rodar:
            ```bash
            cd Sistema_Implementado/storage-dapp
            npm install
            npm run dev
            ```

- [x] **4.2 Componente de Upload (IPFS)**
    - Input de arquivo simples.
    - Ao selecionar: Enviar para nó IPFS local do navegador/usuário.
    - Retorno: Exibir o **CID** gerado (ex: `QmX...`).

- [x] **4.3 Componente de Contratação (Blockchain)**
    - Listar provedores registrados (lendo do Smart Contract).
    - Botão "Contratar":
        - Conectar à carteira (Polkadot.js Extension).
        - Assinar transação `create_deal` enviando o CID e o valor em tokens.

---

## FASE 5: Validação e Testes de Integração (Script Próprio)

Substituição da simulação NS-3 por testes de integração locais para validar o fluxo de dados e latência real do sistema.

- [x] **5.1 Script de Validação (`validate_system.py`)**
    - Script Python para orquestrar o teste.
    - Verifica status do IPFS e Daemon.
    - Gera arquivos de teste de diferentes tamanhos.

- [x] **5.2 Teste de Upload e Pinning**
    - Medir tempo de upload para o nó IPFS local.
    - Simular propagação: Forçar `ipfs pin add` e medir tempo de resposta.
    - Validar integridade do CID.

- [x] **5.3 Relatório de Performance**
    - Gerar logs de latência e sucesso das operações.
    - Validar se o `provider_daemon` está respondendo corretamente.

---

## TRILHA PARALELA: Pesquisa Comportamental (Python)

Enquanto o sistema Rust é construído para demonstração técnica, a simulação Python continua para fins acadêmicos e modelagem de larga escala.

- [ ] **6.1 Agentes Comportamentais**
    - Implementar Teoria da Perspectiva (Aversão à Perda) nos Compradores.
    - Implementar Teoria dos Jogos (Equilíbrio de Nash) nos Provedores.

- [ ] **6.2 Simulação de Massa**
    - Executar cenários com 100+ agentes para gerar dados estatísticos de formação de preço e reputação.