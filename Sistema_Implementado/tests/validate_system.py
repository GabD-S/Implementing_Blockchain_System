import os
import time
import requests
import subprocess
import random
import string

# Configuração
IPFS_API = "http://127.0.0.1:5001/api/v0"
TEST_FILE_NAME = "test_file_mvp.txt"
FILE_SIZE_MB = 5

def log(msg):
    print(f"[TEST] {msg}")

def generate_file(filename, size_mb):
    log(f"Gerando arquivo de teste: {filename} ({size_mb}MB)...")
    with open(filename, "wb") as f:
        f.write(os.urandom(size_mb * 1024 * 1024))
    log("Arquivo gerado.")

def check_ipfs():
    try:
        res = requests.post(f"{IPFS_API}/id")
        if res.status_code == 200:
            log(f"IPFS Online: {res.json()['ID']}")
            return True
    except:
        pass
    log("ERRO: IPFS não está rodando. Execute 'ipfs daemon'.")
    return False

def upload_file(filename):
    log("Iniciando upload para IPFS...")
    start = time.time()
    files = {'file': open(filename, 'rb')}
    res = requests.post(f"{IPFS_API}/add", files=files)
    end = time.time()
    
    if res.status_code == 200:
        data = res.json()
        cid = data['Hash']
        log(f"Upload concluído em {end - start:.4f}s")
        log(f"CID gerado: {cid}")
        return cid
    else:
        log(f"Erro no upload: {res.text}")
        return None

def simulate_provider_pin(cid):
    log(f"Simulando ação do Provider (Pinning {cid})...")
    start = time.time()
    # Simula o comando que o provider_daemon executa
    res = requests.post(f"{IPFS_API}/pin/add?arg={cid}")
    end = time.time()
    
    if res.status_code == 200:
        log(f"Pinning concluído em {end - start:.4f}s")
        return True
    else:
        log(f"Erro no Pinning: {res.text}")
        return False

def main():
    log("=== Iniciando Validação do Sistema (MVP) ===")
    
    if not check_ipfs():
        return

    generate_file(TEST_FILE_NAME, FILE_SIZE_MB)
    
    cid = upload_file(TEST_FILE_NAME)
    if not cid:
        return

    # Simula o delay da blockchain (tempo de bloco)
    BLOCK_TIME = 2
    log(f"Aguardando tempo de bloco simulado ({BLOCK_TIME}s)...")
    time.sleep(BLOCK_TIME)

    success = simulate_provider_pin(cid)
    
    if success:
        log("=== TESTE BEM SUCEDIDO: Fluxo Completo Validado ===")
    else:
        log("=== FALHA NO TESTE ===")

    # Limpeza
    if os.path.exists(TEST_FILE_NAME):
        os.remove(TEST_FILE_NAME)

if __name__ == "__main__":
    main()
