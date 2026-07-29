import { Link } from 'react-router-dom'
import risksIllustration from '../../huella candado.jpg'
import './RisksPage.css'

const RISKS = [
  {
    icon: '◎',
    title: 'Seguimiento',
    impact: 'Medio',
    description:
      'Cookies, identificadores y tecnologías similares pueden registrar tu actividad dentro y fuera de una plataforma.',
  },
  {
    icon: '◇',
    title: 'Perfilado',
    impact: 'Alto',
    description:
      'Tus hábitos, intereses y comportamiento pueden utilizarse para crear perfiles sobre ti.',
  },
  {
    icon: '↗',
    title: 'Compartición con terceros',
    impact: 'Alto',
    description:
      'Tu información puede compartirse con proveedores, socios comerciales o plataformas publicitarias.',
  },
  {
    icon: '⌖',
    title: 'Geolocalización',
    impact: 'Medio',
    description:
      'La ubicación aproximada o precisa puede utilizarse para personalizar servicios, medir actividad o mostrar publicidad.',
  },
  {
    icon: '◷',
    title: 'Conservación de datos',
    impact: 'Variable',
    description:
      'Algunas empresas pueden guardar tus datos durante periodos largos o poco definidos.',
  },
  {
    icon: '⚙',
    title: 'Decisiones automatizadas',
    impact: 'Medio',
    description:
      'Los sistemas automáticos pueden clasificarte, recomendar contenido o tomar decisiones basadas en tus datos.',
  },
]

export default function RisksPage() {
  return (
    <div className="risks-page">
      <section className="risks-hero container">
        <img
          className="risks-hero__illustration"
          src={risksIllustration}
          alt=""
          aria-hidden="true"
        />
        <header className="risks-heading">
          <span className="risks-heading__eyebrow">Privacidad sin letra pequeña</span>
          <h1>Los riesgos que pueden esconderse en una política de privacidad</h1>
          <p>
            Una política puede explicar que tus datos se recopilan, combinan o comparten.
            PrivacyLens te ayuda a detectar estas prácticas y entender qué significan para ti.
          </p>
        </header>

        <div className="risks-grid">
          {RISKS.map((risk, index) => (
            <article className="risk-card" key={risk.title}>
              <span className={`risk-card__icon risk-card__icon--${(index % 3) + 1}`} aria-hidden="true">
                {risk.icon}
              </span>
              <h2>{risk.title}</h2>
              <p>{risk.description}</p>
              <span className="risk-card__impact">
                Impacto habitual: <strong>{risk.impact}</strong>
              </span>
            </article>
          ))}
        </div>
      </section>

      <section className="data-journey">
        <div className="data-journey__inner container">
          <div className="data-journey__copy">
            <span className="data-journey__eyebrow">El recorrido de la información</span>
            <h2>Tus datos no viajan solos</h2>
            <p>
              Una sola acción puede generar distintos tipos de información: ubicación,
              dispositivo, intereses, historial de uso y relaciones con otros servicios.
            </p>
          </div>

          <div className="journey-diagram" aria-label="Usuario conecta con Plataforma, que distribuye datos a Analítica, Publicidad y Terceros">
            <div className="journey-node journey-node--user">
              <span aria-hidden="true">👤</span>
              <strong>Usuario</strong>
            </div>

            <span className="journey-diagram__trunk" aria-hidden="true" />

            <div className="journey-node journey-node--platform">
              <span aria-hidden="true">🌐</span>
              <strong>Plataforma</strong>
            </div>

            <div className="journey-diagram__branches">
              <div className="journey-node">
                <span aria-hidden="true">📊</span>
                <strong>Analítica</strong>
              </div>
              <div className="journey-node">
                <span aria-hidden="true">📢</span>
                <strong>Publicidad</strong>
              </div>
              <div className="journey-node">
                <span aria-hidden="true">🤝</span>
                <strong>Terceros</strong>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="risks-cta container">
        <div>
          <span className="risks-cta__icon" aria-hidden="true">i</span>
          <div>
            <h2>No todos los riesgos significan una infracción</h2>
            <p>
              El contexto importa. PrivacyLens muestra prácticas relevantes para que puedas
              leer con más criterio, pero sus resultados son orientativos y no sustituyen
              asesoramiento jurídico.
            </p>
          </div>
        </div>
        <Link to="/" className="risks-cta__button">
          Analizar una política
        </Link>
      </section>
    </div>
  )
}
