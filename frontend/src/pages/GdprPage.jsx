import { Link } from 'react-router-dom'
import protectionIllustration from '../../escudo.jpg'
import './GdprPage.css'

const RIGHTS = [
  {
    icon: '⌕',
    title: 'Derecho de acceso',
    description:
      'Puedes solicitar qué datos personales tiene una organización sobre ti y cómo los utiliza.',
  },
  {
    icon: '✎',
    title: 'Derecho de rectificación',
    description:
      'Puedes pedir que se corrijan datos personales incorrectos o incompletos.',
  },
  {
    icon: '×',
    title: 'Derecho de supresión',
    description:
      'En determinadas situaciones puedes solicitar que tus datos sean eliminados.',
  },
  {
    icon: '⊘',
    title: 'Derecho de oposición',
    description:
      'Puedes oponerte a ciertos usos de tus datos, como el marketing directo.',
  },
  {
    icon: 'Ⅱ',
    title: 'Derecho a la limitación',
    description:
      'Puedes solicitar que el tratamiento de tus datos quede temporalmente restringido.',
  },
  {
    icon: '⇄',
    title: 'Derecho a la portabilidad',
    description:
      'Puedes recibir tus datos en un formato estructurado y trasladarlos a otro servicio.',
  },
  {
    icon: '⚙',
    title: 'Derecho a no ser objeto de decisiones automatizadas',
    description:
      'Puedes pedir intervención humana cuando una decisión importante se haya tomado únicamente mediante sistemas automáticos.',
  },
  {
    icon: '↶',
    title: 'Derecho a retirar el consentimiento',
    description:
      'Puedes retirar tu consentimiento cuando el tratamiento de tus datos dependa de él.',
  },
]

const STEPS = [
  {
    title: 'Identifica a la organización',
    description: 'Busca el responsable del tratamiento y sus datos de contacto.',
  },
  {
    title: 'Explica tu solicitud',
    description:
      'Indica claramente qué derecho deseas ejercer y sobre qué información.',
  },
  {
    title: 'Conserva una copia',
    description: 'Guarda la solicitud y cualquier respuesta recibida.',
  },
]

const PRIVACYLENS_TOPICS = [
  'Finalidad del tratamiento',
  'Base legal',
  'Conservación de datos',
  'Derechos y contacto',
]

export default function GdprPage() {
  return (
    <div className="gdpr-page">
      <section className="gdpr-hero container">
        <div className="gdpr-hero__copy">
          <span className="gdpr-eyebrow">TUS DATOS, TUS DERECHOS</span>
          <h1>El RGPD te da más control sobre tu información personal</h1>
          <p>
            Las políticas de privacidad deben explicar qué datos se recopilan, para qué se
            utilizan y qué derechos puedes ejercer. PrivacyLens te ayuda a localizar esta
            información y entenderla con un lenguaje más claro.
          </p>
        </div>
        <div className="gdpr-hero__visual" aria-hidden="true">
          <img src={protectionIllustration} alt="" />
        </div>
      </section>

      <section className="gdpr-rights container" aria-labelledby="gdpr-rights-title">
        <header className="gdpr-section-heading">
          <span className="gdpr-eyebrow">Derechos RGPD</span>
          <h2 id="gdpr-rights-title">Herramientas para decidir sobre tus datos</h2>
        </header>

        <div className="gdpr-rights__grid">
          {RIGHTS.map((right, index) => (
            <article className="gdpr-right-card" key={right.title}>
              <span className={`gdpr-right-card__icon gdpr-right-card__icon--${(index % 3) + 1}`} aria-hidden="true">
                {right.icon}
              </span>
              <h3>{right.title}</h3>
              <p>{right.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="gdpr-steps">
        <div className="container">
          <header className="gdpr-section-heading gdpr-section-heading--center">
            <span className="gdpr-eyebrow">Guía práctica</span>
            <h2>Cómo ejercer tus derechos</h2>
          </header>

          <div className="gdpr-steps__grid">
            {STEPS.map((step, index) => (
              <article className="gdpr-step" key={step.title}>
                <span className="gdpr-step__number">{index + 1}</span>
                <h3>{step.title}</h3>
                <p>{step.description}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="gdpr-detection container">
        <div className="gdpr-detection__copy">
          <span className="gdpr-eyebrow">Lectura asistida</span>
          <h2>¿Qué información busca PrivacyLens?</h2>
          <p>
            PrivacyLens analiza fragmentos de políticas para señalar dónde se explican estas
            cuestiones y ayudarte a encontrarlas más rápido.
          </p>
        </div>

        <div className="gdpr-detection__grid">
          {PRIVACYLENS_TOPICS.map((topic, index) => (
            <div className="gdpr-topic" key={topic}>
              <span>{String(index + 1).padStart(2, '0')}</span>
              <strong>{topic}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="gdpr-cta container">
        <div>
          <span className="gdpr-cta__mark" aria-hidden="true">i</span>
          <div>
            <h2>
              PrivacyLens es una herramienta educativa para ayudarte a comprender las
              políticas de privacidad.
            </h2>
            <p>
              No sustituye el asesoramiento jurídico profesional.
            </p>
          </div>
        </div>
        <Link to="/" className="gdpr-cta__button">
          Analizar una política
        </Link>
      </section>
    </div>
  )
}
