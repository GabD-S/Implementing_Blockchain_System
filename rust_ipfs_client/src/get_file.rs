use ipfs_api::IpfsClient;
use std::fs::File;
use std::io::Write;

#[tokio::main]
async fn main() {
    let client = IpfsClient::default();

    let cid = "QmExampleCid"; // Replace with the CID of the file you want to retrieve
    let output_path = "output.txt"; // Replace with the desired output file path

    match client.cat(&cid).await {
        Ok(mut stream) => {
            let mut file = File::create(output_path).expect("Failed to create output file");
            while let Some(chunk) = stream.next().await {
                match chunk {
                    Ok(data) => file.write_all(&data).expect("Failed to write to file"),
                    Err(e) => eprintln!("Error reading chunk: {}", e),
                }
            }
            println!("File retrieved successfully and saved to {}", output_path);
        }
        Err(e) => eprintln!("Error retrieving file: {}", e),
    }
}