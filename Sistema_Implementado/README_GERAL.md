# 📦 Sistema de Armazenamento Descentralizado (Storage Market)

Este projeto implementa um sistema completo de armazenamento descentralizado, integrando Blockchain (Substrate/ink!), IPFS e Wormhole para transferência segura de arquivos P2P. O sistema é composto por três pilares principais:

1. **Smart Contract (Blockchain Backend)**: Gerencia acordos, pagamentos e reputação dos provedores.
2. **Provider Daemon (Backend Off-chain)**: Serviço do provedor que escuta a blockchain e gerencia o armazenamento físico e transferências via Wormhole.
3. **Storage DApp (Frontend)**: Interface web para contratação de armazenamento e transferência de arquivos.

---

## 🛠️ Instalação e Configuração

### 1. Pré-requisitos

- **Rust & Cargo**: Para compilar o contrato e o daemon.
- **Node.js & NPM**: Para rodar o frontend.
- **IPFS Desktop ou CLI**: Para a rede de armazenamento distribuído.
- **Wormhole CLI**: Para transferência segura de arquivos.
  - Instale com:
    ```bash
    curl -L https://github.com/wormhole-foundation/wormhole/releases/latest/download/wormhole-linux-amd64 -o wormhole && chmod +x wormhole && sudo mv wormhole /usr/local/bin/
    ```

---

### 2. Estrutura do Projeto

- `substrate-contracts-node-linux/`: Nó local da blockchain Substrate para contratos inteligentes.
- `storage_market/`: Contrato inteligente (Rust/ink!).
- `provider_daemon/`: Backend do provedor (Rust).
- `storage-dapp/`: Frontend da aplicação (React/TypeScript).
- `kubo/`: Binário e scripts do IPFS.

---

### 3. Configuração Inicial

#### a) Blockchain & Contrato

1. Inicie o nó local Substrate:
    ```bash
    ./substrate-contracts-node-linux/substrate-contracts-node --dev --tmp
    ```
    *Deixe este terminal aberto.*

2. Compile e implante o contrato:
    ```bash
    cd storage_market
    cargo contract build
    cargo contract instantiate --constructor new --suri //Alice --salt $(date +%s)
    ```
    *Anote o endereço do contrato gerado.*

#### b) IPFS

1. Inicie o daemon do IPFS:
    ```bash
    ipfs daemon
    ```
    *Deixe rodando em segundo plano.*

#### c) Provider Daemon (Backend Off-chain)

1. Compile o daemon:
    ```bash
    cd provider_daemon
    cargo build --release
    ```
2. Inicie o daemon:
    ```bash
    cargo run --release
    ```
    *O daemon ficará escutando eventos e gerenciando transferências.*

#### d) Storage DApp (Frontend)

1. Instale as dependências:
    ```bash
    cd storage-dapp
    npm install
    ```
2. Inicie o frontend:
    ```bash
    npm run dev
    ```
    O app abrirá em `http://localhost:1234` (ou porta similar).

---

## 📖 Como Utilizar

1. **No navegador (DApp):**
    - Clique em "Enviar Arquivo" e selecione o arquivo desejado.
    - O sistema irá gerar um código Wormhole real (ex: `7-galaxy-star`).
    - Um QR Code será exibido para facilitar o recebimento.

2. **No terminal (Recebimento):**
    - Em outro computador ou terminal, execute:
      ```bash
      wormhole receive <codigo-gerado>
      ```
    - Exemplo: `wormhole receive 7-galaxy-star`

3. **Gerenciamento de Contratos:**
    - Todos os acordos são registrados e podem ser visualizados na DApp.
    - O histórico local mostra comprador, provedor, preço e status.

---

## ⚠️ Notas Importantes

- Mantenha sempre o `provider_daemon` e o nó Substrate rodando.
- O código Wormhole é de uso único e expira após a transferência.
- O backend é responsável por toda a orquestração do Wormhole; o frontend apenas exibe códigos e logs reais.

---

## ▶️ Resumo dos Comandos para Rodar o Projeto

1. **Blockchain:**
    ```bash
    ./substrate-contracts-node-linux/substrate-contracts-node --dev --tmp
    ```
2. **IPFS:**
    ```bash
    ipfs daemon
    ```
3. **Provider Daemon:**
    ```bash
    cd provider_daemon
    cargo run --release
    ```
4. **Frontend (DApp):**
    ```bash
    cd storage-dapp
    npm install
    npm run dev
    ```

---

*Desenvolvido para a Web3. Dúvidas? Consulte o README original ou abra uma issue.*
