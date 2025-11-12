use ipfs_api::IpfsClient;
use std::fs::File;
use std::io::BufReader;

#[tokio::main]
async fn main() {
    let client = IpfsClient::default();

    let file_path = "example.txt"; // Replace with the path to your file
    let file = File::open(file_path).expect("Failed to open file");
    let reader = BufReader::new(file);

    match client.add(reader).await {
        Ok(response) => println!("File added successfully. CID: {}", response.hash),
        Err(e) => eprintln!("Error adding file: {}", e),
    }
}