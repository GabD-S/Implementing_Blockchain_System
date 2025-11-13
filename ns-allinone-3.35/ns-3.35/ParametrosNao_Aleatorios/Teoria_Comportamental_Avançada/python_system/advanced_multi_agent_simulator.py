#!/usr/bin/env python3
"""
Sistema de Simulação Multi-Agente para Cloud Storage
Versão Avançada com Múltiplos Cenários e Análise Completa
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

# Configurar estilo dos gráficos
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
        """Inicializa todos os agentes com parâmetros realistas"""
        
        # Buyer Agents
        for i in range(self.config['num_buyers']):
            buyer = BuyerAgent(
                id=i,
                budget=np.random.lognormal(7.5, 0.5),  # Budget: ~$500-5000
                storage_needed=np.random.randint(5, 200),  # 5-200 GB
                max_price=np.random.uniform(0.05, 0.30),  # $0.05-0.30 per GB
                reputation_threshold=np.random.uniform(0.3, 0.8)  # Threshold for provider reputation
            )
            self.buyers.append(buyer)
            
        # Provider Agents
        for i in range(self.config['num_providers']):
            provider = ProviderAgent(
                id=i,
                capacity=np.random.randint(100, 5000),  # 100-5000 GB capacity
                price_per_gb=np.random.uniform(0.08, 0.25),  # $0.08-0.25 per GB
                reputation=np.random.beta(2, 1)  # Skewed towards higher reputation
            )
            self.providers.append(provider)
            
        # Network Agents
        for i in range(self.config['num_network_agents']):
            network = NetworkAgent(
                id=i,
                commission_rate=np.random.uniform(0.01, 0.10)  # 1-10% commission
            )
            self.network_agents.append(network)
            
        print(f"✅ Initialized {len(self.buyers)} buyers, {len(self.providers)} providers, {len(self.network_agents)} network agents")
    
    def execute_transaction_attempt(self):
        """Executa uma tentativa de transação entre agentes aleatórios"""
        
        if not self.buyers or not self.providers or not self.network_agents:
            return
            
        # Selecionar agentes aleatoriamente
        buyer = random.choice(self.buyers)
        provider = random.choice(self.providers)
        network = random.choice(self.network_agents)
        
        # Verificar viabilidade da transação
        total_cost = buyer.storage_needed * provider.price_per_gb
        commission = total_cost * network.commission_rate
        total_cost_with_commission = total_cost + commission
        
        # Condições para sucesso
        can_afford = buyer.budget >= total_cost_with_commission
        has_capacity = provider.available >= buyer.storage_needed
        price_acceptable = provider.price_per_gb <= buyer.max_price
        reputation_ok = provider.reputation >= buyer.reputation_threshold
        
        success = can_afford and has_capacity and price_acceptable and reputation_ok
        
        # Determinar razão de falha
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
        
        # Criar transação
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
        
        # Atualizar estados dos agentes se bem-sucedida
        if success:
            buyer.budget -= total_cost_with_commission
            buyer.total_spent += total_cost_with_commission
            buyer.successful_purchases += 1
            buyer.transactions += 1
            
            provider.available -= buyer.storage_needed
            provider.total_earned += total_cost
            provider.transactions += 1
            provider.reputation = min(1.0, provider.reputation + 0.005)  # Pequeno aumento
            
            network.transactions_facilitated += 1
            network.total_commission += commission
        else:
            # Penalizar reputação do provider em alguns casos
            if failure_reason in ["insufficient_capacity", "price_too_high"]:
                provider.reputation = max(0.1, provider.reputation - 0.01)
            
            buyer.transactions += 1
        
        self.transactions.append(transaction)
    
    def run_simulation(self):
        """Executa a simulação completa"""
        print(f"🚀 Iniciando simulação por {self.config['simulation_time']} unidades de tempo...")
        
        self.initialize_agents()
        
        # Loop principal da simulação
        while self.time < self.config['simulation_time']:
            # Número de tentativas de transação por unidade de tempo
            num_attempts = np.random.poisson(self.config['transaction_rate'])
            
            for _ in range(num_attempts):
                self.execute_transaction_attempt()
            
            self.time += 1.0
            
            # Log de progresso
            if int(self.time) % (self.config['simulation_time'] // 10) == 0:
                successful = sum(1 for t in self.transactions if t.successful)
                print(f"⏱️  Tempo {self.time:.0f}: {len(self.transactions)} transações, {successful} bem-sucedidas")
        
        print("✅ Simulação concluída!")
    
    def get_statistics(self) -> Dict:
        """Calcula estatísticas detalhadas da simulação"""
        
        successful_transactions = [t for t in self.transactions if t.successful]
        failed_transactions = [t for t in self.transactions if not t.successful]
        
        # Estatísticas gerais
        total_transactions = len(self.transactions)
        success_rate = len(successful_transactions) / total_transactions if total_transactions > 0 else 0
        total_volume = sum(t.price for t in successful_transactions)
        
        # Estatísticas por tipo de falha
        failure_reasons = {}
        for t in failed_transactions:
            reason = t.failure_reason
            failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
        
        # Estatísticas dos agentes
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

def run_multiple_scenarios():
    """Executa múltiplos cenários de simulação"""
    
    scenarios = [
        {
            'name': 'Cenário Pequeno',
            'num_buyers': 10,
            'num_providers': 5,
            'num_network_agents': 2,
            'simulation_time': 100,
            'transaction_rate': 3
        },
        {
            'name': 'Cenário Médio',
            'num_buyers': 25,
            'num_providers': 12,
            'num_network_agents': 4,
            'simulation_time': 150,
            'transaction_rate': 5
        },
        {
            'name': 'Cenário Grande',
            'num_buyers': 50,
            'num_providers': 20,
            'num_network_agents': 8,
            'simulation_time': 200,
            'transaction_rate': 8
        },
        {
            'name': 'Cenário Intensivo',
            'num_buyers': 100,
            'num_providers': 35,
            'num_network_agents': 15,
            'simulation_time': 300,
            'transaction_rate': 12
        }
    ]
    
    results = {}
    
    for scenario in scenarios:
        print(f"\n{'='*50}")
        print(f"🎯 Executando {scenario['name']}")
        print(f"{'='*50}")
        
        simulator = MultiAgentCloudSimulator(scenario)
        start_time = time.time()
        simulator.run_simulation()
        execution_time = time.time() - start_time
        
        stats = simulator.get_statistics()
        stats['execution_time'] = execution_time
        results[scenario['name']] = stats
        
        print(f"⏱️  Tempo de execução: {execution_time:.2f}s")
        print(f"📊 Taxa de sucesso: {stats['general']['success_rate']:.1%}")
        print(f"💰 Volume total: ${stats['general']['total_volume']:,.2f}")
    
    return results

def create_comprehensive_analysis(results: Dict):
    """Cria análise visual completa dos resultados"""
    
    # Configurar figura com múltiplos subplots
    fig = plt.figure(figsize=(20, 16))
    
    # 1. Taxa de sucesso por cenário
    ax1 = plt.subplot(3, 4, 1)
    scenarios = list(results.keys())
    success_rates = [results[s]['general']['success_rate'] * 100 for s in scenarios]
    bars1 = ax1.bar(scenarios, success_rates, color='lightgreen', alpha=0.8)
    ax1.set_title('Taxa de Sucesso por Cenário', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Taxa de Sucesso (%)')
    ax1.set_ylim(0, 100)
    plt.xticks(rotation=45)
    
    # Adicionar valores nas barras
    for bar, rate in zip(bars1, success_rates):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # 2. Volume total de transações
    ax2 = plt.subplot(3, 4, 2)
    volumes = [results[s]['general']['total_volume'] for s in scenarios]
    bars2 = ax2.bar(scenarios, volumes, color='lightblue', alpha=0.8)
    ax2.set_title('Volume Total de Transações', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Volume ($)')
    plt.xticks(rotation=45)
    
    # Adicionar valores nas barras
    for bar, vol in zip(bars2, volumes):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(volumes)*0.01, 
                f'${vol:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # 3. Número total de transações
    ax3 = plt.subplot(3, 4, 3)
    total_transactions = [results[s]['general']['total_transactions'] for s in scenarios]
    bars3 = ax3.bar(scenarios, total_transactions, color='orange', alpha=0.8)
    ax3.set_title('Total de Transações', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Número de Transações')
    plt.xticks(rotation=45)
    
    # Adicionar valores nas barras
    for bar, total in zip(bars3, total_transactions):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(total_transactions)*0.01, 
                f'{total}', ha='center', va='bottom', fontweight='bold')
    
    # 4. Utilização média dos providers
    ax4 = plt.subplot(3, 4, 4)
    utilizations = [results[s]['providers']['avg_utilization'] * 100 for s in scenarios]
    bars4 = ax4.bar(scenarios, utilizations, color='purple', alpha=0.8)
    ax4.set_title('Utilização Média dos Providers', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Utilização (%)')
    ax4.set_ylim(0, 100)
    plt.xticks(rotation=45)
    
    # Adicionar valores nas barras
    for bar, util in zip(bars4, utilizations):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                f'{util:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # 5. Reputação média dos providers
    ax5 = plt.subplot(3, 4, 5)
    reputations = [results[s]['providers']['avg_reputation'] for s in scenarios]
    bars5 = ax5.bar(scenarios, reputations, color='red', alpha=0.8)
    ax5.set_title('Reputação Média dos Providers', fontsize=12, fontweight='bold')
    ax5.set_ylabel('Reputação (0-1)')
    ax5.set_ylim(0, 1)
    plt.xticks(rotation=45)
    
    # Adicionar valores nas barras
    for bar, rep in zip(bars5, reputations):
        ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, 
                f'{rep:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # 6. Comissões totais dos network agents
    ax6 = plt.subplot(3, 4, 6)
    commissions = [results[s]['network']['total_commission'] for s in scenarios]
    bars6 = ax6.bar(scenarios, commissions, color='brown', alpha=0.8)
    ax6.set_title('Comissões Totais', fontsize=12, fontweight='bold')
    ax6.set_ylabel('Comissões ($)')
    plt.xticks(rotation=45)
    
    # Adicionar valores nas barras
    for bar, comm in zip(bars6, commissions):
        ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(commissions)*0.01, 
                f'${comm:.0f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # 7. Razões de falha (para o cenário maior)
    ax7 = plt.subplot(3, 4, 7)
    largest_scenario = max(scenarios, key=lambda s: results[s]['general']['total_transactions'])
    failure_reasons = results[largest_scenario]['failure_reasons']
    
    if failure_reasons:
        labels = list(failure_reasons.keys())
        values = list(failure_reasons.values())
        ax7.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        ax7.set_title(f'Razões de Falha\n({largest_scenario})', fontsize=12, fontweight='bold')
    else:
        ax7.text(0.5, 0.5, 'Sem falhas', ha='center', va='center', transform=ax7.transAxes)
        ax7.set_title('Razões de Falha', fontsize=12, fontweight='bold')
    
    # 8. Tempo de execução
    ax8 = plt.subplot(3, 4, 8)
    exec_times = [results[s]['execution_time'] for s in scenarios]
    bars8 = ax8.bar(scenarios, exec_times, color='gray', alpha=0.8)
    ax8.set_title('Tempo de Execução', fontsize=12, fontweight='bold')
    ax8.set_ylabel('Tempo (segundos)')
    plt.xticks(rotation=45)
    
    # Adicionar valores nas barras
    for bar, time_val in zip(bars8, exec_times):
        ax8.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(exec_times)*0.01, 
                f'{time_val:.2f}s', ha='center', va='bottom', fontweight='bold')
    
    # 9. Comparação de agentes (para o cenário maior)
    ax9 = plt.subplot(3, 4, 9)
    scenario_data = results[largest_scenario]['simulation_config']
    agent_counts = [
        scenario_data['num_buyers'],
        scenario_data['num_providers'], 
        scenario_data['num_network_agents']
    ]
    agent_types = ['Buyers', 'Providers', 'Network']
    ax9.pie(agent_counts, labels=agent_types, autopct='%1.1f%%', startangle=90)
    ax9.set_title(f'Distribuição de Agentes\n({largest_scenario})', fontsize=12, fontweight='bold')
    
    # 10. Escalabilidade - Transações vs Agentes
    ax10 = plt.subplot(3, 4, 10)
    total_agents = [results[s]['simulation_config']['num_buyers'] + 
                   results[s]['simulation_config']['num_providers'] + 
                   results[s]['simulation_config']['num_network_agents'] for s in scenarios]
    
    ax10.scatter(total_agents, total_transactions, s=100, alpha=0.7, color='darkblue')
    ax10.set_xlabel('Total de Agentes')
    ax10.set_ylabel('Total de Transações')
    ax10.set_title('Escalabilidade do Sistema', fontsize=12, fontweight='bold')
    
    # Adicionar linha de tendência
    z = np.polyfit(total_agents, total_transactions, 1)
    p = np.poly1d(z)
    ax10.plot(total_agents, p(total_agents), "r--", alpha=0.8)
    
    # 11. Eficiência econômica
    ax11 = plt.subplot(3, 4, 11)
    buyer_spending = [results[s]['buyers']['total_spent'] for s in scenarios]
    provider_earnings = [results[s]['providers']['total_earned'] for s in scenarios]
    
    x = np.arange(len(scenarios))
    width = 0.35
    
    ax11.bar(x - width/2, buyer_spending, width, label='Gastos Buyers', alpha=0.8, color='red')
    ax11.bar(x + width/2, provider_earnings, width, label='Ganhos Providers', alpha=0.8, color='green')
    
    ax11.set_xlabel('Cenários')
    ax11.set_ylabel('Valor ($)')
    ax11.set_title('Eficiência Econômica', fontsize=12, fontweight='bold')
    ax11.set_xticks(x)
    ax11.set_xticklabels([s.replace(' ', '\n') for s in scenarios])
    ax11.legend()
    
    # 12. Performance metrics resumo
    ax12 = plt.subplot(3, 4, 12)
    ax12.axis('off')
    
    # Calcular métricas resumo
    avg_success_rate = np.mean(success_rates)
    total_volume_all = sum(volumes)
    total_transactions_all = sum(total_transactions)
    avg_execution_time = np.mean(exec_times)
    
    summary_text = f"""RESUMO EXECUTIVO

