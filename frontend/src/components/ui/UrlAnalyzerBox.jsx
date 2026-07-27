// ============================================================
//  UrlAnalyzerBox.jsx — LA pieza protagonista del producto
// ------------------------------------------------------------
//  QUÉ HACE: la caja donde el usuario pega una URL para
//  analizar su política de privacidad. Es el corazón de la
//  home (patrón "el buscador ES la página").
//
//  PROPS:
//   · onAnalyze(url) — callback que se ejecuta al enviar.
//     La página decide qué hacer (navegar a /analisis, etc.)
//
//  ESTADO: guarda el texto del input y si está analizando.
//  El botón se desactiva mientras "piensa".
//
//  NOTA EXTENSIÓN: este mismo componente se reutilizará en el
//  popup de la extensión de Chrome (mismo comportamiento,
//  estilos adaptados al ancho del popup).
// ============================================================
import { useState } from 'react'
import './UrlAnalyzerBox.css'

export default function UrlAnalyzerBox({ onAnalyze }) {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    const clean = url.trim()
    if (!clean || loading) return
    setLoading(true)
    try {
      await onAnalyze?.(clean)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className="urlbox" onSubmit={handleSubmit}>
      {/* Icono de globo (decorativo) */}
      <svg className="urlbox__icon" width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" strokeWidth="2" aria-hidden="true">
        <circle cx="12" cy="12" r="10" />
        <path d="M2 12h20M12 2a15.3 15.3 0 0 1 0 20 15.3 15.3 0 0 1 0-20z" />
      </svg>

      <input
        className="urlbox__input"
        type="text"
        inputMode="url"
        placeholder="https://empresa.com/politica-de-privacidad"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        aria-label="URL de la política de privacidad a analizar"
      />

      <button className="urlbox__button" type="submit" disabled={loading}>
        {loading ? 'Analizando…' : 'Analizar'}
      </button>
    </form>
  )
}
