use anyhow::Result;
use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::io::Read;
use std::process::{Command, Stdio};
use std::thread;
use std::io::{BufRead, BufReader, Write};
use std::sync::Arc;
use tiny_http::{Response, Server};
use tokio::task;
use tokio::time::{sleep, Duration};

#[derive(Debug, Serialize, Deserialize)]
struct DealEvent { deal_id: u32, file_cid: String }

async fn check_ipfs_connection() -> Result<()> {
    let client = Client::new();
    let resp = client.post("http://127.0.0.1:5001/api/v0/id").send().await?;
    if resp.status().is_success() {
        println!("✅ Conectado ao IPFS local com sucesso.");
        Ok(())
    } else {
        Err(anyhow::anyhow!("Falha ao conectar ao IPFS: {}", resp.status()))
    }
}

async fn pin_ipfs(cid: &str) -> Result<()> {
    let client = Client::new();
    let url = format!("http://127.0.0.1:5001/api/v0/pin/add?arg={}", cid);
    let resp = client.post(&url).send().await?;
    if resp.status().is_success() {
        println!("✅ IPFS pin add: {}", cid);
    } else {
        eprintln!("❌ Falha ao pinar {}: {}", cid, resp.status());
    }
    Ok(())
}

#[tokio::main]
async fn main() -> Result<()> {
    println!("🚀 provider_daemon iniciado.");
    
    if let Err(e) = check_ipfs_connection().await {
        eprintln!("⚠️  Aviso: Não foi possível conectar ao IPFS. Certifique-se de que 'ipfs daemon' está rodando.");
        eprintln!("Erro: {}", e);
    }

    println!("📡 Escutando eventos do contrato (Simulação)...");

    // Inicia servidor HTTP para comandos Wormhole
    let server = Arc::new(Server::http("0.0.0.0:8088").expect("Falha ao iniciar servidor HTTP"));
    println!("🔌 HTTP server ouvindo em http://0.0.0.0:8088");

    let server_clone = server.clone();
    task::spawn(async move {
        loop {
            if let Ok(mut req) = server_clone.recv() {
                let url = req.url().to_string();
                let method = req.method().as_str().to_string();
                let mut body = String::new();
                req.as_reader().read_to_string(&mut body).ok();

                // Estrutura de resposta padrão
                #[derive(Serialize, Deserialize)]
                struct CmdResp { ok: bool, stdout: String, stderr: String }

                // Responder preflight CORS
                if method == "OPTIONS" {
                    let _ = req.respond(
                        Response::empty(204)
                            .with_header(tiny_http::Header::from_bytes(&b"Access-Control-Allow-Origin"[..], &b"*"[..]).unwrap())
                            .with_header(tiny_http::Header::from_bytes(&b"Access-Control-Allow-Headers"[..], &b"Content-Type"[..]).unwrap())
                            .with_header(tiny_http::Header::from_bytes(&b"Access-Control-Allow-Methods"[..], &b"POST, OPTIONS"[..]).unwrap()),
                    );
                    continue;
                }

                // Rota: /wormhole/send { filename }
                if method == "POST" && url == "/wormhole/send" {
                    #[derive(Deserialize)]
                    struct SendReq { filename: String }
                    let parsed: SendReq = serde_json::from_str(&body).unwrap_or(SendReq { filename: String::new() });

                    // 1) Executar wormhole send <filename> e ler stdout em tempo real
                    let mut child = match Command::new("wormhole")
                        .args(["send", &parsed.filename])
                        .stdout(Stdio::piped())
                        .stderr(Stdio::piped())
                        .spawn() {
                        Ok(ch) => ch,
                        Err(e) => {
                            let resp = CmdResp { ok: false, stdout: String::new(), stderr: format!("erro ao executar wormhole: {}", e) };
                            let json = serde_json::to_string(&resp).unwrap();
                            let _ = req.respond(
                                Response::from_string(json)
                                    .with_header(tiny_http::Header::from_bytes(&b"Content-Type"[..], &b"application/json"[..]).unwrap())
                                    .with_header(tiny_http::Header::from_bytes(&b"Access-Control-Allow-Origin"[..], &b"*"[..]).unwrap()),
                            );
                            continue;
                        }
                    };

                    let stdout = child.stdout.take().unwrap();
                    let stderr = child.stderr.take().unwrap();

                    let mut code_found: Option<String> = None;
                    let mut reader = BufReader::new(stdout);
                    let mut line = String::new();

                    // Bloqueia até encontrar o código real no stdout
                    while reader.read_line(&mut line).ok().filter(|&n| n > 0).is_some() {
                        let l = line.trim().to_string();
                        // Padrões comuns impressos pelo wormhole
                        if let Some(pos) = l.find("Wormhole code is:") {
                            let code = l[(pos + "Wormhole code is:".len())..].trim().to_string();
                            code_found = Some(code);
                            break;
                        }
                        if l.starts_with("wormhole receive ") {
                            // Algumas versões imprimem diretamente a linha de receive
                            let code = l.replace("wormhole receive ", "").trim().to_string();
                            code_found = Some(code);
                            break;
                        }
                        line.clear();
                    }

                    // Continua drenando stdout/stderr em background para não bloquear o processo
                    let mut bg_reader = reader;
                    thread::spawn(move || {
                        let mut buf = String::new();
                        while bg_reader.read_line(&mut buf).ok().filter(|&n| n > 0).is_some() {
                            // descartando
                            buf.clear();
                        }
                        let mut err_reader = BufReader::new(stderr);
                        let mut ebuf = String::new();
                        while err_reader.read_line(&mut ebuf).ok().filter(|&n| n > 0).is_some() {
                            ebuf.clear();
                        }
                    });

                    let resp_json = if let Some(code) = code_found {
                        serde_json::json!({"ok": true, "code": code})
                    } else {
                        serde_json::json!({"ok": false, "error": "codigo_nao_encontrado"})
                    };
                    let json = resp_json.to_string();
                    let _ = req.respond(
                        Response::from_string(json)
                            .with_header(tiny_http::Header::from_bytes(&b"Content-Type"[..], &b"application/json"[..]).unwrap())
                            .with_header(tiny_http::Header::from_bytes(&b"Access-Control-Allow-Origin"[..], &b"*"[..]).unwrap()),
                    );
                    continue;
                }

                // Rota: /wormhole/receive { code }
                if method == "POST" && url == "/wormhole/receive" {
                    #[derive(Deserialize)]
                    struct RecvReq { code: String }
                    let parsed: RecvReq = serde_json::from_str(&body).unwrap_or(RecvReq { code: String::new() });

                    // Executar wormhole receive <code> com auto confirmação 'y\n'
                    let mut child = match Command::new("wormhole")
                        .args(["receive", &parsed.code])
                        .stdin(Stdio::piped())
                        .stdout(Stdio::piped())
                        .stderr(Stdio::piped())
                        .spawn() {
                        Ok(ch) => ch,
                        Err(e) => {
                            let resp = CmdResp { ok: false, stdout: String::new(), stderr: format!("erro ao executar wormhole: {}", e) };
                            let json = serde_json::to_string(&resp).unwrap();
                            let _ = req.respond(
                                Response::from_string(json)
                                    .with_header(tiny_http::Header::from_bytes(&b"Content-Type"[..], &b"application/json"[..]).unwrap())
                                    .with_header(tiny_http::Header::from_bytes(&b"Access-Control-Allow-Origin"[..], &b"*"[..]).unwrap()),
                            );
                            continue;
                        }
                    };

                    if let Some(mut stdin) = child.stdin.take() {
                        let _ = stdin.write_all(b"y\n");
                    }

                    let output = child.wait_with_output();
                    let (ok, stdout, stderr) = match output {
                        Ok(out) => (
                            out.status.success(),
                            String::from_utf8_lossy(&out.stdout).to_string(),
                            String::from_utf8_lossy(&out.stderr).to_string(),
                        ),
                        Err(e) => (false, String::new(), format!("erro ao obter saida: {}", e)),
                    };

                    // Extrai caminho do arquivo recebido
                    let mut path: Option<String> = None;
                    for l in stdout.lines() {
                        if let Some(pos) = l.find("Received file written to:") {
                            let p = l[(pos + "Received file written to:".len())..].trim();
                            path = Some(p.to_string());
                            break;
                        }
                    }

                    let resp_json = serde_json::json!({
                        "ok": ok,
                        "stdout": stdout,
                        "stderr": stderr,
                        "path": path
                    });
                    let json = resp_json.to_string();
                    let _ = req.respond(
                        Response::from_string(json)
                            .with_header(tiny_http::Header::from_bytes(&b"Content-Type"[..], &b"application/json"[..]).unwrap())
                            .with_header(tiny_http::Header::from_bytes(&b"Access-Control-Allow-Origin"[..], &b"*"[..]).unwrap()),
                    );
                    continue;
                }

                // Default 404
                let _ = req.respond(
                    Response::from_string("Not Found")
                        .with_status_code(404)
                        .with_header(tiny_http::Header::from_bytes(&b"Access-Control-Allow-Origin"[..], &b"*"[..]).unwrap()),
                );
            }
        }
    });
    
    // Mock simples: em produção use subxt + metadata do contrato para eventos
    // Exemplo de fluxo real:
    // 1. Conectar ao Substrate via WS
    // 2. Subscribe em storage_market::DealCreated
    // 3. Ao receber, chamar pin_ipfs(cid)
    
    let mut id_counter = 1;
    loop {
        // Simula leitura de um novo evento de deal a cada 30 segundos
        sleep(Duration::from_secs(30)).await;

        // Use um CID real do seu IPFS local
        let evt = DealEvent {
            deal_id: id_counter,
            file_cid: "QmQQ74Jji2zeVVxLM1YSHfShaBdoKPdASLkxEg2eLh7n9H".into(),
        };
        println!("📦 [MOCK] Evento DealCreated detectado: id={}, cid={}", evt.deal_id, evt.file_cid);

        if let Err(e) = pin_ipfs(&evt.file_cid).await {
            eprintln!("Erro ao processar deal: {}", e);
        }

        id_counter += 1;
    }
}
