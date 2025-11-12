# Plano de Ação: Projeto de Armazenamento Descentralizado (Duas Trilhas)

Este documento divide o projeto em duas trilhas paralelas:

1.  **Trilha Rust (MVP Funcional e Teste de Rede):** Focada em criar um sistema de ponta-a-ponta funcional para uma apresentação de engenharia, demonstrando a viabilidade da linguagem Rust e testando a resiliência da rede com NS-3.
2.  **Trilha Python (Simulação Comportamental e IA):** Focada na pesquisa acadêmica, modelando o comportamento de milhares de agentes, aplicando teorias econômicas (Teoria da Perspectiva) e desenvolvendo a base para agentes de IA.

---

## TRILHA 1: RUST (Demonstração de Viabilidade e Teste de Rede)

**Objetivo:** Um MVP 100% em Rust (Cliente, Nó, Contrato) que interage com IPFS e é testado em um simulador de rede (NS-3).

### Fase 1: 💾 O Armazenamento Básico (Cliente-IPFS em Rust)

**Meta:** Provar que o Rust pode interagir com a camada de armazenamento IPFS.

- [ ] **Ação 1.1:** Configurar o IPFS (Kubo).
    - [ ] Instalar o `kubo`.
    - [ ] Executar `ipfs init`.
    - [ ] Executar `ipfs daemon`.

- [ ] **Ação 1.2:** Criar o Projeto Rust (`rust_ipfs_client`).
    - [ ] Adicionar a crate `ipfs-api` ao `Cargo.toml`.

- [ ] **Ação 1.3:** Script `add_file.rs` (adiciona um arquivo e imprime o CID).

- [ ] **Ação 1.4:** Script `get_file.rs` (lê um CID e baixa o arquivo).

### Fase 2: ⛓️ O Smart Contract (A Lógica de Negócios em Rust/ink!)

**Meta:** Criar as "regras do jogo" em uma blockchain (Wasm).

- [ ] **Ação 2.1:** Configurar o Ambiente `ink!`.
    - [ ] Instalar `cargo-contract`.
    - [ ] Instalar um nó de desenvolvimento (ex: `substrate-contracts-node`).

- [ ] **Ação 2.2:** Modelar os Contratos (`storage_market`).
    - [ ] Definir `structs`: `ProviderProfile`, `StorageDeal` (com `file_cid: String`).
    - [ ] Definir `Mappings` de armazenamento para `providers` e `deals`.

- [ ] **Ação 2.3:** Implementar as Funções (Mensagens) do Contrato.
    - [ ] `fn register_provider(...)`
    - [ ] `fn request_storage(..., file_cid: String, ...)` (tipo `payable`)
    - [ ] `fn complete_storage(...)` (para liberar o *escrow*).

### Fase 3: 🤖 O Nó Provedor (O Agente de Serviço Rust)

**Meta:** Criar o daemon que o **Provedor** executa.

- [ ] **Ação 3.1:** Criar o Daemon `provider_node` (usando **Tokio**).
    - [ ] Adicionar `ipfs-api` (Fase 1).
    - [ ] Adicionar `subxt` (para falar com a blockchain Substrate/ink!).

- [ ] **Ação 3.2:** Loop do Agente (Ouvir a Blockchain).
    - [ ] Conectar ao WebSocket do nó da blockchain.
    - [ ] Assinar (subscribe) os **eventos** do smart contract `storage_market`.

- [ ] **Ação 3.3:** Lógica de Ação (Conectar ao IPFS).
    - [ ] Ao detectar um evento `DealCreated`:
    - [ ] Extrair o `file_cid`.
    - [ ] Chamar `api.pin_add(file_cid, recursive=true)` (Fase 1).

### Fase 4: 🖥️ O Cliente Comprador (A CLI em Rust)

**Meta:** A CLI que o **Comprador** usa.

- [ ] **Ação 4.1:** Criar o Projeto `buyer_cli` (usando **clap**).

- [ ] **Ação 4.2:** Implementar o Fluxo de Upload (`upload <file>`).
    - [ ] **(Local)** `ipfs-api.add()` para obter o `file_cid`.
    - [ ] **(Rede)** `subxt.call(request_storage, file_cid, ...)` com o pagamento.

- [ ] **Ação 4.3:** Implementar o Fluxo de Download (`download <cid>`).
    - [ ] **(Local)** `ipfs-api.cat(cid)`.

### Fase 5: 🔬 Simulação de Rede (Integração NS-3)

**Meta:** Testar a robustez do sistema (Fases 1-4) contra condições de rede realistas.

