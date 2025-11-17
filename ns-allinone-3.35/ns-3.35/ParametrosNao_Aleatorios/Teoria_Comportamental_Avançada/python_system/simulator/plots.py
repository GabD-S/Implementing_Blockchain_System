import os
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from typing import Dict, List

RESULTS_DIR = os.path.join(os.getcwd(), 'resultados')
os.makedirs(RESULTS_DIR, exist_ok=True)

def save_plot(fig, name: str):
    path = os.path.join(RESULTS_DIR, name)
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)

def plot_tps_vs_nodes(scenarios: Dict):
    fig, ax = plt.subplots(figsize=(8,5))
    nodes = [s['general']['total_nodes'] for s in scenarios.values()]
    tps = [s['general']['tps'] for s in scenarios.values()]
    ax.plot(nodes, tps, marker='o')
    ax.set_xlabel('Total Nodes')
    ax.set_ylabel('TPS')
    ax.set_title('TPS vs Total Nodes')
    save_plot(fig, 'tps_vs_nodes.png')

def plot_latency_cdf(latencies: List[float], name='latency_cdf.png'):
    fig, ax = plt.subplots(figsize=(8,5))
    sorted_l = np.sort(latencies)
    p = np.arange(1, len(sorted_l)+1) / len(sorted_l)
    ax.plot(sorted_l, p)
    ax.set_xlabel('Latency (ms)')
    ax.set_ylabel('CDF')
    ax.set_title('Latency CDF')
    save_plot(fig, name)

def plot_throughput_timeseries(timeseries: List[int], name='throughput_timeseries.png'):
    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(timeseries)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Transactions/sec')
    ax.set_title('Throughput Timeseries')
    save_plot(fig, name)

def plot_heatmap_blocksize_interval(block_sizes, intervals, tps_matrix, lat_matrix, name='heatmap_blocksize_interval.png'):
    fig, axes = plt.subplots(1,2, figsize=(14,5))
    sns.heatmap(tps_matrix, xticklabels=intervals, yticklabels=block_sizes, ax=axes[0], cmap='viridis')
    axes[0].set_title('TPS heatmap')
    sns.heatmap(lat_matrix, xticklabels=intervals, yticklabels=block_sizes, ax=axes[1], cmap='magma')
    axes[1].set_title('Latency heatmap (ms)')
    save_plot(fig, name)

def plot_basic_summary(results: Dict):
    # Save a set of default plots from a single results dict
    plot_latency_cdf(results.get('latencies_ms', []), name='latency_cdf.png')
    plot_throughput_timeseries(results.get('throughput_timeseries', []), name='throughput_timeseries.png')

def plot_latency_vs_txrate(tx_rates: List[int], avg_latencies: List[float], name='latency_vs_txrate.png'):
    fig, ax = plt.subplots(figsize=(8,5))
    ax.plot(tx_rates, avg_latencies, marker='o', color='#E74C3C')
    ax.set_xlabel('Transaction rate (tx/s)')
    ax.set_ylabel('Avg confirmation latency (ms)')
    ax.set_title('Latency vs Transaction Rate')
    save_plot(fig, name)

def plot_forks_vs_propagation(propagations_ms: List[float], forks_rates: List[float], name='forks_vs_propagation.png'):
    fig, ax = plt.subplots(figsize=(8,5))
    ax.plot(propagations_ms, forks_rates, marker='s', color='#8E44AD')
    ax.set_xlabel('Avg propagation (ms)')
    ax.set_ylabel('Fork rate (probability)')
    ax.set_title('Forks vs Propagation')
    save_plot(fig, name)

def plot_bandwidth_vs_throughput(throughputs: List[float], bandwidths: List[float], name='bandwidth_vs_throughput.png'):
    fig, ax = plt.subplots(figsize=(8,5))
    ax.scatter(throughputs, bandwidths, color='#3498DB')
    ax.set_xlabel('Throughput (TPS)')
    ax.set_ylabel('Estimated bandwidth (Mbps)')
    ax.set_title('Bandwidth vs Throughput')
    save_plot(fig, name)

def plot_cpu_vs_load(loads: List[float], name='cpu_vs_load.png'):
    fig, ax = plt.subplots(figsize=(8,5))
    ax.plot(range(1, len(loads)+1), [l*100 for l in loads], marker='^', color='#27AE60')
    ax.set_xlabel('Scenario index')
    ax.set_ylabel('CPU per node (%)')
    ax.set_title('CPU vs Load (per scenario)')
    save_plot(fig, name)

def plot_availability_vs_time(series: List[float], name='availability_vs_time.png'):
    fig, ax = plt.subplots(figsize=(10,3))
    ax.plot(series, color='#2C3E50')
    ax.set_ylim(-0.1, 1.1)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Availability')
    ax.set_title('Node Availability Over Time')
    save_plot(fig, name)

def plot_scalability_users(users: List[int], tps: List[float], acceptance: List[float], name='scalability_users.png'):
    fig, ax1 = plt.subplots(figsize=(9,5))
    ax1.set_xlabel('Number of users (buyers)')
    ax1.set_ylabel('TPS', color='#1F77B4')
    ax1.plot(users, tps, 'o-', color='#1F77B4')
    ax2 = ax1.twinx()
    ax2.set_ylabel('Acceptance rate (%)', color='#FF7F0E')
    ax2.plot(users, [a*100 for a in acceptance], 's--', color='#FF7F0E')
    fig.suptitle('Business Scalability: Users vs TPS and Acceptance')
    save_plot(fig, name)
