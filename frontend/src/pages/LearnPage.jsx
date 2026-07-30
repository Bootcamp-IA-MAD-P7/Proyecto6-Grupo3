import { Link } from 'react-router-dom'
import './LearnPage.css'

const TALK_URL = 'https://www.youtube.com/watch?v=NPE7i8wuupk'
const TALK_THUMBNAIL = 'https://img.youtube.com/vi/NPE7i8wuupk/maxresdefault.jpg'

const LEARNING_PATHS = [
  {
    number: '01',
    symbol: '§',
    title: 'Quiero conocer mis derechos',
    description:
      'Descubre qué puedes solicitar a una empresa y cómo ejercer tus derechos sobre tus datos.',
    href: 'https://www.aepd.es/derechos-y-deberes/ejerce-tus-derechos',
    action: 'Conocer mis derechos',
  },
  {
    number: '02',
    symbol: '◇',
    title: 'Quiero protegerme en Internet',
    description:
      'Aprende a controlar permisos, contraseñas, identidad digital y privacidad en tus dispositivos.',
    href: 'https://www.incibe.es/ciudadania/tematicas/privacidad',
    action: 'Mejorar mi privacidad',
  },
  {
    number: '03',
    symbol: '◎',
    title: 'Quiero entender el RGPD',
    description:
      'Consulta información oficial de la Unión Europea sobre protección de datos y derechos de las personas.',
    href: 'https://commission.europa.eu/law/law-topic/data-protection/information-individuals_en',
    action: 'Entender el RGPD',
  },
]

const RESOURCES = [
  {
    type: 'Organismo oficial',
    title: 'Agencia Española de Protección de Datos',
    description:
      'Información oficial sobre derechos, protección de datos, reclamaciones y uso responsable de la información personal.',
    href: 'https://www.aepd.es/',
    action: 'Visitar la AEPD',
    featured: true,
  },
  {
    type: 'Guía',
    title: 'Guía para la ciudadanía',
    description:
      'Una guía práctica para entender cómo se utilizan tus datos personales y qué herramientas tienes para protegerlos.',
    href: 'https://www.aepd.es/guias/guia-ciudadano.pdf',
    action: 'Abrir la guía',
    featured: true,
  },
  {
    type: 'Infografía',
    title: 'Permisos de aplicaciones',
    description:
      'Una infografía de INCIBE para comprender qué permisos solicitan las aplicaciones y qué riesgos pueden implicar.',
    href: 'https://www.incibe.es/ciudadania/formacion/infografias/permisos-de-apps-y-riesgos-para-tu-privacidad',
    action: 'Ver infografía',
  },
  {
    type: 'Derechos',
    title: 'Tus derechos digitales',
    description:
      'Información para reconocer y ejercer los principales derechos relacionados con tus datos personales.',
    href: 'https://www.aepd.es/derechos-y-deberes/ejerce-tus-derechos',
    action: 'Consultar derechos',
  },
]

const HABITS = [
  'Revisa los permisos de las aplicaciones.',
  'Activa la verificación en dos pasos.',
  'Utiliza contraseñas diferentes.',
  'Comprueba qué información compartes públicamente.',
  'Revisa las opciones antes de aceptar todas las cookies.',
]

function ExternalLink({ className = '', href, children }) {
  return (
    <a
      className={className}
      href={href}
      target="_blank"
      rel="noopener noreferrer"
    >
      {children} <span aria-hidden="true">↗</span>
    </a>
  )
}

export default function LearnPage() {
  return (
    <div className="learn-editorial">
      <header className="learn-intro container">
        <span className="learn-label">PRIVACIDAD SIN TECNICISMOS</span>
        <h1>Aprende a reconocer qué ocurre con tus datos</h1>
        <p>
          Una selección de vídeos, guías y recursos fiables para entender la privacidad y
          tomar decisiones con más información.
        </p>
      </header>

      <section className="learn-talk container" aria-labelledby="featured-talk-title">
        <a
          className="learn-talk__media"
          href={TALK_URL}
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Ver la charla ¿Por qué me vigilan, si no soy nadie? en YouTube"
        >
          <img
            src={TALK_THUMBNAIL}
            alt="Marta Peirano durante su charla TEDxMadrid sobre vigilancia y privacidad"
          />
          <span className="learn-talk__play" aria-hidden="true">▶</span>
        </a>

        <div className="learn-talk__content">
          <span className="learn-label">CHARLA DESTACADA</span>
          <h2 id="featured-talk-title">¿Por qué me vigilan, si no soy nadie?</h2>
          <strong>Marta Peirano · TEDxMadrid</strong>
          <p>
            Una explicación clara y cercana sobre por qué la vigilancia y la recopilación de
            datos afectan a todas las personas, incluso cuando creemos que no tenemos nada
            que ocultar.
          </p>
          <ExternalLink className="learn-action learn-action--primary" href={TALK_URL}>
            Ver la charla
          </ExternalLink>
        </div>
      </section>

      <section className="learn-paths">
        <div className="container">
          <header className="learn-section-title">
            <span className="learn-label">TRES RECORRIDOS</span>
            <h2>Empieza por aquí</h2>
            <p>Elige el tema que más te interese y continúa aprendiendo a tu ritmo.</p>
          </header>

          <div className="learn-paths__layout">
            {LEARNING_PATHS.map((path, index) => (
              <article className={`learn-path learn-path--${index + 1}`} key={path.title}>
                <div className="learn-path__symbol" aria-hidden="true">{path.symbol}</div>
                <span className="learn-path__number">{path.number}</span>
                <h3>{path.title}</h3>
                <p>{path.description}</p>
                <ExternalLink className="learn-path__link" href={path.href}>
                  {path.action}
                </ExternalLink>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="learn-magazine container">
        <header className="learn-section-title learn-section-title--wide">
          <span className="learn-label">SELECCIÓN EDITORIAL</span>
          <h2>Recursos para seguir aprendiendo</h2>
        </header>

        <div className="learn-magazine__grid">
          {RESOURCES.map((resource, index) => (
            <article
              className={`learn-resource ${resource.featured ? 'learn-resource--featured' : ''} learn-resource--${index + 1}`}
              key={resource.title}
            >
              <span className="learn-resource__type">{resource.type}</span>
              <h3>{resource.title}</h3>
              <p>{resource.description}</p>
              <ExternalLink className="learn-resource__link" href={resource.href}>
                {resource.action}
              </ExternalLink>
            </article>
          ))}
        </div>
      </section>

      <section className="learn-habits">
        <div className="container">
          <header className="learn-section-title">
            <span className="learn-label">PRIVACIDAD COTIDIANA</span>
            <h2>Cinco hábitos que puedes aplicar hoy</h2>
          </header>

          <ol className="learn-habits__list">
            {HABITS.map((habit, index) => (
              <li key={habit}>
                <span>{String(index + 1).padStart(2, '0')}</span>
                <p>{habit}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="learn-final container">
        <span className="learn-final__number" aria-hidden="true">PL</span>
        <div>
          <span className="learn-label">SIGUIENTE PASO</span>
          <h2>Ahora mira una política con otros ojos</h2>
          <p>
            Utiliza PrivacyLens para localizar los fragmentos más importantes y comprender
            mejor qué ocurre con tus datos.
          </p>
        </div>
        <Link className="learn-action learn-action--primary" to="/">
          Analizar una política
        </Link>
      </section>
    </div>
  )
}
