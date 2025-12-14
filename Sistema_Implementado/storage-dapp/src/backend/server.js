import express from 'express'
import cors from 'cors'
import { spawn } from 'child_process'
import path from 'path'
import { fileURLToPath } from 'url'
import fs from 'fs'

// ===== Paths =====
const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const FILES_DIR = path.join(__dirname, 'files')

// ===== App =====
const app = express()
app.use(cors())
app.use(express.json())

// ===== SSE Clients =====
let sseClients = []

function broadcast(msg) {
  sseClients.forEach(res => {
    res.write(`data: ${msg.replace(/\n/g, '')}\n\n`)
  })
}

// ===== SSE Endpoint =====
app.get('/wormhole/logs', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream')
  res.setHeader('Cache-Control', 'no-cache')
  res.setHeader('Connection', 'keep-alive')
  res.flushHeaders()

  sseClients.push(res)

  req.on('close', () => {
    sseClients = sseClients.filter(c => c !== res)
  })
})

// ================================
// SEND
// ================================
app.post('/wormhole/send', (req, res) => {
  const { filename } = req.body
  if (!filename) return res.json({ ok: false, error: 'filename ausente' })

  const fullPath = path.join(FILES_DIR, filename)
  if (!fs.existsSync(fullPath)) {
    return res.json({ ok: false, error: 'Arquivo não encontrado' })
  }

  broadcast(`📤 Enviando: ${filename}`)

  const proc = spawn('wormhole', ['send', fullPath])
  let responded = false

  proc.stdout.on('data', data => {
    const text = data.toString()
    console.log(text)
    broadcast(text)

    const match = text.match(/wormhole receive\s+([^\s]+)/)
    if (match && !responded) {
      responded = true
      res.json({ ok: true, code: match[1].trim() })
    }
  })

  proc.stderr.on('data', data => {
    console.error(data.toString())
    broadcast(`❌ ${data.toString()}`)
  })
})

// ================================
// RECEIVE
// ================================
app.post('/wormhole/receive', (req, res) => {
  const { code } = req.body
  if (!code) return res.json({ ok: false })

  broadcast(`📥 Recebendo com código ${code}`)

  const proc = spawn('wormhole', ['receive', code])

  proc.stdout.on('data', data => {
    const text = data.toString()
    console.log(text)
    broadcast(text)

    if (text.toLowerCase().includes('ok?')) {
      proc.stdin.write('y\n')
    }
  })

  proc.stderr.on('data', data => {
    console.error(data.toString())
    broadcast(`❌ ${data.toString()}`)
  })

  proc.on('close', () => {
    broadcast('✅ Transferência finalizada')
    res.json({ ok: true })
  })
})

// ===== Start =====
app.listen(8088, () => {
  console.log('🚀 Wormhole backend em http://127.0.0.1:8088')
  console.log(`📂 Pasta de arquivos: ${FILES_DIR}`)
})
