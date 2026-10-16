import { spawn, spawnSync, type ChildProcess } from 'node:child_process'
import { existsSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import type { Plugin } from 'vite'

const backend = fileURLToPath(new URL('../../backend/', import.meta.url))
const python = fileURLToPath(new URL(process.platform === 'win32'
  ? '../../backend/.venv/Scripts/python.exe'
  : '../../backend/.venv/bin/python', import.meta.url))
const healthUrl = 'http://127.0.0.1:8000/api/health'

async function health(): Promise<'ready' | 'stale' | 'other' | 'offline'> {
  try {
    const response = await fetch(healthUrl, { signal: AbortSignal.timeout(600) })
    if (!response.ok) return 'other'
    const data = await response.json() as { backend?: string; database?: string; api_version?: number }
    if (data.backend !== 'python-fastapi' || data.database !== 'sqlite') return 'other'
    return data.api_version === 5 ? 'ready' : 'stale'
  } catch { return 'offline' }
}

// Vite owns its Python process. An already-running compatible API is reused.
export function pythonApi(): Plugin {
  let child: ChildProcess | undefined
  const stop = () => {
    // Stop only this instance's process tree, including the Windows launcher
    // and Uvicorn reload worker. Never stop a reused external API.
    if (child?.pid && child.exitCode === null) {
      if (process.platform === 'win32') spawnSync('taskkill', ['/PID', String(child.pid), '/T', '/F'], { windowsHide: true, stdio: 'ignore' })
      else child.kill()
    }
    child = undefined
  }
  async function start() {
    const current = await health()
    if (current === 'ready') return
    if (current === 'stale') throw new Error('Hay una API antigua de Reviews en el puerto 8000. Cierra su terminal y vuelve a iniciar npm run dev.')
    if (current === 'other') throw new Error('El puerto 8000 está ocupado por otra aplicación. Libéralo antes de iniciar Aftercredits.')
    if (!existsSync(python)) throw new Error('Falta backend/.venv. Sigue la preparación Python en backend/README.md.')
    child = spawn(python, ['run.py'], {
      cwd: backend, stdio: 'inherit', windowsHide: true,
      env: { ...process.env, PORT: '8000', PYTHONUNBUFFERED: '1', AFTERCREDITS_RELOAD: '1' },
    })
    let failure: string | undefined
    child.once('error', error => { failure = error.message })
    child.once('exit', code => { failure = `Python terminó con código ${code}. Revisa el error anterior.` })
    const deadline = Date.now() + 15000
    while (Date.now() < deadline) {
      if (await health() === 'ready') {
        console.log('API Python lista en http://127.0.0.1:8000')
        return
      }
      if (failure) { stop(); throw new Error(failure) }
      await new Promise(resolve => setTimeout(resolve, 150))
    }
    stop()
    throw new Error('Python no inició en 15 segundos. Revisa la salida de la API en esta terminal.')
  }
  return {
    name: 'aftercredits-python-api',
    async configureServer(server) {
      server.httpServer?.once('close', stop)
      await start()
    },
    async configurePreviewServer(server) {
      server.httpServer.once('close', stop)
      await start()
    },
  }
}
