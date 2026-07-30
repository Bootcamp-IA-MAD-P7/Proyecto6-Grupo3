import { Link } from 'react-router-dom'
import labIllustration from '../../privaylens lab.jpg'
import './ModelPage.css'

const LAB_MODULES = [
  {
    icon: '🤖',
    title: 'El modelo',
    description: 'Cómo funciona el algoritmo que clasifica cada fragmento.',
    action: 'Explorar',
  },
  {
    icon: '📊',
    title: 'Rendimiento',
    description: 'Conoce las métricas obtenidas durante la evaluación del modelo.',
    action: 'Ver métricas',
  },
  {
    icon: '⚙️',
    title: 'Entrenamiento',
    description: 'Cómo se prepararon los datos antes del aprendizaje.',
    action: 'Descubrir',
  },
  {
    icon: '📚',
    title: 'Dataset',
    description: 'Información sobre OPP-115 y el conjunto de entrenamiento.',
    action: 'Más información',
  },
  {
    icon: '🔄',
    title: 'Pipeline',
    description: 'Paso a paso del proceso seguido desde una política hasta el resultado.',
    action: 'Ver proceso',
  },
]

export default function ModelPage() {
  return (
    <div className="lab-page">
      <section className="lab-hero">
        <div className="lab-hero__inner container">
          <div className="lab-hero__copy">
            <span className="lab-eyebrow">LABORATORIO DE IA</span>
            <h1>PrivacyLens Lab</h1>
            <p>
              Descubre cómo la inteligencia artificial analiza una política de privacidad y
              la transforma en información comprensible para cualquier persona.
            </p>
          </div>

          <div className="lab-hero__visual">
            <img
              src={labIllustration}
              alt="Panel tecnológico con visualizaciones de datos e inteligencia artificial"
            />
            <span className="lab-hero__status">
              <i aria-hidden="true" />
              Sistema preparado
            </span>
          </div>
        </div>
      </section>

      <section className="lab-intro container">
        <span className="lab-intro__mark" aria-hidden="true">AI</span>
        <p>
          PrivacyLens utiliza técnicas de <strong>Procesamiento del Lenguaje Natural</strong> y
          {' '}<strong>Machine Learning</strong> para identificar automáticamente distintos
          tipos de información presentes en una política de privacidad.
        </p>
      </section>

      <section className="lab-modules container" id="lab-modules">
        <header className="lab-section-heading">
          <span className="lab-eyebrow">MÓDULOS DEL LABORATORIO</span>
          <h2>Explora cómo aprende PrivacyLens</h2>
          <p>Cada módulo abre una parte diferente del proceso de inteligencia artificial.</p>
        </header>

        <div className="lab-grid">
          {LAB_MODULES.map((module, index) => (
            <article className={`lab-card lab-card--${index + 1}`} key={module.title}>
              <div className="lab-card__top">
                <span className="lab-card__index">{String(index + 1).padStart(2, '0')}</span>
                <span className="lab-card__icon" aria-hidden="true">{module.icon}</span>
              </div>
              <h3>{module.title}</h3>
              <p>{module.description}</p>
              <button type="button">{module.action} <span aria-hidden="true">→</span></button>
            </article>
          ))}
        </div>
      </section>

      <section className="lab-cta container">
        <div>
          <span className="lab-eyebrow">PRUEBA EL SISTEMA</span>
          <h2>¿Quieres ver la IA en acción?</h2>
          <p>Pon a prueba PrivacyLens analizando una política de privacidad real.</p>
        </div>
        <Link to="/" className="lab-cta__button">
          Ir al Analizador
        </Link>
      </section>
    </div>
  )
}
