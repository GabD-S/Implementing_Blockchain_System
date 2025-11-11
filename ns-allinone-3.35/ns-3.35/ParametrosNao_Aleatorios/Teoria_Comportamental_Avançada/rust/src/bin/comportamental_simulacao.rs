use rand::{Rng, SeedableRng};
use rand::rngs::StdRng;
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

    let buyers: Vec<ProspectBuyer> = (0..25).map(|i| ProspectBuyer {
        id: i,
        ref_point: rng.gen_range(400.0..6000.0), // orçamento como ponto de referência
        storage: rng.gen_range(15..180),
        alpha: 0.88,
        beta: 0.88,
        lambda: 2.25,
    }).collect();

    let providers: Vec<ProspectProvider> = (0..12).map(|i| ProspectProvider {
        id: i,
        capacity: rng.gen_range(800..5000),
        price: rng.gen_range(0.08..0.24),
        fairness_threshold: rng.gen_range(0.10..0.18),
        reputation: rng.gen_range(0.4..0.9),
    }).collect();

    let mut decisions: Vec<Decision> = Vec::new();

    for b in &buyers {
        // prospect theory evaluation across providers
        let mut best: Option<Decision> = None;
        for p in &providers {
            if p.capacity < b.storage { continue; }
            let total_cost = b.storage as f64 * p.price;
            let relative = b.ref_point - total_cost; // ganho ou perda
            let v = value_fn(relative, b.alpha, b.beta, b.lambda);
            let fairness_penalty = if p.price > p.fairness_threshold { (p.price - p.fairness_threshold) * 10.0 } else { 0.0 };
            let fairness_score = (1.0 - fairness_penalty).max(0.0) * p.reputation;
            let accept = v > - (b.lambda) && fairness_score > 0.2; // critérios simplificados
            let decision = Decision { buyer_id: b.id, provider_id: p.id, accepted: accept, value_fn: v, perceived_fairness: fairness_score };
            if let Some(ref current) = best {
                if decision.accepted && (!current.accepted || decision.value_fn > current.value_fn) { best = Some(decision); }
            } else { best = Some(decision); }
        }
        if let Some(d) = best { decisions.push(d); }
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

    fs::create_dir_all("ParametrosNao_Aleatorios/Teoria_Comportamental_Avançada/rust/resultados")?;
    let mut f = File::create("ParametrosNao_Aleatorios/Teoria_Comportamental_Avançada/rust/resultados/comportamental_resultados.json")?;
    f.write_all(serde_json::to_string_pretty(&out)?.as_bytes())?;
    println!("Resultados (comportamental) salvos em .../comportamental_resultados.json");
    Ok(())
}
