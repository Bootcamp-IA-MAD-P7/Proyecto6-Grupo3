import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import UrlAnalyzerBox from '../components/ui/UrlAnalyzerBox'
import AnalysisPreviewCard from '../components/ui/AnalysisPreviewCard'
import StatCard from '../components/ui/StatCard'
import RecentAnalyses from '../components/ui/RecentAnalyses'
import { getRecentAnalyses, getGlobalStats } from '../services/analysisService'
import { MOCK_ANALYSIS } from '../services/mockData'
import fingerprintImage from '../../huella-digital.png'
import './HomePage.css'

const STAT_TONES = ['primary', 'secondary', 'accent', 'amber']

export default function HomePage() {
  const navigate = useNavigate()
  const [preview] = useState(MOCK_ANALYSIS)
  const [recent, setRecent] = useState([])
  const [stats, setStats] = useState([])

  useEffect(() => {
    getRecentAnalyses().then(setRecent)
    getGlobalStats().then(setStats)
  }, [])

  const handleAnalyze = async (url) => {
    navigate('/analisis', { state: { url } })
  }

  return (
    <>
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

          <UrlAnalyzerBox onAnalyze={handleAnalyze} />

          <div className="hero__benefits" aria-label="Ventajas de PrivacyLens">
            <span>✓ Analiza políticas en segundos</span>
            <span>✓ IA entrenada con OPP-115</span>
            <span>✓ Basado en categorías de privacidad</span>
          </div>

          <p className="hero__alt">
            ¿Sin URL? <a href="#texto">Pega el texto de la política directamente →</a>
          </p>

          <div className="hero__trust">
            <div><b>1.247</b> políticas analizadas</div>
            <div><b>10</b> categorías detectadas</div>
            <div><b>6</b> idiomas</div>
          </div>
        </div>

        <div className="hero__visual">
          <img
            className="hero__fingerprint"
            src={fingerprintImage}
            alt=""
            aria-hidden="true"
          />
          <AnalysisPreviewCard analysis={preview} />
        </div>
      </section>

      <section className="stats container" aria-label="Métricas de PrivacyLens">
        {stats.map((stat, index) => (
          <StatCard
            key={stat.label}
            value={stat.value}
            label={stat.label}
            tone={STAT_TONES[index % 4]}
          />
        ))}
      </section>

      <RecentAnalyses
        items={recent}
        onSelect={(slug) => navigate('/analisis', { state: { slug } })}
      />
    </>
  )
}
