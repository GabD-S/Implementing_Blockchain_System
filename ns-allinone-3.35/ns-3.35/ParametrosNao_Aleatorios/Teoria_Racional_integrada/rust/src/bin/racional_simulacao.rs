use rand::{Rng, SeedableRng};
use rand::rngs::StdRng;
use serde::Serialize;
use std::fs::{self, File};
use std::io::Write;

#[derive(Debug, Serialize, Clone)]
struct RacionalBuyer { id: usize, budget: f64, storage: u32, max_price: f64 }
#[derive(Debug, Serialize, Clone)]
struct RacionalProvider { id: usize, capacity: u32, price: f64, cost: f64 }
#[derive(Debug, Serialize, Clone)]
struct MatchResult { buyer_id: usize, provider_id: usize, accepted: bool, utility: f64 }

fn expected_utility(budget: f64, price_total: f64) -> f64 {
    if price_total > budget { return -10.0; }
    // utilidade simples logarítmica
    (budget - price_total + 1.0).ln()
}

fn main() -> anyhow::Result<()> {
    let seed = 2025u64;
    let mut rng = StdRng::seed_from_u64(seed);

    let buyers: Vec<RacionalBuyer> = (0..20).map(|i| RacionalBuyer {
        id: i,
        budget: rng.gen_range(300.0..5000.0),
        storage: rng.gen_range(10..150),
        max_price: rng.gen_range(0.06..0.28),
    }).collect();

    let providers: Vec<RacionalProvider> = (0..10).map(|i| RacionalProvider {
        id: i,
        capacity: rng.gen_range(500..4000),
        price: rng.gen_range(0.07..0.22),
        cost: rng.gen_range(0.02..0.05),
    }).collect();

    let mut matches: Vec<MatchResult> = Vec::new();

    for b in &buyers {
        // escolha racional: maximiza utilidade = -preço total sob restrições
        let mut best: Option<MatchResult> = None;
        for p in &providers {
            if p.capacity < b.storage { continue; }
            if p.price > b.max_price { continue; }
            let price_total = b.storage as f64 * p.price;
            let util = expected_utility(b.budget, price_total);
            if util.is_finite() {
                if let Some(ref current) = best {
                    if util > current.utility { best = Some(MatchResult { buyer_id: b.id, provider_id: p.id, accepted: true, utility: util }); }
                } else {
                    best = Some(MatchResult { buyer_id: b.id, provider_id: p.id, accepted: true, utility: util });
                }
            }
        }
        if let Some(m) = best { matches.push(m); } else { matches.push(MatchResult { buyer_id: b.id, provider_id: usize::MAX, accepted: false, utility: -100.0 }); }
    }

    let accepted: Vec<&MatchResult> = matches.iter().filter(|m| m.accepted).collect();
    let acceptance_rate = accepted.len() as f64 / matches.len() as f64;

    let out = serde_json::json!({
        "seed": seed,
        "buyers": buyers,
        "providers": providers,
        "matches": matches,
        "acceptance_rate": acceptance_rate,
    });

    fs::create_dir_all("ParametrosNao_Aleatorios/Teoria_Racional_integrada/rust/resultados")?;
    let mut f = File::create("ParametrosNao_Aleatorios/Teoria_Racional_integrada/rust/resultados/racional_resultados.json")?;
    f.write_all(serde_json::to_string_pretty(&out)?.as_bytes())?;
    println!("Resultados (racional) salvos em .../racional_resultados.json");
    Ok(())
}
