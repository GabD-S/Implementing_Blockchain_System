export interface Contract {
  id: number
  time: string
  transferCode: string
  buyerStatus: string
  networkStatus: string
  price: number
  isRealized: boolean
}

// ===== Cálculo de custo =====
export function calculatePrice(fileSize: number): number {
  return Math.floor(10 + fileSize / (1024 * 1024))
}

// ===== Código temporário =====
export function generateTempCode(): string {
  const words = ['alpha', 'nebula', 'delta', 'orbit', 'crypto', 'node']
  const a = Math.floor(Math.random() * 100)
  const b = words[Math.floor(Math.random() * words.length)]
  const c = words[Math.floor(Math.random() * words.length)]
  return `${a}-${b}-${c}`
}

// ===== Criar contrato =====
export function createContract(fileSize: number): Contract {
  return {
    id: Date.now(),
    time: new Date().toLocaleString(),
    transferCode: generateTempCode(),
    buyerStatus: 'Local',
    networkStatus: 'Estável',
    price: calculatePrice(fileSize),
    isRealized: false
  }
}

// ===== Persistência =====
export function saveContracts(contracts: Contract[]) {
  localStorage.setItem('storage_contracts_db', JSON.stringify(contracts))
}

export function saveBalance(balance: number) {
  localStorage.setItem('storage_balance', balance.toString())
}
