import { useEffect, useRef, useState } from 'react'
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
    meaning:
      'El seguimiento consiste en observar tu actividad mientras utilizas páginas y aplicaciones. Distintas señales pueden combinarse para reconocer tu dispositivo y conocer qué contenidos consultas.',
    effect:
      'Puede reducir tu privacidad al crear un historial detallado de tus hábitos, incluso cuando no has iniciado sesión.',
    recommendations: [
      'Revisa las preferencias de cookies antes de aceptar.',
      'Bloquea las cookies de terceros cuando no sean necesarias.',
      'Elimina periódicamente los datos de navegación.',
      'Comprueba los ajustes de privacidad del navegador.',
    ],
  },
  {
    icon: '◇',
    title: 'Perfilado',
    impact: 'Alto',
    description:
      'Tus hábitos, intereses y comportamiento pueden utilizarse para crear perfiles sobre ti.',
    meaning:
      'El perfilado utiliza información sobre tus acciones para estimar intereses, preferencias o características personales. El perfil resultante puede actualizarse cada vez que utilizas el servicio.',
    effect:
      'Puede influir en los anuncios, contenidos, precios u oportunidades que se te muestran sin que sepas exactamente por qué.',
    recommendations: [
      'Desactiva la personalización de anuncios cuando sea posible.',
      'Revisa qué intereses ha asociado cada plataforma a tu cuenta.',
      'Limita la información opcional que añades a tus perfiles.',
      'Solicita información sobre decisiones importantes basadas en perfiles.',
    ],
  },
  {
    icon: '↗',
    title: 'Compartición con terceros',
    impact: 'Alto',
    description:
      'Tu información puede compartirse con proveedores, socios comerciales o plataformas publicitarias.',
    meaning:
      'Ocurre cuando una organización facilita tus datos a otras empresas o permite que estas los recopilen. Pueden ser proveedores necesarios para el servicio o entidades con sus propias finalidades.',
    effect:
      'Pierdes parte del control sobre quién utiliza la información y puede resultar más difícil saber dónde se encuentra o pedir que se elimine.',
    recommendations: [
      'Consulta con qué tipos de empresas se comparten los datos.',
      'Rechaza finalidades publicitarias que no sean necesarias.',
      'Evita vincular servicios si no necesitas esa conexión.',
      'Utiliza los formularios de privacidad para ejercer tus derechos.',
    ],
  },
  {
    icon: '⌖',
    title: 'Geolocalización',
    impact: 'Medio',
    description:
      'La ubicación aproximada o precisa puede utilizarse para personalizar servicios, medir actividad o mostrar publicidad.',
    meaning:
      'La geolocalización permite conocer dónde se encuentra tu dispositivo de forma aproximada o precisa. Puede obtenerse mediante GPS, redes wifi, dirección IP u otras señales.',
    effect:
      'Un historial de ubicaciones puede revelar rutinas, lugares frecuentes y momentos en los que te encuentras fuera de casa.',
    recommendations: [
      'Concede acceso a la ubicación sólo mientras usas la aplicación.',
      'Desactiva la ubicación precisa cuando no sea imprescindible.',
      'Revisa periódicamente qué aplicaciones tienen permiso.',
      'Borra el historial de ubicaciones que no necesites conservar.',
    ],
  },
  {
    icon: '◷',
    title: 'Conservación de datos',
    impact: 'Variable',
    description:
      'Algunas empresas pueden guardar tus datos durante periodos largos o poco definidos.',
    meaning:
      'Se refiere al tiempo durante el que una organización mantiene tus datos después de recopilarlos. Algunas políticas indican un plazo concreto y otras utilizan criterios más generales.',
    effect:
      'Cuanto más tiempo se conserva la información, más posibilidades existen de que se use nuevamente o quede expuesta en un incidente.',
    recommendations: [
      'Busca si la política indica plazos de conservación concretos.',
      'Elimina cuentas que ya no utilizas.',
      'Solicita la supresión de datos que ya no sean necesarios.',
      'Conserva la confirmación de cualquier solicitud realizada.',
    ],
  },
  {
    icon: '⚙',
    title: 'Decisiones automatizadas',
    impact: 'Medio',
    description:
      'Los sistemas automáticos pueden clasificarte, recomendar contenido o tomar decisiones basadas en tus datos.',
    meaning:
      'Son decisiones o clasificaciones realizadas por sistemas informáticos a partir de tus datos, con poca o ninguna intervención humana. Pueden utilizar reglas, perfiles o modelos de inteligencia artificial.',
    effect:
      'Una decisión incorrecta puede limitar opciones o tratarte de forma diferente, y a veces resulta difícil comprender cómo se llegó al resultado.',
    recommendations: [
      'Comprueba si puedes solicitar intervención humana.',
      'Pide una explicación cuando una decisión tenga efectos importantes.',
      'Corrige los datos incorrectos utilizados por el sistema.',
      'Presenta una revisión o reclamación si el resultado te perjudica.',
    ],
  },
]