📊 Taxa de Sucesso Média: {avg_success_rate:.1f}%
💰 Volume Total: ${total_volume_all:,.0f}
🔢 Transações Totais: {total_transactions_all:,}
⏱️ Tempo Médio: {avg_execution_time:.2f}s

🏆 Melhor Cenário: {scenarios[success_rates.index(max(success_rates))]}
📈 Maior Volume: {scenarios[volumes.index(max(volumes))]}"""
    
    ax12.text(0.1, 0.9, summary_text, transform=ax12.transAxes, fontsize=11,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('multi_agent_cloud_storage_complete_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("📊 Análise completa salva como: multi_agent_cloud_storage_complete_analysis.png")

def main():
    """Função principal que executa todo o sistema de simulação"""
    
    print("🌟 SISTEMA DE SIMULAÇÃO MULTI-AGENTE CLOUD STORAGE 🌟")
    print("=" * 60)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Executar múltiplos cenários
    results = run_multiple_scenarios()
    
    # Salvar resultados detalhados
    with open('simulation_results_detailed.json', 'w') as f:
        # Converter numpy types para JSON serializável
        def convert_numpy(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj
        
        # Converter recursivamente
        def clean_for_json(data):
            if isinstance(data, dict):
                return {k: clean_for_json(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [clean_for_json(v) for v in data]
            else:
                return convert_numpy(data)
        
        json.dump(clean_for_json(results), f, indent=2)
    
    # Criar análise visual
    create_comprehensive_analysis(results)
    
    # Imprimir resumo final
    print("\n" + "=" * 60)
    print("📈 RESUMO FINAL")
    print("=" * 60)
    
    for scenario_name, data in results.items():
        print(f"\n🎯 {scenario_name}:")
        print(f"   📊 Taxa de Sucesso: {data['general']['success_rate']:.1%}")
        print(f"   💰 Volume: ${data['general']['total_volume']:,.2f}")
        print(f"   🔢 Transações: {data['general']['total_transactions']:,}")
        print(f"   ⏱️ Tempo: {data['execution_time']:.2f}s")
    
    print(f"\n✅ Simulação completa! Resultados salvos em:")
    print("   📄 simulation_results_detailed.json")
    print("   📊 multi_agent_cloud_storage_complete_analysis.png")
    print(f"\n⏰ Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
