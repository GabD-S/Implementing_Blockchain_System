use rand::SeedableRng;
use rand::rngs::StdRng;
use rand_distr::{Distribution, LogNormal, Normal, Beta};
use serde::Serialize;
use std::fs::{self, File};
use std::io::Write;

#[derive(Debug, Serialize, Clone)]
struct ProspectBuyer { id: usize, ref_point: f64, storage: u32, alpha: f64, beta: f64, lambda: f64 }
#[derive(Debug, Serialize, Clone)]
struct ProspectProvider { id: usize, capacity: u32, price: f64, fairness_threshold: f64, reputation: f64 }
#[derive(Debug, Serialize, Clone)]
struct Decision { buyer_id: usize, provider_id: usize, accepted: bool, value_fn: f64, perceived_fairness: f64 }

fn value_fn(x: f64, alpha: f64, beta: f64, lambda: f64) -> f64 {
    if x >= 0.0 { x.powf(alpha) } else { -lambda * (-x).powf(beta) }
}

fn main() -> anyhow::Result<()> {
    let seed = 2025u64 + 7;
    let mut rng = StdRng::seed_from_u64(seed);
    let expected_market_price: f64 = 0.15; // preço esperado de mercado (R$/GB)

    // --- Distribuições auxiliares ---
    // Storage (GB) ~ LogNormal
    let storage_logn = LogNormal::new( (50f64).ln(), 0.6 ).unwrap(); // mediana ~50GB, cauda longa
    // Capacity (GB) ~ LogNormal
    let capacity_logn = LogNormal::new( (1200f64).ln(), 0.7 ).unwrap(); // mediana ~1200GB
    // Price (R$/GB) ~ Normal truncado ao intervalo [0.16, 0.24] com média acima do mercado
    // Aumenta a chance de preço superar o ponto de referência do comprador, gerando rejeições
    let price_norm = Normal::new(0.18, 0.03).unwrap();
    // Reputation ~ Beta(5,2) mapeada para [0.4, 0.9]
    let rep_beta = Beta::new(5.0, 2.0).unwrap();
    // Ref point noise ~ Normal(-0.05, 0.10) levemente enviesado para baixo para gerar mais perdas potenciais
    let ref_noise_norm = Normal::new(-0.05, 0.10).unwrap();

    let buyers: Vec<ProspectBuyer> = (0..25).map(|i| {
        // storage lognormal com limites razoáveis
        let mut storage = storage_logn.sample(&mut rng).round().max(10.0).min(400.0) as u32;
        if storage == 0 { storage = 10; }
        // orçamento ancorado no preço de mercado com ruído controlado
    let raw_noise = ref_noise_norm.sample(&mut rng);
    let noise = if raw_noise < -0.3 { -0.3 } else if raw_noise > 0.25 { 0.25 } else { raw_noise }; // clamp assimétrico (-30%, +25%)
        let ref_point = (storage as f64 * expected_market_price * (1.0 + noise)).max(5.0);
        ProspectBuyer {
            id: i,
            ref_point,
            storage,
            alpha: 0.88,
            beta: 0.88,
            lambda: 2.25,
        }
    }).collect();

    let providers: Vec<ProspectProvider> = (0..12).map(|i| {
        // capacity lognormal com limites
        let capacity = capacity_logn.sample(&mut rng).round().max(400.0).min(8000.0) as u32;
    // preço normal truncado
    let mut price: f64 = price_norm.sample(&mut rng);
    price = price.clamp(0.16, 0.24);
        // fairness threshold próximo do preço esperado
        let mut fairness_threshold = Normal::new(expected_market_price, 0.02).unwrap().sample(&mut rng);
        fairness_threshold = fairness_threshold.clamp(0.10, 0.20);
        // reputação beta mapeada para [0.4, 0.9]
        let reputation = 0.4 + 0.5 * rep_beta.sample(&mut rng);
        ProspectProvider { id: i, capacity, price, fairness_threshold, reputation }
    }).collect();

    let mut decisions: Vec<Decision> = Vec::new();
    // mapa de capacidade remanescente por provedor
    let mut remaining: Vec<u32> = providers.iter().map(|p| p.capacity).collect();

    for b in &buyers {
        // prospect theory evaluation across providers
        let mut best: Option<Decision> = None;
        for (idx, p) in providers.iter().enumerate() {
            if remaining[idx] < b.storage { continue; }
            let total_cost = b.storage as f64 * p.price;
            let relative = b.ref_point - total_cost; // ganho ou perda
            let v = value_fn(relative, b.alpha, b.beta, b.lambda);
            let fairness_penalty = if p.price > p.fairness_threshold { (p.price - p.fairness_threshold) * 12.0 } else { 0.0 };
            let fairness_score = (1.0 - fairness_penalty).max(0.0) * p.reputation;
            // Critério mais restritivo: exige ganho e fairness superior a 0.40
            let accept = v > 0.0 && fairness_score > 0.40;
            let decision = Decision { buyer_id: b.id, provider_id: p.id, accepted: accept, value_fn: v, perceived_fairness: fairness_score };
            if let Some(ref current) = best {
                if decision.accepted && (!current.accepted || decision.value_fn > current.value_fn) { best = Some(decision); }
            } else { best = Some(decision); }
        }
        if let Some(d) = best {
            // reserva capacidade caso aceite
            if d.accepted {
                if let Some(pos) = providers.iter().position(|p| p.id == d.provider_id) {
                    if remaining[pos] >= buyers[b.id].storage { remaining[pos] -= buyers[b.id].storage; }
                }
            }
            decisions.push(d);
        }
    }

    let accepted: Vec<&Decision> = decisions.iter().filter(|d| d.accepted).collect();
    let acceptance_rate = if decisions.is_empty() {0.0} else { accepted.len() as f64 / decisions.len() as f64 };

    let out = serde_json::json!({
        "seed": seed,
        "buyers": buyers,
        "providers": providers,
        "decisions": decisions,
        "acceptance_rate": acceptance_rate,
    });

    // Persistência: salvar diretamente no diretório local 'Resultados/' (maiúsculo)
    fs::create_dir_all("Resultados")?;
    let mut f = File::create("Resultados/comportamental_resultados.json")?;
    f.write_all(serde_json::to_string_pretty(&out)?.as_bytes())?;
    println!("Resultados (comportamental) salvos em .../comportamental_resultados.json");
    Ok(())
}
