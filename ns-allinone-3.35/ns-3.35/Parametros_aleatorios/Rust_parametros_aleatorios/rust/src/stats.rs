use crate::model::{Simulator, Transaction};
use serde::Serialize;

#[derive(Debug, Serialize)]
pub struct GeneralStats {
    pub total_transactions: usize,
    pub successful_transactions: usize,
    pub success_rate: f64,
    pub total_volume: f64,
}

#[derive(Debug, Serialize)]
pub struct BuyerStats {
    pub total_spent: f64,
    pub avg_budget_remaining: f64,
    pub avg_transactions: f64,
}

#[derive(Debug, Serialize)]
pub struct ProviderStats {
    pub total_earned: f64,
    pub avg_utilization: f64,
    pub avg_reputation: f64,
}

#[derive(Debug, Serialize)]
pub struct NetworkStats {
    pub total_commission: f64,
    pub avg_transactions: f64,
}

#[derive(Debug, Serialize)]
pub struct FailureReasons(pub Vec<(String, usize)>);

#[derive(Debug, Serialize)]
pub struct SimulationReport {
    pub general: GeneralStats,
    pub failure_reasons: FailureReasons,
    pub buyers: BuyerStats,
    pub providers: ProviderStats,
    pub network: NetworkStats,
}

pub fn compute_stats(sim: &Simulator) -> SimulationReport {
    let total_transactions = sim.transactions.len();
    let successful: Vec<&Transaction> = sim.transactions.iter().filter(|t| t.successful).collect();
    let failed: Vec<&Transaction> = sim.transactions.iter().filter(|t| !t.successful).collect();
    let success_rate = if total_transactions > 0 { successful.len() as f64 / total_transactions as f64 } else { 0.0 };
    let total_volume: f64 = successful.iter().map(|t| t.price).sum();

    let failure_map = {
        use std::collections::HashMap;
        let mut m: HashMap<String, usize> = HashMap::new();
        for t in failed { *m.entry(t.failure_reason.clone()).or_insert(0) += 1; }
        let mut v: Vec<(String, usize)> = m.into_iter().collect();
        v.sort_by(|a,b| b.1.cmp(&a.1));
        v
    };

    let total_spent: f64 = sim.buyers.iter().map(|b| b.total_spent).sum();
    let avg_budget_remaining = if sim.buyers.is_empty() {0.0} else { sim.buyers.iter().map(|b| b.budget).sum::<f64>() / sim.buyers.len() as f64 };
    let avg_transactions_b = if sim.buyers.is_empty() {0.0} else { sim.buyers.iter().map(|b| b.transactions as f64).sum::<f64>() / sim.buyers.len() as f64 };

    let total_earned: f64 = sim.providers.iter().map(|p| p.total_earned).sum();
    let avg_utilization = if sim.providers.is_empty() {0.0} else { sim.providers.iter().map(|p| (p.capacity - p.available) as f64 / p.capacity as f64).sum::<f64>() / sim.providers.len() as f64 };
    let avg_reputation = if sim.providers.is_empty() {0.0} else { sim.providers.iter().map(|p| p.reputation).sum::<f64>() / sim.providers.len() as f64 };

    let total_commission: f64 = sim.networks.iter().map(|n| n.total_commission).sum();
    let avg_transactions_n = if sim.networks.is_empty() {0.0} else { sim.networks.iter().map(|n| n.transactions_facilitated as f64).sum::<f64>() / sim.networks.len() as f64 };

    SimulationReport {
        general: GeneralStats { total_transactions, successful_transactions: successful.len(), success_rate, total_volume },
        failure_reasons: FailureReasons(failure_map),
        buyers: BuyerStats { total_spent, avg_budget_remaining, avg_transactions: avg_transactions_b },
        providers: ProviderStats { total_earned, avg_utilization, avg_reputation },
        network: NetworkStats { total_commission, avg_transactions: avg_transactions_n },
    }
}
