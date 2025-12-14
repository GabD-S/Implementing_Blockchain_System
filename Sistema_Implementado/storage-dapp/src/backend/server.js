import express from 'express'
import cors from 'cors'
import { spawn } from 'child_process'
import path from 'path'
import { fileURLToPath } from 'url'
import fs from 'fs'

// ===== Configuração de paths =====
const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// Pasta correta dos arquivos
const FILES_DIR = path.join(__dirname, 'files')

// ===== App =====
const app = express()
app.use(cors())
app.use(express.json())

// ================================
// SEND
// ================================
app.post('/wormhole/send', (req, res) => {
  const { filename } = req.body
  if (!filename) {
    return res.json({ ok: false, error: 'filename ausente' })
  }

  const fullPath = path.join(FILES_DIR, filename)

  if (!fs.existsSync(fullPath)) {
    return res.json({
      ok: false,
      error: `Arquivo não encontrado: ${filename}`
    })
  }

  console.log(`📤 Enviando arquivo: ${fullPath}`)

  const proc = spawn('wormhole', ['send', fullPath])

  let codeSent = false

  proc.stdout.on('data', data => {
    const text = data.toString()
    console.log(text)

    // Captura o código real do wormhole
    const match = text.match(/wormhole receive\s+([^\s]+)/)

    if (match && !codeSent) {
      codeSent = true
      const code = match[1].trim()

      console.log(`✅ Código Wormhole capturado: ${code}`)

      res.json({
        ok: true,
        code
      })
    }
  })

  proc.stderr.on('data', data => {
    console.error('wormhole stderr:', data.toString())
  })

  proc.on('close', code => {
    console.log(`wormhole send finalizado (${code})`)
  })
})

// ================================
// RECEIVE
// ================================
app.post('/wormhole/receive', (req, res) => {
  const { code } = req.body
  if (!code) {
    return res.json({ ok: false, error: 'code ausente' })
  }

  console.log(`📥 Recebendo com código: ${code}`)

  const proc = spawn('wormhole', ['receive', code])

  proc.stdout.on('data', data => {
    const text = data.toString()
    console.log(text)

    // Confirma automaticamente o download
    if (text.toLowerCase().includes('ok?')) {
      proc.stdin.write('y\n')
    }
  })

  proc.stderr.on('data', data => {
    console.error('wormhole stderr:', data.toString())
  })

  proc.on('close', () => {
    res.json({ ok: true })
  })
})

// ================================
app.listen(8088, () => {
  console.log('🚀 Wormhole backend em http://127.0.0.1:8088')
  console.log(`📂 Pasta de arquivos: ${FILES_DIR}`)
})
