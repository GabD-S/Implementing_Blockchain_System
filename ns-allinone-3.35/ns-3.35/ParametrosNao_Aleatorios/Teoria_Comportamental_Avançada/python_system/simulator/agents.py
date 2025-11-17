from dataclasses import dataclass
from typing import Optional
import numpy as np

@dataclass
class Buyer:
    id: int
    ref_point: float
    storage: int
    alpha: float
    beta: float
    lambda_: float

@dataclass
class Provider:
    id: int
    capacity: int
    price: float
    fairness_threshold: float
    reputation: float

@dataclass
class NetworkAgent:
    id: int
    bandwidth_mbps: float
    latency_ms: float
    reliability: float

def generate_agents(seed: int = 2032, num_buyers: int = 25, num_providers: int = 12):
    rng = np.random.default_rng(seed)
    expected_market_price = 0.15

    # Distributions (parameters ported from comportamental_simulacao.rs)
    storage_mu = np.log(50.0)
    storage_sigma = 0.6
    capacity_mu = np.log(1200.0)
    capacity_sigma = 0.7
    price_mu = 0.18
    price_sigma = 0.03
    rep_a, rep_b = 5.0, 2.0
    ref_noise_mu = -0.05
    ref_noise_sigma = 0.10

    buyers = []
    for i in range(num_buyers):
        storage = int(np.clip(rng.lognormal(storage_mu, storage_sigma), 10, 400))
        raw_noise = rng.normal(ref_noise_mu, ref_noise_sigma)
        noise = float(np.clip(raw_noise, -0.3, 0.25))
        ref_point = max(5.0, storage * expected_market_price * (1.0 + noise))
        buyers.append(Buyer(i, ref_point, storage, 0.88, 0.88, 2.25))

    providers = []
    for i in range(num_providers):
        capacity = int(np.clip(rng.lognormal(capacity_mu, capacity_sigma), 400, 8000))
        price = float(np.clip(rng.normal(price_mu, price_sigma), 0.16, 0.24))
        fairness_threshold = float(np.clip(rng.normal(expected_market_price, 0.02), 0.10, 0.20))
        reputation = 0.4 + 0.5 * rng.beta(rep_a, rep_b)
        providers.append(Provider(i, capacity, price, fairness_threshold, reputation))

    return buyers, providers