- [ ] **Ação 5.1:** Compilar os Binários Rust.
    - [ ] Compilar `provider_node` (Fase 3) e `buyer_cli` (Fase 4) em modo `release`.

- [ ] **Ação 5.2:** Configurar o Ambiente NS-3 (C++).
    - [ ] Instalar o NS-3.
    - [ ] Criar um script de simulação C++.

- [ ] **Ação 5.3:** Definir a Topologia no NS-3.
    - [ ] Criar uma topologia de rede (ex: Ponto-a-Ponto, Estrela) com vários nós.
    - [ ] Adicionar modelos de latência (ex: 50ms) e perda de pacotes (ex: 0.1%) aos canais.
    - [ ] Configurar o **TapBridge** do NS-3 para criar dispositivos de rede virtuais (TUN/TAP) no Linux para cada nó simulado.

- [ ] **Ação 5.4:** Executar a Simulação.
    - [ ] Iniciar a simulação NS-3 (que ativa as interfaces TAP).
    - [ ] "Amarrar" (bind) os executáveis Rust a essas interfaces de rede virtuais.
    - [ ] Executar o `buyer_cli upload ...` em um nó TAP.
    - [ ] Observar o `provider_node` (em outro nó TAP) receber o evento e fixar o CID.

- [ ] **Ação 5.5:** Coletar Métricas.
    - [ ] Usar os logs do NS-3 (`.pcap`, logs de throughput) para medir:
        - O tempo total do "upload" (da CLI até o "pin" do provedor).
        - O impacto da perda de pacotes na comunicação com o smart contract.
        - O throughput real da transferência IPFS na rede simulada.

---

## TRILHA 2: PYTHON (Simulação Comportamental e IA)

**Objetivo:** Usar Python para modelagem em larga escala, economia comportamental e desenvolvimento de IA (conforme `SMA_Artigo_Final.pdf` e `comportamental_resultados.json`).

### Fase 6: 🐍 Simulação Base (Python/Asyncio)

**Meta:** Replicar e validar a simulação de base do seu artigo.

- [ ] [cite_start]**Ação 6.1:** Implementar os Agentes de Regras Simples[cite: 886, 892].
    - [ ] Agente `Comprador` (Python `asyncio`).
    - [ ] Agente `Provedor` (Python `asyncio`).
    - [ ] Agente `Broker` (Python `asyncio`).

- [ ] **Ação 6.2:** Implementar o `MessageBus` (Fila de Mensagens).
    - [ ] [cite_start]Adicionar simulação de latência de rede[cite: 885, 920].

- [ ] [cite_start]**Ação 6.3:** Replicar Cenários de Escalabilidade[cite: 1004].
    - [ ] Executar simulações (Pequena, Média, Grande, Massiva).
    - [ ] [cite_start]Validar as métricas: Throughput (TPS), Taxa de Sucesso, Latência[cite: 1031].

### Fase 7: 🧠 Modelagem Comportamental (Economia)

**Meta:** Substituir os agentes de regras simples por agentes economicamente realistas.

- [ ] **Ação 7.1:** Implementar Inicialização Estocástica.
    - [ ] Substituir `random.uniform()` por distribuições realistas (Log-Normal, Beta).

- [ ] **Ação 7.2:** Implementar a Teoria da Perspectiva (Kahneman & Tversky).
    - [ ] Implementar a `value_fn` (como no seu protótipo Rust).
    - [ ] A lógica de decisão do `Comprador` deve usar `value_fn(orçamento - custo_total)`.

- [ ] **Ação 7.3:** Apertar o Ponto de Referência (Orçamento).
    - [ ] Vincular o `ref_point` (orçamento) ao `storage` solicitado, para forçar o surgimento de "aversão à perda".

- [ ] **Ação 7.4:** Implementar a Teoria dos Jogos (Provedor).
    - [ ] A lógica de precificação do `Provedor` deve reagir aos preços médios do mercado.

### Fase 8: 🤖 Futuro (Integração com IA)

**Meta:** Substituir a lógica codificada por agentes inteligentes.

- [ ] **Ação 8.1:** Aprendizado por Reforço (RL) para Provedores.
    - [ ] O `Provedor` se torna um agente de RL (usando `gymnasium` + `stable-baselines3`).
    - [ ] **Ação:** Mudar preço.
    - [ ] **Recompensa:** Lucro total.
    - [ ] **Objetivo:** Encontrar a política de preços ótima.

- [ ] **Ação 8.2:** Agentes de Linguagem (LLM) para Compradores.
    - [ ] [cite_start]Usar LLMs (como o CAMEL [cite: 1257]) para simular negociações complexas de contratos.