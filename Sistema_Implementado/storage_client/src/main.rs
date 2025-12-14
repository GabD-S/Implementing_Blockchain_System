use anyhow::Result;
use blake2::{Blake2b512, Digest};
use parity_scale_codec::Encode;
use subxt::{OnlineClient, PolkadotConfig};
use subxt_signer::sr25519::dev;
use subxt::utils::{AccountId32, MultiAddress};
use subxt::ext::scale_value::Value;

// Gas limits altos para ambiente dev
const GAS_LIMIT_REF_TIME: u64 = 100_000_000_000;
const GAS_LIMIT_PROOF_SIZE: u64 = 3_000_000;

// Calcula o seletor ink! (4 primeiros bytes do Blake2b)
fn get_selector(sig: &str) -> [u8; 4] {
    let mut hasher = Blake2b512::new();
    hasher.update(sig.as_bytes());
    let result = hasher.finalize();
    let mut selector = [0u8; 4];
    selector.copy_from_slice(&result[0..4]);
    println!("🔧 Seletor '{}': 0x{}", sig, hex::encode(selector));
    selector
}

#[tokio::main]
async fn main() -> Result<()> {
    println!("🚀 Iniciando Storage Client");

    // 1. Conexão com nó local
    let api = OnlineClient::<PolkadotConfig>::from_url("ws://127.0.0.1:9944").await?;
    println!("✅ Conectado ao nó local");

    // 2. Signer (Alice)
    let signer = dev::alice();
    let signer_id = signer.public_key().to_account_id();
    println!("👤 Usando Alice: {:?}", signer_id);

    // 3. ENDEREÇO DO CONTRATO (SUBSTITUA PELO REAL)
    let contract_addr_str = "5DfDUsaL2bSaQ9utkvWDc6Ko8Wb7DonTtCgVnAVK9hpvFRiy";
    let contract_id: AccountId32 = contract_addr_str.parse()?;
    let dest = MultiAddress::Id(contract_id.clone());

    // ================================
    // 1️⃣ register_provider
    // ================================
    println!("\n📦 register_provider");

    let selector = get_selector("register_provider");
    let capacity: u64 = 1000;
    let price: u128 = 10;

    let mut data = Vec::new();
    data.extend_from_slice(&selector);
    capacity.encode_to(&mut data);
    price.encode_to(&mut data);

    let tx_register = subxt::dynamic::tx(
        "Contracts",
        "call",
        vec![
            Value::bytes(dest.encode()),              // dest
            Value::u128(0),                            // value
            Value::named_composite(vec![               // gas_limit
                ("ref_time", Value::u128(GAS_LIMIT_REF_TIME as u128)),
                ("proof_size", Value::u128(GAS_LIMIT_PROOF_SIZE as u128)),
            ]),
            Value::variant("None", vec![]),            // storage_deposit_limit
            Value::bytes(data),                        // data
        ],
    );

    let events = api
        .tx()
        .sign_and_submit_then_watch(&tx_register, &signer, Default::default())
        .await?
        .wait_for_finalized_success()
        .await?;

    println!(
        "✅ register_provider incluído. Extrinsic hash: {:?}",
        events.extrinsic_hash()
    );

    // ================================
    // 2️⃣ create_deal
    // ================================
    println!("\n📦 create_deal");

    let selector = get_selector("create_deal");
    let provider = signer_id.clone();
    let file_cid = "QmTestCid123456789";
    let size: u64 = 500;
    let duration: u64 = 30 * 24 * 60 * 60;

    let mut data = Vec::new();
    data.extend_from_slice(&selector);
    provider.encode_to(&mut data);
    file_cid.encode_to(&mut data);
    size.encode_to(&mut data);
    duration.encode_to(&mut data);

    let value: u128 = 1_000;

    let tx_deal = subxt::dynamic::tx(
        "Contracts",
        "call",
        vec![
            Value::bytes(dest.encode()),              // dest
            Value::u128(value),                        // value
            Value::named_composite(vec![
                ("ref_time", Value::u128(GAS_LIMIT_REF_TIME as u128)),
                ("proof_size", Value::u128(GAS_LIMIT_PROOF_SIZE as u128)),
            ]),
            Value::variant("None", vec![]),
            Value::bytes(data),
        ],
    );

    let events = api
        .tx()
        .sign_and_submit_then_watch(&tx_deal, &signer, Default::default())
        .await?
        .wait_for_finalized_success()
        .await?;

    println!(
        "✅ create_deal incluído. Extrinsic hash: {:?}",
        events.extrinsic_hash()
    );

    println!("\n🎉 Integração concluída com sucesso");
    Ok(())
}
