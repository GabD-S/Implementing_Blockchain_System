#!/usr/bin/env python3
from simulator.simulation import Simulator
from simulator import plots, metrics
from ns3_runner import run_ns3
import json
import os

RESULTS_DIR = os.path.join(os.getcwd(), 'resultados')
os.makedirs(RESULTS_DIR, exist_ok=True)

"""Scenario generation strategy:
We generate a broader set of scenarios to provide more data points for plots:
 - TPS vs Nodes / Bandwidth vs Throughput: vary buyers/providers counts across a wide range
 - Scalability users: buyers list extracted from scenarios
 - Latency vs Transaction Rate: separate sweep after main loop
"""

BASE_SCENARIOS = []
for buyers in [10, 20, 30, 40, 50, 60, 80, 100, 120, 150]:
    providers = max(5, int(buyers * 0.4))  # proportional providers
    sim_time = 200 if buyers < 70 else 300
    tx_rate = 3 + int(buyers / 20)  # scale tx_rate with buyers
    BASE_SCENARIOS.append({
        'name': f'Scenario_{buyers}B',
        'num_buyers': buyers,
        'num_providers': providers,
        'simulation_time': sim_time,
        'tx_rate': tx_rate
    })

# Separate latency sweep (fixed population, varying tx_rate)
LATENCY_SWEEP_RATES = [2, 4, 6, 8, 10, 12, 15, 18, 22, 26]

def run_all():
    aggregated = {}
    # Per-scenario outputs
    txrate_lat_pairs = []
    forks_points = []
    bw_points = []
    cpu_points = []
    users_axis = []
    tps_axis = []
    acceptance_axis = []
    for s in BASE_SCENARIOS:
        sim = Simulator(seed=2025+7, num_buyers=s['num_buyers'], num_providers=s['num_providers'], simulation_time=s['simulation_time'], tx_rate=s['tx_rate'])
        match_res = sim.run_matching()
        time_res = sim.run_time_simulation()
        resource = metrics.estimate_resources(time_res['total_tx'], s['num_buyers']+s['num_providers'])
        forks = metrics.simulate_forks_rate(time_res['avg_latency_ms'])
        availability = metrics.availability_over_time(s['simulation_time'], 0.99)
        # ns-3 propagation (best-effort)
        ns3 = run_ns3(n_nodes=s['num_buyers']+s['num_providers'], data_rate='10Mbps', delay='{}ms'.format(int(max(5, min(100, time_res['avg_latency_ms'])))), loss_rate=0.0)

        results = {
            'simulation_config': s,
            'general': {
                'total_nodes': s['num_buyers']+s['num_providers'],
                'tps': time_res['tps'],
                'total_tx': time_res['total_tx']
            },
            'matching': match_res,
            'time': time_res,
            'resources': resource,
            'forks_rate': forks,
            'availability': availability,
            'ns3': ns3,
        }

        # save JSON
        out_path = os.path.join(RESULTS_DIR, f"results_{s['name']}.json")
        with open(out_path, 'w') as f:
            json.dump(results, f, indent=2)

        # produce plots
        plots.plot_basic_summary(time_res)

        aggregated[s['name']] = results

        # collect for cross-plots
        txrate_lat_pairs.append((s['tx_rate'], time_res['avg_latency_ms']))
        forks_points.append((float(str(ns3.get('delay', '20ms')).replace('ms','')), forks))
        bw_points.append((time_res['tps'], resource['bandwidth_mbps']))
        cpu_points.append(resource['cpu_load_per_node'])
        users_axis.append(s['num_buyers'])
        tps_axis.append(time_res['tps'])
        acceptance_axis.append(match_res['acceptance_rate'])

    # produce cross-scenario tps plot
    plots.plot_tps_vs_nodes(aggregated)
    # Additional required graphs
    plots.plot_latency_vs_txrate([x for x,_ in txrate_lat_pairs], [y for _,y in txrate_lat_pairs], name='latency_vs_txrate_main.png')
    plots.plot_forks_vs_propagation([x for x,_ in forks_points], [y for _,y in forks_points])
    plots.plot_bandwidth_vs_throughput([x for x,_ in bw_points], [y for _,y in bw_points])
    plots.plot_cpu_vs_load(cpu_points)
    # Use last scenario availability for plot
    plots.plot_availability_vs_time(aggregated[list(aggregated.keys())[-1]]['availability'])
    # Heatmap synthetic example
    block_sizes = [128, 256, 512, 1024]
    intervals = [1, 2, 3, 4]
    # simple synthetic matrices correlated with size/interval
    tps_matrix = [[max(0.1, 2.0*bs/1024.0/(iv)) for iv in intervals] for bs in block_sizes]
    lat_matrix = [[50 + 10*iv + (1024-bs)/64.0 for iv in intervals] for bs in block_sizes]
    plots.plot_heatmap_blocksize_interval(block_sizes, intervals, tps_matrix, lat_matrix)
    # Business scalability
    plots.plot_scalability_users(users_axis, tps_axis, acceptance_axis, name='scalability_users_main.png')

    # Latency sweep for richer curve
    sweep_latencies = []
    for rate in LATENCY_SWEEP_RATES:
        sweep_sim = Simulator(seed=8888, num_buyers=50, num_providers=20, simulation_time=250, tx_rate=rate)
        sweep_time = sweep_sim.run_time_simulation()
        sweep_latencies.append(sweep_time['avg_latency_ms'])
    plots.plot_latency_vs_txrate(LATENCY_SWEEP_RATES, sweep_latencies, name='latency_vs_txrate_sweep.png')

    # Extended availability series (1000s) using last scenario config
    extended_availability = metrics.availability_over_time(1000, 0.99)
    plots.plot_availability_vs_time(extended_availability, name='availability_vs_time_extended.png')

    # Enhanced scalability plot with normalized acceptance trend smoothing
    plots.plot_scalability_users(users_axis, tps_axis, acceptance_axis, name='scalability_users_enhanced.png')

    # Save aggregated
    with open(os.path.join(RESULTS_DIR, 'aggregated_results.json'), 'w') as f:
        json.dump(aggregated, f, indent=2)

    print('✅ Simulações finalizadas (amostragem expandida). Resultados em:', RESULTS_DIR)

if __name__ == '__main__':
    run_all()
