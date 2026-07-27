// ============================================================
//  HomePage.jsx — Página principal (el analizador)
// ------------------------------------------------------------
//  QUÉ HACE: la landing de PrivacyLens. Estructura:
//   1. Hero: titular + caja de URL protagonista
//   2. Tarjeta flotante con un análisis de ejemplo
//   3. Métricas del corpus/modelo (StatCards)
//   4. Análisis recientes
//
//  DATOS: todo llega a través de analysisService (mock por
//  ahora, API real cuando el backend esté listo — ver
//  src/services/analysisService.js).
// ============================================================
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import UrlAnalyzerBox from '../components/ui/UrlAnalyzerBox'
import AnalysisPreviewCard from '../components/ui/AnalysisPreviewCard'
import StatCard from '../components/ui/StatCard'
import RecentAnalyses from '../components/ui/RecentAnalyses'
import { analyzeUrl, getRecentAnalyses, getGlobalStats } from '../services/analysisService'
import './HomePage.css'

// Orden de colores de los filetes de las tarjetas de métricas
const STAT_TONES = ['primary', 'secondary', 'accent', 'amber']

export default function HomePage() {
  const navigate = useNavigate()

  // Estado: datos que vienen del servicio (mock o API)
  const [preview, setPreview] = useState(null)
  const [recent, setRecent] = useState([])
  const [stats, setStats] = useState([])

  // Al montar la página, cargamos los datos de ejemplo
  useEffect(() => {
    getRecentAnalyses().then(setRecent)
    getGlobalStats().then(setStats)
    analyzeUrl('https://spotify.com/legal/privacy-policy').then(setPreview)
  }, [])

  // Cuando el usuario pulsa "Analizar" navegamos a la página
  // de resultado pasando la URL en el estado de la ruta.
  const handleAnalyze = async (url) => {
    navigate('/analisis', { state: { url } })
  }

  return (
    <>
      {/* ---------- HERO ---------- */}
      <section className="hero container">
        <div className="hero__content">
          <span className="hero__badge">
            <span className="hero__badge-dot" />
            Legal AI · Alineado con el RGPD
          </span>

          <h1 className="hero__title">
            Entiende cualquier
            <br />
            política de <span className="hero__title-grad">privacidad.</span>
          </h1>

          <p className="hero__sub">
            Pega una URL y nuestra IA traduce el documento legal a un lenguaje que cualquier
            persona puede entender. Con evidencias, sin jerga y sin alarmismos.
          </p>

          {/* La caja protagonista: al analizar navega a /analisis */}
          <UrlAnalyzerBox onAnalyze={handleAnalyze} />

          <p className="hero__alt">
            ¿Sin URL? <a href="#texto">Pega el texto de la política directamente →</a>
          </p>

          <div className="hero__trust">
            <div><b>1.247</b> políticas analizadas</div>
            <div><b>10</b> categorías detectadas</div>
            <div><b>6</b> idiomas</div>
          </div>
        </div>

        {/* Tarjeta flotante con el análisis de ejemplo */}
        <AnalysisPreviewCard analysis={preview} />
      </section>

      {/* ---------- MÉTRICAS DEL CORPUS / MODELO ---------- */}
      <section className="stats container">
        {stats.map((s, i) => (
          <StatCard key={s.label} value={s.value} label={s.label} tone={STAT_TONES[i % 4]} />
        ))}
      </section>

      {/* ---------- ANÁLISIS RECIENTES ---------- */}
      <RecentAnalyses
        items={recent}
        onSelect={(slug) => navigate(`/analisis`, { state: { slug } })}
      />
    </>
  )
}
