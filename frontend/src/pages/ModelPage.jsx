import StatCard from '../components/ui/StatCard'
import { MOCK_STATS } from '../services/mockData'
import './ModelPage.css'

const PIPELINE_STEPS = [
  {
    number: '01',
    name: 'TF-IDF',
    detail: 'Convierte el lenguaje de cada fragmento en características comparables.',
  },
  {
    number: '02',
    name: 'LinearSVC',
    detail: 'Aprende los patrones que distinguen cada práctica de privacidad.',
  },
  {
    number: '03',
    name: '9 categorías',
    detail: 'Devuelve una lectura estructurada y fácil de interpretar.',
  },
]

export default function ModelPage() {
  return (
    <section className="model-page container">
      <header className="model-page__heading">
        <span className="page-heading__eyebrow">Tecnología explicable</span>
        <h1 className="model-page__title">El modelo, explicado</h1>
        <p className="model-page__sub">
          Sin tablas crípticas. Así de bien entiende PrivacyLens cada categoría.
        </p>
      </header>

      <div className="model-page__stats">
        {MOCK_STATS.map((stat, index) => (
          <StatCard
            key={stat.label}
            value={stat.value}
            label={stat.label}
            tone={['primary', 'secondary', 'accent', 'amber'][index % 4]}
          />
        ))}
      </div>

      <section className="pipeline" aria-labelledby="pipeline-title">
        <div className="pipeline__intro">
          <span>Cómo funciona</span>
          <h2 id="pipeline-title">Del texto legal a una lectura clara</h2>
          <p>Un flujo compacto y reproducible, diseñado para mantener cada resultado trazable.</p>
        </div>

        <div className="pipeline__steps">
          {PIPELINE_STEPS.map((step, index) => (
            <div className="pipeline__item" key={step.name}>
              <article className="pipeline-card">
                <span className="pipeline-card__number">{step.number}</span>
                <div className="pipeline-card__icon" aria-hidden="true">
                  {index === 0 ? 'Aa' : index === 1 ? '∑' : '9'}
                </div>
                <h3>{step.name}</h3>
                <p>{step.detail}</p>
              </article>
              {index < PIPELINE_STEPS.length - 1 && (
                <span className="pipeline__connector" aria-hidden="true">
                  <i />
                  <b>→</b>
                </span>
              )}
            </div>
          ))}
        </div>
      </section>

      <p className="model-page__todo">
        Las gráficas de rendimiento se activarán cuando el backend exponga
        las métricas de validación del modelo.
      </p>
    </section>
  )
}
