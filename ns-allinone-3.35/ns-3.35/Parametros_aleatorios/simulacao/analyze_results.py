#!/usr/bin/env python3
"""Cópia reorganizada do script de análise simples."""
import matplotlib.pyplot as plt
import numpy as np
import json
import os

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resultados')
os.makedirs(RESULTS_DIR, exist_ok=True)

def create_sample_analysis():
    agents_data = {
        'buyers': {'count': 5, 'success_rate': 0.85, 'avg_cost': 120.50},
        'providers': {'count': 3, 'success_rate': 0.92, 'avg_revenue': 450.25},
        'network': {'count': 2, 'success_rate': 0.88, 'avg_transactions': 25}
    }
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    agent_types = list(agents_data.keys())
    success_rates = [agents_data[agent]['success_rate'] for agent in agent_types]
    axes[0,0].bar(agent_types, success_rates, color=['blue', 'green', 'orange'])
    axes[0,0].set_title('Success Rates by Agent Type')
    axes[0,0].set_ylabel('Success Rate')
    axes[0,0].set_ylim(0, 1)
    agent_counts = [agents_data[agent]['count'] for agent in agent_types]
    axes[0,1].pie(agent_counts, labels=agent_types, autopct='%1.1f%%')
    axes[0,1].set_title('Agent Distribution')
    costs = [agents_data['buyers']['avg_cost']]
    revenues = [agents_data['providers']['avg_revenue']]
    axes[1,0].bar(['Avg Cost', 'Avg Revenue'], [costs[0], revenues[0]], color=['red', 'green'])
    axes[1,0].set_title('Economic Performance')
    axes[1,0].set_ylabel('Amount ($)')
    x = np.linspace(0, 60, 100)
    y = np.sin(x/10) * 10 + 20 + np.random.normal(0, 2, 100)
    axes[1,1].plot(x, y)
    axes[1,1].set_title('Network Activity Over Time')
    axes[1,1].set_xlabel('Time (seconds)')
    axes[1,1].set_ylabel('Transactions/sec')
    plt.tight_layout()
    out_img = os.path.join(RESULTS_DIR, 'cloud_storage_analysis.png')
    plt.savefig(out_img, dpi=300, bbox_inches='tight')
    plt.close()
    results = {
        'simulation': 'Multi-Agent Cloud Storage',
        'agents': agents_data,
        'summary': {
            'total_agents': sum(agent_counts),
            'avg_success_rate': np.mean(success_rates),
            'economic_efficiency': revenues[0] / costs[0] if costs[0] > 0 else 0
        }
    }
    out_json = os.path.join(RESULTS_DIR, 'simulation_results.json')
    with open(out_json, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"✅ Analysis complete!\n📊 Visualization: {out_img}\n📄 Results: {out_json}")
    return results

if __name__ == '__main__':
    create_sample_analysis()
