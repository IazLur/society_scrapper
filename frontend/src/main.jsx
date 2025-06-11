import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

async function loadConfig() {
  try {
    const resp = await fetch('/config.json')
    if (resp.ok) {
      window.CONFIG = await resp.json()
      return
    }
  } catch (e) {
    // ignore and use defaults
  }
  window.CONFIG = { API_URL: 'http://127.0.0.1:5000' }
}

loadConfig().then(() => {
  createRoot(document.getElementById('root')).render(
    <StrictMode>
      <App />
    </StrictMode>,
  )
})
