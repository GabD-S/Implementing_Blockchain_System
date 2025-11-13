#!/usr/bin/env python3
"""
Simple analysis script for cloud storage simulation results
"""

import matplotlib.pyplot as plt
import numpy as np
import json
import os

def create_sample_analysis():
    """Create sample analysis and visualizations"""
    
    # Sample data (in real implementation, this would come from simulation)
    agents_data = {
        'buyers': {'count': 5, 'success_rate': 0.85, 'avg_cost': 120.50},
        'providers': {'count': 3, 'success_rate': 0.92, 'avg_revenue': 450.25},
        'network': {'count': 2, 'success_rate': 0.88, 'avg_transactions': 25}
    }
    
    # Create visualization
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Success rates
    agent_types = list(agents_data.keys())
    success_rates = [agents_data[agent]['success_rate'] for agent in agent_types]
    
    axes[0,0].bar(agent_types, success_rates, color=['blue', 'green', 'orange'])
    axes[0,0].set_title('Success Rates by Agent Type')
    axes[0,0].set_ylabel('Success Rate')
    axes[0,0].set_ylim(0, 1)
    
    # Agent counts
    agent_counts = [agents_data[agent]['count'] for agent in agent_types]
    axes[0,1].pie(agent_counts, labels=agent_types, autopct='%1.1f%%')
    axes[0,1].set_title('Agent Distribution')
    
    # Economic performance
    costs = [agents_data['buyers']['avg_cost']]
    revenues = [agents_data['providers']['avg_revenue']]
    
    axes[1,0].bar(['Avg Cost', 'Avg Revenue'], [costs[0], revenues[0]], 
                  color=['red', 'green'])
    axes[1,0].set_title('Economic Performance')
    axes[1,0].set_ylabel('Amount ($)')
    
    # Network activity
    x = np.linspace(0, 60, 100)
    y = np.sin(x/10) * 10 + 20 + np.random.normal(0, 2, 100)
    axes[1,1].plot(x, y)
    axes[1,1].set_title('Network Activity Over Time')
    axes[1,1].set_xlabel('Time (seconds)')
    axes[1,1].set_ylabel('Transactions/sec')
    
    plt.tight_layout()
    plt.savefig('cloud_storage_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Save results
    results = {
        'simulation': 'Multi-Agent Cloud Storage',
        'timestamp': '2025-07-25',
        'agents': agents_data,
        'summary': {
            'total_agents': sum(agent_counts),
            'avg_success_rate': np.mean(success_rates),
            'economic_efficiency': revenues[0] / costs[0] if costs[0] > 0 else 0
        }
    }
    
    with open('simulation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("✅ Analysis complete!")
    print("📊 Visualization saved: cloud_storage_analysis.png")
    print("📄 Results saved: simulation_results.json")
    
    return results

if __name__ == "__main__":
    create_sample_analysis()
