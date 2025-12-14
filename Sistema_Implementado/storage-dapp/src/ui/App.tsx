import React, { useEffect, useState } from 'react'
import './App.css'
import {
  Contract,
  calculatePrice,
  generateTempCode,
  createContract,
  saveContracts,
  saveBalance
} from '../contractController'

export default function App() {
  const [activeTab, setActiveTab] = useState<'send' | 'receive'>('send')
  const [wormholeCode, setWormholeCode] = useState('')
  const [receiveCode, setReceiveCode] = useState('')
  const [fileName, setFileName] = useState('')
  const [fileSize, setFileSize] = useState(0)
  const [latency, setLatency] = useState('12ms')
  const [logs, setLogs] = useState<string[]>([])
  const [userIp, setUserIp] = useState('Detectando IP...')
  const [balance, setBalance] = useState(1_000_000)
  const [contracts, setContracts] = useState<Contract[]>([])

  const addLog = (msg: string) =>
    setLogs(prev => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev])

  // ===== SSE =====
  useEffect(() => {
    try {
      const es = new EventSource('http://127.0.0.1:8088/wormhole/logs')
      es.onmessage = e => addLog(e.data)
      es.onerror = () => {
        // Silencioso - servidor pode não estar rodando
      }
      return () => es.close()
    } catch (err) {
      // Silencioso
    }
  }, [])

  // ===== Init =====
  useEffect(() => {
    fetch('https://api.ipify.org?format=json')
      .then(r => r.json())
      .then(d => setUserIp(d.ip))
      .catch(() => setUserIp('127.0.0.1'))

    const c = localStorage.getItem('storage_contracts_db')
    if (c) {
      try {
        setContracts(JSON.parse(c))
      } catch (err) {
        addLog('⚠️ Erro ao carregar contratos')
      }
    }

    const b = localStorage.getItem('storage_balance')
    if (b) setBalance(Number(b))
  }, [])

  // ===== Latência simulada =====
  useEffect(() => {
    const i = setInterval(() => {
      const base = 20 + (fileSize / 1024 / 1024) * 5
      setLatency(`${Math.floor(base + Math.random() * 10)}ms`)
    }, 2000)
    return () => clearInterval(i)
  }, [fileSize])

  // ===== Salvar contratos e saldo quando mudarem =====
  useEffect(() => {
    if (contracts.length > 0) {
      saveContracts(contracts)
    }
  }, [contracts])

  useEffect(() => {
    saveBalance(balance)
  }, [balance])

  function onUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0]
    if (!f) return
    setFileName(f.name)
    setFileSize(f.size)
    setWormholeCode('')
    addLog(`📄 Arquivo preparado: ${f.name} (${(f.size / 1024).toFixed(2)} KB)`)
    
    const price = calculatePrice(f.size)
    addLog(`💰 Custo estimado: ${price} UNIT`)
  }

  async function handleSend() {
    if (!fileName) {
      addLog('⚠️ Nenhum arquivo selecionado')
      return
    }

    const price = calculatePrice(fileSize)
    
    if (balance < price) {
      addLog('❌ Saldo insuficiente')
      return
    }

    addLog('🚀 Iniciando transferência...')

    // Criar contrato e código
    const code = generateTempCode()
    setWormholeCode(code)
    
    const newContract = createContract(fileSize)
    newContract.transferCode = code
    
    // Adicionar contrato e atualizar saldo IMEDIATAMENTE
    setContracts(prev => [newContract, ...prev])
    setBalance(prev => prev - price)
    
    addLog(`✅ Wormhole criado: ${code}`)
    addLog(`💸 Débito: ${price} UNIT`)
    addLog(`💰 Saldo atual: ${(balance - price).toLocaleString()} UNIT`)

    // Tentar comunicar com servidor em segundo plano
    try {
      await fetch('http://127.0.0.1:8088/wormhole/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: fileName, code: code })
      })
    } catch (err) {
      // Silencioso - já criamos localmente
    }
  }

  async function handleReceive() {
    if (!receiveCode.trim()) {
      addLog('⚠️ Digite um código wormhole')
      return
    }

    addLog(`📥 Buscando arquivo com código: ${receiveCode}`)

    // Marcar contrato como realizado IMEDIATAMENTE
    setContracts(prev =>
      prev.map(c =>
        c.transferCode === receiveCode
          ? { ...c, isRealized: true }
          : c
      )
    )
    
    addLog('✅ Download iniciado')
    setReceiveCode('')

    // Tentar comunicar com servidor em segundo plano
    try {
      await fetch('http://127.0.0.1:8088/wormhole/receive', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: receiveCode })
      })
    } catch (err) {
      // Silencioso - já marcamos como realizado localmente
    }
  }

  function handleContractClick(contract: Contract) {
    if (!contract.isRealized && activeTab !== 'receive') {
      setActiveTab('receive')
      setReceiveCode(contract.transferCode)
      addLog(`📋 Código copiado: ${contract.transferCode}`)
    }
  }

  return (
    <div className="app-container">
      {/* ===== HEADER ===== */}
      <header className="app-header">
        <div className="header-left">
          <h1>📦 Mercado de Armazenamento Descentralizado</h1>
          <p>Conectado ao nó local: <b>{userIp}</b></p>
        </div>

        <div className="app-status">
          <div className="status-item">
            <span className="status-dot"></span>
            Latência: <b>{latency}</b>
          </div>
          <div className="status-item balance">
            <span className="coin-icon">●</span>
            <b>{balance.toLocaleString()} UNIT</b>
          </div>
        </div>
      </header>

      {/* ===== GRID ===== */}
      <div className="main-grid">
        {/* ===== LEFT PANEL ===== */}
        <div className="card left-panel">
          <div className="tabs">
            <button className={activeTab === 'send' ? 'active' : ''} onClick={() => setActiveTab('send')}>
              📤 Enviar
            </button>
            <button className={activeTab === 'receive' ? 'active' : ''} onClick={() => setActiveTab('receive')}>
              📥 Receber
            </button>
          </div>

          {activeTab === 'send' ? (
            <>
              <h2>📤 Envio de Arquivo</h2>

              <div className="upload-area">
                <input type="file" id="file" onChange={onUpload} hidden />
                <label htmlFor="file" className="file-label">
                  {fileName ? `📄 ${fileName}` : 'Selecionar arquivo'}
                </label>
                {fileSize > 0 && (
                  <div style={{ marginTop: '12px', fontSize: '14px', color: '#a0a0b0', textAlign: 'center' }}>
                    Tamanho: <b>{(fileSize / 1024).toFixed(2)} KB</b> • Custo: <b>{calculatePrice(fileSize)} UNIT</b>
                  </div>
                )}
              </div>

              <button 
                className={`action-button ${fileName ? 'active' : 'disabled'}`} 
                onClick={handleSend}
                disabled={!fileName}
              >
                🚀 Iniciar Wormhole
              </button>

              {wormholeCode && (
                <div className="wormhole-box">
                  <h3>🔐 Código Wormhole</h3>
                  <code className="wormhole-code">{wormholeCode}</code>
                  <code className="terminal-command">
                    wormhole receive {wormholeCode}
                  </code>
                  <p style={{ marginTop: '12px', fontSize: '13px', color: '#a0a0b0', textAlign: 'center' }}>
                    Compartilhe este código com o destinatário
                  </p>
                </div>
              )}
            </>
          ) : (
            <>
              <h2>📥 Recebimento</h2>
              <input
                className="code-input"
                placeholder="Digite o código wormhole"
                value={receiveCode}
                onChange={e => setReceiveCode(e.target.value)}
                onKeyPress={e => e.key === 'Enter' && handleReceive()}
              />
              <button 
                className={`action-button ${receiveCode.trim() ? 'active' : 'disabled'}`} 
                onClick={handleReceive}
                disabled={!receiveCode.trim()}
              >
                ⬇️ Baixar Arquivo
              </button>
              <p style={{ marginTop: '16px', fontSize: '13px', color: '#a0a0b0', textAlign: 'center' }}>
                Cole o código que você recebeu e pressione Enter ou clique em Baixar
              </p>
            </>
          )}
        </div>

        {/* ===== RIGHT PANEL ===== */}
        <div className="right-panel">
          {/* ===== CONTRACTS ===== */}
          <div className="card">
            <h2>📜 Contratos ({contracts.length})</h2>

            {contracts.length === 0 ? (
              <p className="empty-state">Nenhum contrato ainda. Envie um arquivo para criar seu primeiro contrato!</p>
            ) : (
              <div className="table-container">
                <table className="contracts-table">
                  <thead>
                    <tr>
                      <th>Hora</th>
                      <th>Código</th>
                      <th>Rede</th>
                      <th>Preço</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {contracts.map(c => (
                      <tr 
                        key={c.id} 
                        onClick={() => handleContractClick(c)}
                        style={{ cursor: c.isRealized ? 'default' : 'pointer' }}
                      >
                        <td>{c.time.split(' ')[1]}</td>
                        <td><code>{c.transferCode}</code></td>
                        <td>{c.networkStatus}</td>
                        <td>{c.price} UNIT</td>
                        <td>
                          <span className={`status-badge ${c.isRealized ? 'active' : ''}`}>
                            {c.isRealized ? '✓ Realizado' : '⏳ Pendente'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* ===== TERMINAL ===== */}
          <div className="terminal-logs">
            <div className="terminal-header">
              <span className="terminal-title">🖥️ Terminal</span>
              <div className="terminal-controls">
                <span className="control-dot red"></span>
                <span className="control-dot yellow"></span>
                <span className="control-dot green"></span>
              </div>
            </div>
            <div className="logs-content">
              {logs.length === 0 ? (
                <div className="log-line empty">Aguardando eventos...</div>
              ) : (
                logs.map((l, i) => (
                  <div key={i} className="log-line">{l}</div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}