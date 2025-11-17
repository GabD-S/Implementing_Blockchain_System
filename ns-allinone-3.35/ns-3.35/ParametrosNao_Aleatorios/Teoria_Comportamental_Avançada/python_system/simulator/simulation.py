from typing import List, Dict
import numpy as np
from .agents import Buyer, Provider, generate_agents
from .contract import StorageMarketContract

def value_fn(x: float, alpha: float, beta: float, lambda_: float) -> float:
    if x >= 0.0:
        return x ** alpha
    return -lambda_ * ((-x) ** beta)

class Simulator:
    def __init__(self, seed: int = 2032, num_buyers: int = 25, num_providers: int = 12, simulation_time: int = 120, tx_rate: int = 5):
        self.seed = seed
        self.num_buyers = num_buyers
        self.num_providers = num_providers
        self.simulation_time = simulation_time
        self.tx_rate = tx_rate
        self.rng = np.random.default_rng(seed)
        self.buyers, self.providers = generate_agents(seed, num_buyers, num_providers)

    def run_matching(self) -> Dict:
        contract = StorageMarketContract()
        # register providers in contract
        for p in self.providers:
            contract.registerProvider(p.id, "")

        decisions = []
        remaining = [p.capacity for p in self.providers]
        for b in self.buyers:
            best = None
            for idx, p in enumerate(self.providers):
                if remaining[idx] < b.storage:
                    continue
                total_cost = b.storage * p.price
                relative = b.ref_point - total_cost
                v = value_fn(relative, b.alpha, b.beta, b.lambda_)
                fairness_penalty = (p.price - p.fairness_threshold) * 12.0 if p.price > p.fairness_threshold else 0.0
                fairness_score = max(0.0, 1.0 - fairness_penalty) * p.reputation
                accept = (v > 0.0) and (fairness_score > 0.40)
                decision = {
                    'buyer_id': b.id,
                    'provider_id': p.id,
                    'accepted': accept,
                    'value_fn': float(v),
                    'perceived_fairness': float(fairness_score),
                    'cost': float(total_cost)
                }
                if best is None:
                    best = decision
                else:
                    if decision['accepted'] and (not best['accepted'] or decision['value_fn'] > best['value_fn']):
                        best = decision
            if best is not None:
                if best['accepted']:
                    pid = best['provider_id']
                    if remaining[pid] >= self.buyers[best['buyer_id']].storage:
                        remaining[pid] -= self.buyers[best['buyer_id']].storage
                    # Drive contract state machine
                    deal_id = contract.requestStorage(best['buyer_id'], best['provider_id'], "QmCID")
                    contract.acceptProvider(best['provider_id'], deal_id)
                    contract.acceptBuyer(best['buyer_id'], deal_id)
                    contract.completeStorage(best['buyer_id'], deal_id)
                decisions.append(best)

        accepted = [d for d in decisions if d['accepted']]
        acceptance_rate = (len(accepted) / len(decisions)) if decisions else 0.0

        result = {
            'decisions': decisions,
            'accepted_count': len(accepted),
            'total_requests': len(decisions),
            'acceptance_rate': acceptance_rate,
            'providers_remaining_capacity': remaining,
            'contract_events': contract.events,
        }
        return result

    def run_time_simulation(self) -> Dict:
        # Simulate transactions over time to compute tps and latency distributions
        total_tx = 0
        latencies = []
        throughput_timeseries = []
        for t in range(self.simulation_time):
            # number of tx this second
            num_tx = self.rng.poisson(self.tx_rate)
            total_tx += num_tx
            # latencies in ms: base + jitter
            l = self.rng.normal(100.0, 20.0, size=max(0, num_tx))
            l = [max(1.0, float(x)) for x in l]
            latencies.extend(l)
            throughput_timeseries.append(num_tx)

        tps = total_tx / max(1.0, self.simulation_time)
        avg_latency = float(np.mean(latencies)) if latencies else 0.0

        return {
            'total_tx': total_tx,
            'tps': tps,
            'avg_latency_ms': avg_latency,
            'latencies_ms': latencies,
            'throughput_timeseries': throughput_timeseries
        }
