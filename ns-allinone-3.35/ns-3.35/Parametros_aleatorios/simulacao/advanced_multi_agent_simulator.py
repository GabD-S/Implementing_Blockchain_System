# Cópia reorganizada
from __future__ import annotations
# Mantido igual ao original (ver original em ns-3.35/advanced_multi_agent_simulator.py)
# Comentário: Esta versão foi movida para parametros_aleatorios/simulacao para indicar uso de geração estocástica.

#!/usr/bin/env python3
"""
Sistema de Simulação Multi-Agente para Cloud Storage
Versão Avançada com Múltiplos Cenários e Análise Completa
(CÓPIA) - pasta parametros_aleatorios/simulacao
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import json
import time
import random
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Tuple
import os

plt.style.use('default')
sns.set_palette("husl")

@dataclass
class BuyerAgent:
    id: int
    budget: float
    storage_needed: int
    max_price: float
    reputation_threshold: float
    transactions: int = 0
    total_spent: float = 0.0
    successful_purchases: int = 0
    
@dataclass
class ProviderAgent:
    id: int
    capacity: int
    price_per_gb: float
    reputation: float
    available: int = None
    transactions: int = 0
    total_earned: float = 0.0
    
    def __post_init__(self):
        if self.available is None:
            self.available = self.capacity
            
@dataclass
class NetworkAgent:
    id: int
    commission_rate: float
    transactions_facilitated: int = 0
    total_commission: float = 0.0
    
@dataclass
class Transaction:
    timestamp: float
    buyer_id: int
    provider_id: int
    network_id: int
    storage_gb: int
    price: float
    successful: bool
    failure_reason: str = ""

class MultiAgentCloudSimulator:
    def __init__(self, config: Dict):
        self.config = config
        self.buyers: List[BuyerAgent] = []
        self.providers: List[ProviderAgent] = []
        self.network_agents: List[NetworkAgent] = []
        self.transactions: List[Transaction] = []
        self.time = 0.0
        
    def initialize_agents(self):
        for i in range(self.config['num_buyers']):
            buyer = BuyerAgent(
                id=i,
                budget=np.random.lognormal(7.5, 0.5),
                storage_needed=np.random.randint(5, 200),
                max_price=np.random.uniform(0.05, 0.30),
                reputation_threshold=np.random.uniform(0.3, 0.8)
            )
            self.buyers.append(buyer)
        for i in range(self.config['num_providers']):
            provider = ProviderAgent(
                id=i,
                capacity=np.random.randint(100, 5000),
                price_per_gb=np.random.uniform(0.08, 0.25),
                reputation=np.random.beta(2, 1)
            )
            self.providers.append(provider)
        for i in range(self.config['num_network_agents']):
            network = NetworkAgent(
                id=i,
                commission_rate=np.random.uniform(0.01, 0.10)
            )
            self.network_agents.append(network)
        print(f"✅ Initialized {len(self.buyers)} buyers, {len(self.providers)} providers, {len(self.network_agents)} network agents")
    
    def execute_transaction_attempt(self):
        if not self.buyers or not self.providers or not self.network_agents:
            return
        buyer = random.choice(self.buyers)
        provider = random.choice(self.providers)
        network = random.choice(self.network_agents)
        total_cost = buyer.storage_needed * provider.price_per_gb
        commission = total_cost * network.commission_rate
        total_cost_with_commission = total_cost + commission
        can_afford = buyer.budget >= total_cost_with_commission
        has_capacity = provider.available >= buyer.storage_needed
        price_acceptable = provider.price_per_gb <= buyer.max_price
        reputation_ok = provider.reputation >= buyer.reputation_threshold
        success = can_afford and has_capacity and price_acceptable and reputation_ok
        failure_reason = ""
        if not success:
            if not can_afford:
                failure_reason = "insufficient_budget"
            elif not has_capacity:
                failure_reason = "insufficient_capacity"
            elif not price_acceptable:
                failure_reason = "price_too_high"
            elif not reputation_ok:
                failure_reason = "reputation_too_low"
        transaction = Transaction(
            timestamp=self.time,
            buyer_id=buyer.id,
            provider_id=provider.id,
            network_id=network.id,
            storage_gb=buyer.storage_needed,
            price=total_cost,
            successful=success,
            failure_reason=failure_reason
        )
        if success:
            buyer.budget -= total_cost_with_commission
            buyer.total_spent += total_cost_with_commission
            buyer.successful_purchases += 1
            buyer.transactions += 1
            provider.available -= buyer.storage_needed
            provider.total_earned += total_cost
            provider.transactions += 1
            provider.reputation = min(1.0, provider.reputation + 0.005)
            network.transactions_facilitated += 1
            network.total_commission += commission
        else:
            if failure_reason in ["insufficient_capacity", "price_too_high"]:
                provider.reputation = max(0.1, provider.reputation - 0.01)
            buyer.transactions += 1
        self.transactions.append(transaction)
    
    def run_simulation(self):
        print(f"🚀 Iniciando simulação por {self.config['simulation_time']} unidades de tempo...")
        self.initialize_agents()
        while self.time < self.config['simulation_time']:
            num_attempts = np.random.poisson(self.config['transaction_rate'])
            for _ in range(num_attempts):
                self.execute_transaction_attempt()
            self.time += 1.0
            if int(self.time) % (self.config['simulation_time'] // 10) == 0:
                successful = sum(1 for t in self.transactions if t.successful)
                print(f"⏱️  Tempo {self.time:.0f}: {len(self.transactions)} transações, {successful} bem-sucedidas")
        print("✅ Simulação concluída!")
    
    def get_statistics(self) -> Dict:
        successful_transactions = [t for t in self.transactions if t.successful]
        failed_transactions = [t for t in self.transactions if not t.successful]
        total_transactions = len(self.transactions)
        success_rate = len(successful_transactions) / total_transactions if total_transactions > 0 else 0
        total_volume = sum(t.price for t in successful_transactions)
        failure_reasons = {}
        for t in failed_transactions:
            reason = t.failure_reason
            failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
        buyer_stats = {
            'total_spent': sum(b.total_spent for b in self.buyers),
            'avg_budget_remaining': np.mean([b.budget for b in self.buyers]),
            'avg_transactions': np.mean([b.transactions for b in self.buyers])
        }
        provider_stats = {
            'total_earned': sum(p.total_earned for p in self.providers),
            'avg_utilization': np.mean([(p.capacity - p.available) / p.capacity for p in self.providers]),
            'avg_reputation': np.mean([p.reputation for p in self.providers])
        }
        network_stats = {
            'total_commission': sum(n.total_commission for n in self.network_agents),
            'avg_transactions': np.mean([n.transactions_facilitated for n in self.network_agents])
        }
        return {
            'general': {
                'total_transactions': total_transactions,
                'successful_transactions': len(successful_transactions),
                'success_rate': success_rate,
                'total_volume': total_volume
            },
            'failure_reasons': failure_reasons,
            'buyers': buyer_stats,
            'providers': provider_stats,
            'network': network_stats,
            'simulation_config': self.config
        }

def main():
    scenario = {
        'name': 'Copia Simples',
        'num_buyers': 10,
        'num_providers': 5,
        'num_network_agents': 2,
        'simulation_time': 50,
        'transaction_rate': 3
    }
    sim = MultiAgentCloudSimulator(scenario)
    sim.run_simulation()
    stats = sim.get_statistics()
    # Salvar resultados na pasta "resultados" dentro de parametros_aleatorios
    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resultados')
    os.makedirs(base_dir, exist_ok=True)
    out_path = os.path.join(base_dir, 'simulation_results_detailed.json')
    with open(out_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f'Resultados salvos em {out_path}')

if __name__ == '__main__':
    main()
