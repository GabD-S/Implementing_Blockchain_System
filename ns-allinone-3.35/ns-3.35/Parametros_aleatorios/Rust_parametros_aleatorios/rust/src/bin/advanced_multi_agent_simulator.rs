use simulacao_cloud_parametros_aleatorios::model::{SimConfig, Simulator};
use simulacao_cloud_parametros_aleatorios::stats::compute_stats;
use std::fs::{self, File};
use std::io::Write;

fn main() -> anyhow::Result<()> {
    let cfg = SimConfig {
        name: "Copia Simples".into(),
        num_buyers: 10,
        num_providers: 5,
        num_network_agents: 2,
        simulation_time: 50,
        transaction_rate: 3.0,
        seed: Some(42),
    };

    let mut sim = Simulator::new(cfg);
    sim.run();
    let stats = compute_stats(&sim);
    let json = serde_json::to_string_pretty(&stats)?;

    fs::create_dir_all("parametros_aleatorios/resultados")?;
    let mut f = File::create("parametros_aleatorios/resultados/simulation_results_detailed_rust_single.json")?;
    f.write_all(json.as_bytes())?;

    println!("Resultados salvos em parametros_aleatorios/resultados/simulation_results_detailed_rust_single.json");
    Ok(())
}
