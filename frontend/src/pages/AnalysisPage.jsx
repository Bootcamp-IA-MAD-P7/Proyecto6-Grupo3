// ============================================================
//  AnalysisPage.jsx — Página de resultado ("radiografía")
// ------------------------------------------------------------
//  ESTADO: ESQUELETO funcional (FASE 2 del roadmap).
//
//  QUÉ HARÁ: mostrar el análisis completo de una política:
//   · Resumen de la IA en lenguaje llano (turquesa)
//   · Categorías detectadas con % de cobertura
//   · Evidencias literales del documento (ámbar)
//   · Artículos del RGPD relacionados
//   · Botón "Ver en el documento" (usa paragraph_index.json
//     del backend para localizar el párrafo exacto)
//
//  AHORA MISMO: recibe la URL por el estado de la ruta,
//  llama al servicio (mock) y pinta una versión preliminar
//  reutilizando los componentes ya construidos.
// ============================================================
import { useEffect, useState } from 'react'
import { useLocation, Link } from 'react-router-dom'
import AnalysisPreviewCard from '../components/ui/AnalysisPreviewCard'
import { analyzeUrl } from '../services/analysisService'
import './AnalysisPage.css'

export default function AnalysisPage() {
  // La home nos pasa la URL elegida por el usuario aquí
  const { state } = useLocation()
  const requestedUrl = state?.url ?? null

  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(Boolean(requestedUrl))
  const [error, setError] = useState('')

  useEffect(() => {
    if (!requestedUrl) return
    setAnalysis(null)
    setError('')
    setLoading(true)
    analyzeUrl(requestedUrl)
      .then(setAnalysis)
      .catch((requestError) => {
        setError(
          requestError instanceof Error
            ? requestError.message
            : 'No se ha podido completar el análisis.',
        )
      })
      .finally(() => setLoading(false))
  }, [requestedUrl])

  return (
    <section className="analysis-page container">
      <Link to="/" className="analysis-page__back">← Nuevo análisis</Link>

      <h1 className="analysis-page__title">Radiografía de la política</h1>

      {/* Estados de la página: sin URL / cargando / resultado */}
      {!requestedUrl && (
        <p className="analysis-page__note">
          No hay ninguna URL que analizar. Vuelve al inicio y pega una política de privacidad.
        </p>
      )}
      {loading && <p className="analysis-page__note">Analizando {requestedUrl}…</p>}
      {!loading && error && (
        <div className="analysis-page__error" role="alert">
          <strong>No se pudo analizar la política.</strong>
          <p>{error}</p>
        </div>
      )}
      {!loading && !error && analysis && <AnalysisPreviewCard analysis={analysis} />}
    </section>
  )
}
