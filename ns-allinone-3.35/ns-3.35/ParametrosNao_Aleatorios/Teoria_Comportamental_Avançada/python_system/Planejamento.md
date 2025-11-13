# checklist de ações — confecção do projeto sma

## smartcontract

* especificar abi e eventos
* implementar em solidity (versão 0.8.x)
* adicionar funções: constructor/create, set_state, set_reserve, verify_hash (view)
* emitir eventos: agreement_created, state_changed, reserve_set
* testar com hardhat: unit tests cobrindo constructor, only_party modifier, verify_hash
* implementar factory contract opcional para criação dinâmica de acordos

## plataforma do comprador

* gerar request com parâmetros de tamanho, duração, qos, orçamento, deadline
* coletar propostas e escolher a melhor por regra definida
* gerar json final do acordo e calcular keccak256(json)
* assinar a versão final off-chain (eip-191/eip-712)
* publicar hash on-chain via adapter (ns3_adapter.publish_hash)
* reagir a eventos on-chain (state_changed)
* criar métricas internas: tempo até acordo, tentativas, taxa de sucesso
* definir cli/http interface do ns3_adapter com endpoints: /publish, /set_state, /verify

## plataforma do vendedor

* receber request com requisitos
* formular proposta com preço, capacidade e reputação
* aceitar se condições forem satisfeitas (price <= threshold, disponibilidade ok)
* simular falhas com parâmetro failure_prob controlado pelo ns-3
* emitir confirmação off-chain após aceitar contrato
* escutar eventos on-chain e executar set_state(failed/completed)
* definir parâmetros configuráveis pelo ns-3: total_capacity, reserved_capacity, failure_prob, response_latency, pricing_model

## integração com ns-3

* criar ns3_adapter.py ou node adapter para expor endpoints /publish, /set_state, /simulate_event
* definir como o ns-3 aciona buyer e seller agents (por eventos simulados)
* usar nó local (ganache/hardhat node) ou mock para registrar chamadas on-chain
* documentar no simulator_integration/readme os comandos ns-3 necessários

## especificações de dados e eventos

* definir formato json do contrato off-chain com campos id, buyer, seller, qos, size_gb, price, start, end, reserve_ptr, meta
* calcular keccak256(json) como contract_hash
* definir eventos on-chain: agreement_created, state_changed, reserve_set
* definir mensagens off-chain: request, proposal, accept, publish_hash, onchain_event

## testes e validação

* criar testes unitários para funções principais do contrato
* criar testes de integração simulando cenários de sucesso, falha e disputa
* medir taxa de sucesso, tempo até publicação on-chain, número de chamadas, utilização dos provedores, eventos por tempo

## segurança e revisão

* revisar imports e usar bibliotecas auditadas (openzeppelin)
* evitar strings longas on-chain; preferir bytes32 e events
* restringir funções mutáveis com modifiers only_party/only_owner
* rodar slither/solhint e fuzz tests
* planejar atualização de lógica apenas se necessária
