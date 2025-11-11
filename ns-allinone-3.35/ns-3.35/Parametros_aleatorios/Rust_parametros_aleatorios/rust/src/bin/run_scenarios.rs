use simulacao_cloud_parametros_aleatorios::model::{SimConfig, Simulator};
use simulacao_cloud_parametros_aleatorios::stats::compute_stats;
use serde_json::json;
use std::fs::{self, File};
use std::io::Write;

fn main() -> anyhow::Result<()> {
    let scenarios = vec![
        ("Cenário Pequeno", 10, 5, 2, 100, 3.0),
        ("Cenário Médio", 25, 12, 4, 150, 5.0),
        ("Cenário Grande", 50, 20, 8, 200, 8.0),
        ("Cenário Intensivo", 100, 35, 15, 300, 12.0),
    ];

    let mut aggregate = serde_json::Map::new();

    for (name, nb, np, nn, time, rate) in scenarios {
        println!("==============================\nExecutando {}", name);
        let cfg = SimConfig {
            name: name.to_string(),
            num_buyers: nb,
            num_providers: np,
            num_network_agents: nn,
            simulation_time: time,
            transaction_rate: rate,
            seed: None,
        };
        let mut sim = Simulator::new(cfg.clone());
        let start = std::time::Instant::now();
        sim.run();
        let elapsed = start.elapsed().as_secs_f64();
        let stats = compute_stats(&sim);
        let mut node = serde_json::to_value(&stats)?;
        if let serde_json::Value::Object(ref mut o) = node { o.insert("execution_time".into(), json!(elapsed)); }
        aggregate.insert(name.to_string(), node);
        println!("Concluído: {:.2}s - taxa sucesso {:.2}%", stats.general.success_rate*100.0,);    }

    fs::create_dir_all("parametros_aleatorios/resultados")?;
    let mut f = File::create("parametros_aleatorios/resultados/simulation_results_detailed_rust.json")?;
    f.write_all(serde_json::to_string_pretty(&aggregate)?.as_bytes())?;
    println!("Resultados salvos em parametros_aleatorios/resultados/simulation_results_detailed_rust.json");
    Ok(())
}
