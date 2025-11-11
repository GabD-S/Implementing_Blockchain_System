use rand::distributions::Distribution;
use rand::{rngs::StdRng, Rng, SeedableRng};
use rand_distr::{Gamma, LogNormal, Poisson, Uniform};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BuyerAgent {
    pub id: usize,
    pub budget: f64,
    pub storage_needed: u32,
    pub max_price: f64,
    pub reputation_threshold: f64,
    pub transactions: u32,
    pub total_spent: f64,
    pub successful_purchases: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProviderAgent {
    pub id: usize,
    pub capacity: u32,
    pub price_per_gb: f64,
    pub reputation: f64,
    pub available: u32,
    pub transactions: u32,
    pub total_earned: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NetworkAgent {
    pub id: usize,
    pub commission_rate: f64,
    pub transactions_facilitated: u32,
    pub total_commission: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Transaction {
    pub timestamp: f64,
    pub buyer_id: usize,
    pub provider_id: usize,
    pub network_id: usize,
    pub storage_gb: u32,
    pub price: f64,
    pub successful: bool,
    pub failure_reason: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SimConfig {
    pub name: String,
    pub num_buyers: usize,
    pub num_providers: usize,
    pub num_network_agents: usize,
    pub simulation_time: u32,
    pub transaction_rate: f64,
    pub seed: Option<u64>,
}

#[derive(Debug)]
pub struct Simulator {
    pub cfg: SimConfig,
    pub buyers: Vec<BuyerAgent>,
    pub providers: Vec<ProviderAgent>,
    pub networks: Vec<NetworkAgent>,
    pub transactions: Vec<Transaction>,
    time: f64,
    rng: StdRng,
}

impl Simulator {
    pub fn new(cfg: SimConfig) -> Self {
        let seed = cfg.seed.unwrap_or_else(|| 42);
        let rng = StdRng::seed_from_u64(seed);
        Self {
            cfg,
            buyers: Vec::new(),
            providers: Vec::new(),
            networks: Vec::new(),
            transactions: Vec::new(),
            time: 0.0,
            rng,
        }
    }

    fn sample_beta(&mut self, a: f64, b: f64) -> f64 {
        // Beta(a,b) ~ Gamma(a,1) / (Gamma(a,1) + Gamma(b,1))
        let ga = Gamma::new(a, 1.0).unwrap();
        let gb = Gamma::new(b, 1.0).unwrap();
        let x = ga.sample(&mut self.rng);
        let y = gb.sample(&mut self.rng);
        x / (x + y)
    }

    pub fn initialize_agents(&mut self) {
        // Buyers
        let ln = LogNormal::new(7.5, 0.5).unwrap();
        let storage = Uniform::new_inclusive(5_u32, 200_u32);
        let max_price = Uniform::new(0.05, 0.30);
        let rep_thr = Uniform::new(0.3, 0.8);
        for i in 0..self.cfg.num_buyers {
            let buyer = BuyerAgent {
                id: i,
                budget: ln.sample(&mut self.rng),
                storage_needed: storage.sample(&mut self.rng),
                max_price: max_price.sample(&mut self.rng),
                reputation_threshold: rep_thr.sample(&mut self.rng),
                transactions: 0,
                total_spent: 0.0,
                successful_purchases: 0,
            };
            self.buyers.push(buyer);
        }

        // Providers
        let cap = Uniform::new_inclusive(100_u32, 5000_u32);
        let price = Uniform::new(0.08, 0.25);
        for i in 0..self.cfg.num_providers {
            let provider = ProviderAgent {
                id: i,
                capacity: cap.sample(&mut self.rng),
                price_per_gb: price.sample(&mut self.rng),
                reputation: self.sample_beta(2.0, 1.0),
                available: 0,
                transactions: 0,
                total_earned: 0.0,
            };
            let mut p = provider;
            p.available = p.capacity;
            self.providers.push(p);
        }

        // Network agents
        let comm = Uniform::new(0.01, 0.10);
        for i in 0..self.cfg.num_network_agents {
            let n = NetworkAgent {
                id: i,
                commission_rate: comm.sample(&mut self.rng),
                transactions_facilitated: 0,
                total_commission: 0.0,
            };
            self.networks.push(n);
        }
    }

    pub fn execute_attempt(&mut self) {
        if self.buyers.is_empty() || self.providers.is_empty() || self.networks.is_empty() {
            return;
        }
        let buyer_idx = self.rng.gen_range(0..self.buyers.len());
        let provider_idx = self.rng.gen_range(0..self.providers.len());
        let network_idx = self.rng.gen_range(0..self.networks.len());

        let (b_id, p_id, n_id);
        // Borrow checker: we'll clone smaller pieces
        let (storage_needed, max_price, rep_thr, mut budget);
        {
            let b = &self.buyers[buyer_idx];
            b_id = b.id;
            storage_needed = b.storage_needed;
            max_price = b.max_price;
            rep_thr = b.reputation_threshold;
            budget = b.budget;
        }
        let (price_per_gb, mut available, mut reputation);
        {
            let p = &self.providers[provider_idx];
            p_id = p.id;
            price_per_gb = p.price_per_gb;
            available = p.available;
            reputation = p.reputation;
        }
        let commission_rate = self.networks[network_idx].commission_rate;
        n_id = self.networks[network_idx].id;

        let total_cost = storage_needed as f64 * price_per_gb;
        let commission = total_cost * commission_rate;
        let total_with_comm = total_cost + commission;

        let can_afford = budget >= total_with_comm;
        let has_capacity = available >= storage_needed;
        let price_ok = price_per_gb <= max_price;
        let reputation_ok = reputation >= rep_thr;
        let success = can_afford && has_capacity && price_ok && reputation_ok;

        let failure_reason = if success {
            String::new()
        } else if !can_afford {
            "insufficient_budget".into()
        } else if !has_capacity {
            "insufficient_capacity".into()
        } else if !price_ok {
            "price_too_high".into()
        } else {
            "reputation_too_low".into()
        };

        if success {
            // update buyer
            {
                let b = &mut self.buyers[buyer_idx];
                b.budget -= total_with_comm;
                b.total_spent += total_with_comm;
                b.successful_purchases += 1;
                b.transactions += 1;
            }
            // update provider
            {
                let p = &mut self.providers[provider_idx];
                p.available -= storage_needed;
                p.total_earned += total_cost;
                p.transactions += 1;
                p.reputation = (p.reputation + 0.005).min(1.0);
            }
            // update network
            {
                let n = &mut self.networks[network_idx];
                n.transactions_facilitated += 1;
                n.total_commission += commission;
            }
        } else {
            // penalize provider in selected failures
            if failure_reason == "insufficient_capacity" || failure_reason == "price_too_high" {
                let p = &mut self.providers[provider_idx];
                p.reputation = (p.reputation - 0.01).max(0.1);
            }
            let b = &mut self.buyers[buyer_idx];
            b.transactions += 1;
        }

        self.transactions.push(Transaction {
            timestamp: self.time,
            buyer_id: b_id,
            provider_id: p_id,
            network_id: n_id,
            storage_gb: storage_needed,
            price: total_cost,
            successful: success,
            failure_reason,
        });
    }

    pub fn run(&mut self) {
        self.initialize_agents();
        let poi = Poisson::new(self.cfg.transaction_rate).unwrap();
        for _t in 0..self.cfg.simulation_time {
            let attempts = poi.sample(&mut self.rng) as u32;
            for _ in 0..attempts { self.execute_attempt(); }
            self.time += 1.0;
        }
    }
}
