import React, { useState, useEffect } from 'react'
import './App.css'

interface Contract {
  id: number
  time: string
  transferCode: string
  buyerStatus: string
  networkStatus: string
  price: number
  isRealized: boolean
}

export default function App() {
  const [activeTab, setActiveTab] = useState<'send' | 'receive'>('send')
  const [wormholeCode, setWormholeCode] = useState<string>('')
  const [receiveCode, setReceiveCode] = useState<string>('')
  const [fileName, setFileName] = useState<string>('')
  const [fileSize, setFileSize] = useState<number>(0)
  const [latency, setLatency] = useState<string>('12ms')
  const [logs, setLogs] = useState<string[]>([])
  const [userIp, setUserIp] = useState<string>('Detectando IP...')
  const [balance, setBalance] = useState<number>(1000000)
  const [contracts, setContracts] = useState<Contract[]>([])

  const addLog = (msg: string) =>
    setLogs(prev => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev])

  useEffect(() => {
    fetch('https://api.ipify.org?format=json')
      .then(r => r.json())
      .then(d => {
        setUserIp(d.ip)
        addLog(`IP detectado: ${d.ip}`)
      })
      .catch(() => {
        setUserIp('127.0.0.1')
        addLog('IP local usado')
      })

    const savedContracts = localStorage.getItem('storage_contracts_db')
    if (savedContracts) setContracts(JSON.parse(savedContracts))

    const savedBalance = localStorage.getItem('storage_balance')
    if (savedBalance) setBalance(Number(savedBalance))
  }, [])

  useEffect(() => {
    const i = setInterval(() => {
      let base = 20 + (fileSize / 1024 / 1024) * 5
      setLatency(`${Math.floor(base + Math.random() * 10)}ms`)
    }, 2000)
    return () => clearInterval(i)
  }, [fileSize])

  function onUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0]
    if (!f) return
    setFileName(f.name)
    setFileSize(f.size)
    setWormholeCode('')
    addLog(`Arquivo selecionado: ${f.name}`)
  }

  async function handleCreateDeal() {
    if (!fileName) return alert('Selecione um arquivo')

    const cost = Math.floor(10 + fileSize / (1024 * 1024))
    if (balance < cost) return alert('Saldo insuficiente')

    addLog('Iniciando wormhole send...')
    const r = await fetch('http://127.0.0.1:8088/wormhole/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename: fileName })
    })
    const data = await r.json()

    if (!data.ok) return alert('Falha no envio')

    setWormholeCode(data.code)

    const newBalance = balance - cost
    setBalance(newBalance)
    localStorage.setItem('storage_balance', newBalance.toString())

    const c: Contract = {
      id: Date.now(),
      time: new Date().toLocaleString(),
      transferCode: data.code,
      buyerStatus: 'Local',
      networkStatus: 'Estável',
      price: cost,
      isRealized: true
    }

    const updated = [c, ...contracts]
    setContracts(updated)
    localStorage.setItem('storage_contracts_db', JSON.stringify(updated))

    addLog(`Código wormhole: ${data.code}`)
  }

  async function handleReceive() {
    if (!receiveCode) return alert('Digite o código')

    addLog(`Recebendo arquivo com código ${receiveCode}`)
    const r = await fetch('http://127.0.0.1:8088/wormhole/receive', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: receiveCode })
    })
    const d = await r.json()

    if (d.ok) alert('Arquivo recebido com sucesso')
    else alert('Erro ao receber arquivo')
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>📦 Storage DApp (Wormhole)</h1>
        <p>IP: <b>{userIp}</b> | Latência: <b>{latency}</b></p>
        <p>Saldo: <b>{balance} UNIT</b></p>
      </header>

      <div className="tabs">
        <button onClick={() => setActiveTab('send')}>Enviar</button>
        <button onClick={() => setActiveTab('receive')}>Receber</button>
      </div>

      {activeTab === 'send' ? (
        <>
          <input type="file" onChange={onUpload} />
          <button onClick={handleCreateDeal}>Enviar Arquivo</button>

          {wormholeCode && (
            <div>
              <p>Código Wormhole:</p>
              <code>wormhole receive {wormholeCode}</code>
            </div>
          )}
        </>
      ) : (
        <>
          <input
            placeholder="código wormhole"
            value={receiveCode}
            onChange={e => setReceiveCode(e.target.value)}
          />
          <button onClick={handleReceive}>Receber</button>
        </>
      )}

      <div className="terminal-logs">
        {logs.map((l, i) => <div key={i}>{l}</div>)}
      </div>
    </div>
  )
}
