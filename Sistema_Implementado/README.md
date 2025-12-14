# 📦 Sistema de Armazenamento Descentralizado (Storage Market)

Bem-vindo ao Sistema de Armazenamento Descentralizado. Este projeto implementa um mercado completo de armazenamento de dados utilizando Blockchain (Substrate/ink!), IPFS e Wormhole para transferência segura de arquivos P2P.

O sistema é composto por três pilares fundamentais que devem operar em conjunto para garantir a integridade e disponibilidade dos dados:

1.  **Smart Contract (Backend Blockchain)**: Gerencia os acordos, pagamentos e reputação dos provedores.
2.  **Provider Daemon (Backend Off-chain)**: O "cérebro" do provedor que escuta a blockchain e gerencia o armazenamento físico.
3.  **Storage DApp (Frontend)**: A interface de usuário para contratar armazenamento e transferir arquivos.

---

## 🚀 Pré-requisitos

Antes de iniciar, certifique-se de ter instalado:

*   **Rust & Cargo**: Para compilar o contrato e o daemon.
*   **Node.js & NPM**: Para rodar o frontend.
*   **IPFS Desktop ou CLI**: Para a rede de armazenamento distribuído.
*   **Wormhole CLI**: Essencial para o túnel de transferência de dados criptografados.
    *   Instalação: `curl -L https://github.com/wormhole-foundation/wormhole/releases/latest/download/wormhole-linux-amd64 -o wormhole && chmod +x wormhole && sudo mv wormhole /usr/local/bin/`

---

## 🛠️ Instalação e Configuração

Siga a ordem abaixo para garantir que todos os componentes se comuniquem corretamente.

### 1. Configurar o Backend (Blockchain & Contrato)

O coração do sistema. Sem ele, não há consenso sobre os arquivos armazenados.

1.  Navegue até a pasta do nó Substrate (se estiver usando o `substrate-contracts-node`):
    ```bash
    ./substrate-contracts-node --dev --tmp
    ```
    *Deixe este terminal aberto rodando a blockchain.*

2.  Em outro terminal, compile e implante o contrato inteligente:
    ```bash
    cd storage_market
    cargo contract build
    cargo contract instantiate --constructor new --suri //Alice --salt $(date +%s)
    ```
    *Anote o endereço do contrato gerado.*

### 2. Iniciar o Provider Daemon

Este serviço é crucial. Ele conecta o mundo físico (seu disco rígido/IPFS) ao mundo digital (Blockchain). Ele monitora os contratos e garante que os dados sejam persistidos.

1.  Certifique-se que o IPFS está rodando:
    ```bash
    ipfs daemon
    ```

2.  Compile e inicie o daemon do provedor:
    ```bash
    cd provider_daemon
    cargo run --release
    ```
    *O daemon ficará escutando eventos de novos acordos na blockchain.*

### 3. Iniciar o Frontend (DApp)

A interface onde a mágica acontece.

1.  Instale as dependências:
    ```bash
    cd storage-dapp
    npm install
    ```

2.  Inicie o servidor de desenvolvimento:
    ```bash
    npm start
    ```
    O aplicativo abrirá em `http://localhost:1234` (ou porta similar).

---

## 📖 Guia de Uso

### Transferindo Arquivos com Segurança

O sistema utiliza uma abordagem híbrida inovadora. Enquanto o contrato inteligente registra a posse e o pagamento, o **Wormhole** é utilizado para o transporte seguro dos dados entre o Cliente e o Provedor.

1.  **No DApp (Navegador):**
    *   Clique em **"Enviar Arquivo"** e selecione o arquivo desejado.
    *   O sistema irá gerar um **Código Wormhole** único e criptografado (ex: `7-galaxy-star`).
    *   Um QR Code será gerado para facilitar a leitura por dispositivos móveis ou outros terminais.

2.  **No Terminal (Envio):**
    *   O DApp instruirá você a abrir seu terminal e executar o comando de envio para iniciar o túnel. O arquivo selecionado será preparado para o teletransporte digital.

3.  **No Outro PC (Recuperação):**
    *   Para baixar o arquivo em outra máquina (ou simular o recebimento pelo provedor), utilize o código gerado:
    ```bash
    wormhole receive <codigo-gerado>
    ```
    *   Exemplo: `wormhole receive 7-galaxy-star`

### Gerenciando Contratos

*   Todos os acordos firmados são registrados na tabela **"Contratos Realizados"**.
*   O sistema mantém um histórico local de todas as suas transações, incluindo Comprador, Vendedor, Preço e Status.
*   **Nota Importante**: Cada contrato é único. Se desejar armazenar outro arquivo, um novo contrato deve ser gerado na blockchain para garantir a imutabilidade do acordo.

---

## ⚠️ Notas do Sistema

*   **Backend Ativo**: Mantenha sempre o `provider_daemon` e o `substrate-contracts-node` rodando. Embora a transferência de dados ocorra via Wormhole, o registro do evento na blockchain é o que garante a validade jurídica do armazenamento no ecossistema descentralizado.
*   **Segurança**: O código Wormhole é de uso único. Após a transferência bem-sucedida, o túnel é fechado automaticamente.

---

*Desenvolvido para a Web3.*