export default function RisksPage() {
  const [selectedRisk, setSelectedRisk] = useState(null)
  const [isClosing, setIsClosing] = useState(false)
  const closeButtonRef = useRef(null)
  const triggerRef = useRef(null)
  const closeTimerRef = useRef(null)

  const openRisk = (risk, trigger) => {
    if (closeTimerRef.current) window.clearTimeout(closeTimerRef.current)
    triggerRef.current = trigger
    setIsClosing(false)
    setSelectedRisk(risk)
  }

  const closeRisk = () => {
    if (!selectedRisk || isClosing) return
    setIsClosing(true)
    closeTimerRef.current = window.setTimeout(() => {
      setSelectedRisk(null)
      setIsClosing(false)
      triggerRef.current?.focus()
    }, 180)
  }

  useEffect(() => {
    if (!selectedRisk) return undefined

    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    const focusFrame = window.requestAnimationFrame(() => closeButtonRef.current?.focus())
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') closeRisk()
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => {
      window.cancelAnimationFrame(focusFrame)
      window.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = previousOverflow
    }
  }, [selectedRisk, isClosing])

  useEffect(
    () => () => {
      if (closeTimerRef.current) window.clearTimeout(closeTimerRef.current)
    },
    [],
  )

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
            <button
              type="button"
              className="risk-card"
              key={risk.title}
              onClick={(event) => openRisk(risk, event.currentTarget)}
              aria-haspopup="dialog"
            >
              <span className={`risk-card__icon risk-card__icon--${(index % 3) + 1}`} aria-hidden="true">
                {risk.icon}
              </span>
              <strong className="risk-card__title">{risk.title}</strong>
              <span className="risk-card__description">{risk.description}</span>
              <span className="risk-card__impact">
                Impacto habitual: <strong>{risk.impact}</strong>
              </span>
              <span className="risk-card__hint">
                <i aria-hidden="true">i</i>
                Haz clic para saber más
              </span>
            </button>
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
        <Link to="/" className="risks-cta__button">Analizar una política</Link>
      </section>

      {selectedRisk && (
        <div
          className={`risk-dialog-backdrop ${isClosing ? 'is-closing' : ''}`}
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) closeRisk()
          }}
          role="presentation"
        >
          <section
            className={`risk-dialog ${isClosing ? 'is-closing' : ''}`}
            role="dialog"
            aria-modal="true"
            aria-labelledby="risk-dialog-title"
            aria-describedby="risk-dialog-meaning"
          >
            <header className="risk-dialog__header">
              <span className="risk-dialog__icon" aria-hidden="true">{selectedRisk.icon}</span>
              <div>
                <span>Riesgo de privacidad</span>
                <h2 id="risk-dialog-title">{selectedRisk.title}</h2>
              </div>
            </header>

            <div className="risk-dialog__content">
              <div>
                <h3>¿En qué consiste?</h3>
                <p id="risk-dialog-meaning">{selectedRisk.meaning}</p>
              </div>
              <div>
                <h3>¿Cómo puede afectarte?</h3>
                <p>{selectedRisk.effect}</p>
              </div>
              <div className="risk-dialog__recommendations">
                <h3>¿Qué puedes hacer para reducirlo?</h3>
                <ul>
                  {selectedRisk.recommendations.map((recommendation) => (
                    <li key={recommendation}>{recommendation}</li>
                  ))}
                </ul>
              </div>
            </div>

            <button
              type="button"
              className="risk-dialog__close"
              onClick={closeRisk}
              ref={closeButtonRef}
            >
              Cerrar
            </button>
          </section>
        </div>
      )}
    </div>
  )
}
