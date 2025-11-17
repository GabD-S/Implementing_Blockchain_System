import numpy as np
from typing import List, Dict

def compute_tps(total_tx: int, simulation_time: int) -> float:
    return total_tx / max(1.0, simulation_time)

def latency_statistics(latencies_ms: List[float]) -> Dict:
    if not latencies_ms:
        return {'avg': 0.0, 'p50': 0.0, 'p90': 0.0, 'p99': 0.0}
    a = np.array(latencies_ms)
    return {
        'avg': float(np.mean(a)),
        'p50': float(np.percentile(a, 50)),
        'p90': float(np.percentile(a, 90)),
        'p99': float(np.percentile(a, 99)),
    }

def estimate_resources(total_tx: int, num_nodes: int) -> Dict:
    # Simple heuristic estimates
    avg_bandwidth_per_tx_kb = 50.0
    total_kb = total_tx * avg_bandwidth_per_tx_kb
    bandwidth_mbps = (total_kb * 8.0) / (1024.0 * 1024.0)  # MBps -> Mbps
    cpu_load_per_node = min(1.0, (total_tx / max(1, num_nodes)) / 1000.0)
    mem_per_node_mb = min(8192.0, 100.0 + (total_tx / max(1, num_nodes)) * 0.5)
    return {
        'bandwidth_mbps': bandwidth_mbps,
        'cpu_load_per_node': cpu_load_per_node,
        'mem_per_node_mb': mem_per_node_mb
    }

def simulate_forks_rate(avg_propagation_ms: float) -> float:
    # heuristic: higher propagation increases fork probability
    return min(0.5, (avg_propagation_ms / 1000.0) * 0.05)

def availability_over_time(simulation_time: int, reliability: float) -> List[float]:
    # returns availability fraction per timeslice (0..1)
    rng = np.random.default_rng(42)
    return list(rng.binomial(1, reliability, size=simulation_time).astype(float))
