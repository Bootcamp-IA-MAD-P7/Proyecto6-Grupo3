import { useEffect, useRef, useState } from 'react'
import { CATEGORIES } from '../config/categories'
import './CategoriesPage.css'

const CATEGORY_DETAILS = {
  cookies: {
    icon: '◉',
    description: 'Uso de cookies y tecnologías similares en el sitio.',
    meaning:
      'Las cookies son pequeños archivos que una web guarda en tu dispositivo. Pueden recordar tus preferencias, mantener tu sesión abierta o registrar cómo utilizas la página.',
    importance:
      'Algunas cookies permiten seguir tu actividad y relacionarla con otros datos para conocer mejor tus hábitos.',
    example:
      'Una tienda recuerda los productos que has mirado y después te muestra anuncios relacionados en otras páginas.',
  },
  data_collection: {
    icon: '↓',
    description: 'Información que la organización recoge y utiliza.',
    meaning:
      'Explica qué información obtiene una organización sobre ti. Puede incluir datos que proporcionas directamente y otros que se generan cuando utilizas el servicio.',
    importance:
      'Conocer qué se recopila te ayuda a decidir si la información solicitada es razonable para el servicio que recibes.',
    example:
      'Al crear una cuenta facilitas tu correo, pero la aplicación también registra el dispositivo y la hora de acceso.',
  },
  third_party: {
    icon: '↗',
    description: 'Datos compartidos o recopilados por terceros.',
    meaning:
      'Indica si tus datos se envían a empresas distintas de la que ofrece el servicio. Estas pueden ser proveedores técnicos, socios comerciales o plataformas publicitarias.',
    importance:
      'Cuando intervienen más organizaciones, tus datos pueden utilizarse en contextos que no esperabas inicialmente.',
    example:
      'Una aplicación comparte información de uso con una empresa de analítica para medir cómo navegan sus usuarios.',
  },
  data_retention: {
    icon: '◷',
    description: 'Plazos y criterios para conservar la información.',
    meaning:
      'Describe durante cuánto tiempo se guardan tus datos o qué criterios se utilizan para decidir cuándo eliminarlos. El plazo puede variar según el tipo de información.',
    importance:
      'Guardar datos durante más tiempo del necesario aumenta la posibilidad de usos futuros o accesos no autorizados.',
    example:
      'Una plataforma conserva tus facturas durante varios años, pero elimina los registros de actividad al cerrar la cuenta.',
  },
  data_security: {
    icon: '◇',
    description: 'Medidas empleadas para proteger los datos.',
    meaning:
      'Resume las medidas que utiliza una organización para evitar pérdidas, accesos indebidos o modificaciones de tus datos. Puede incluir controles técnicos y procedimientos internos.',
    importance:
      'Una protección adecuada reduce el riesgo de que tu información quede expuesta o sea utilizada por personas no autorizadas.',
    example:
      'El servicio cifra las comunicaciones y limita el acceso a los datos únicamente al personal que lo necesita.',
  },
  user_rights: {
    icon: '✓',
    description: 'Opciones para acceder, modificar o eliminar datos.',
    meaning:
      'Explica qué decisiones puedes tomar sobre tus datos personales. Entre ellas están consultar la información, corregirla, solicitar su eliminación o limitar determinados usos.',
    importance:
      'Estos derechos permiten mantener el control y actuar cuando la información es incorrecta o ya no quieres que se utilice.',
    example:
      'Solicitas a una plataforma una copia de tus datos y pides que corrija una dirección antigua.',
  },
  intl_transfer: {
    icon: '↔',
    description: 'Transferencias de información entre países.',
    meaning:
      'Indica si tus datos pueden almacenarse o tratarse fuera de tu país o del Espacio Económico Europeo. También puede explicar las garantías aplicadas en esos casos.',
    importance:
      'Las normas y niveles de protección pueden variar entre países, por lo que importa saber dónde viaja tu información.',
    example:
      'Una empresa europea utiliza servidores de un proveedor situado en Estados Unidos para alojar sus datos.',
  },
  children_privacy: {
    icon: '○',
    description: 'Tratamiento de datos de menores y audiencias específicas.',
    meaning:
      'Explica si el servicio está dirigido a menores y cómo gestiona su información. Puede incluir límites de edad, consentimiento familiar y medidas de protección especiales.',
    importance:
      'Los menores necesitan una protección reforzada porque pueden comprender con más dificultad las consecuencias de compartir datos.',
    example:
      'Una aplicación educativa solicita autorización familiar antes de crear la cuenta de una persona menor de edad.',
  },
  tracking: {
    icon: '⌁',
    description: 'Seguimiento, perfilado y señales de no rastreo.',
    meaning:
      'Describe tecnologías que observan tu actividad y combinan señales para conocer intereses o comportamientos. Esto puede ocurrir dentro de un servicio o entre distintas páginas.',
    importance:
      'El seguimiento puede crear perfiles detallados que influyen en los contenidos, anuncios u opciones que ves.',
    example:
      'Una red publicitaria relaciona las páginas que visitas para estimar tus intereses y personalizar anuncios.',
  },
  policy_change: {
    icon: '↻',
    description: 'Cómo se comunican los cambios de la política.',
    meaning:
      'Explica cuándo y cómo puede modificarse la política de privacidad. También indica de qué manera se avisará a las personas usuarias sobre cambios importantes.',
    importance:
      'Una actualización puede introducir nuevos usos de tus datos, por lo que conviene saber cómo podrás enterarte y revisar las novedades.',
    example:
      'La plataforma envía un correo antes de aplicar una nueva política que permite usar datos para funciones adicionales.',
  },
}

export default function CategoriesPage() {
  const [selectedCategory, setSelectedCategory] = useState(null)
  const [isClosing, setIsClosing] = useState(false)
  const closeButtonRef = useRef(null)
  const triggerRef = useRef(null)
  const closeTimerRef = useRef(null)

  const openCategory = (category, trigger) => {
    if (closeTimerRef.current) window.clearTimeout(closeTimerRef.current)
    triggerRef.current = trigger
    setIsClosing(false)
    setSelectedCategory(category)
  }

  const closeCategory = () => {
    if (!selectedCategory || isClosing) return
    setIsClosing(true)
    closeTimerRef.current = window.setTimeout(() => {
      setSelectedCategory(null)
      setIsClosing(false)
      triggerRef.current?.focus()
    }, 180)
  }

  useEffect(() => {
    if (!selectedCategory) return undefined

    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    const focusFrame = window.requestAnimationFrame(() => closeButtonRef.current?.focus())

    const handleKeyDown = (event) => {
      if (event.key === 'Escape') closeCategory()
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => {
      window.cancelAnimationFrame(focusFrame)
      window.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = previousOverflow
    }
  }, [selectedCategory, isClosing])

  useEffect(
    () => () => {
      if (closeTimerRef.current) window.clearTimeout(closeTimerRef.current)
    },
    [],
  )

  const selectedDetail = selectedCategory
    ? CATEGORY_DETAILS[selectedCategory.id]
    : null

  return (
    <>
      <section className="categories-page container">
        <header className="page-heading">
          <span className="page-heading__eyebrow">Taxonomía PrivacyLens</span>
          <h1>Categorías de privacidad</h1>
          <p>
            Los temas que PrivacyLens identifica para convertir una política extensa en
            información clara y fácil de revisar.
          </p>
        </header>

        <div className="categories-grid">
          {CATEGORIES.map((category) => {
            const detail = CATEGORY_DETAILS[category.id]
            return (
              <button
                type="button"
                className="category-card"
                key={category.id}
                onClick={(event) => openCategory(category, event.currentTarget)}
                aria-haspopup="dialog"
              >
                <span
                  className="category-card__icon"
                  style={{
                    color: `var(${category.colorToken})`,
                    background: `var(${category.softToken})`,
                  }}
                  aria-hidden="true"
                >
                  {detail.icon}
                </span>
                <span className="category-card__content">
                  <strong>{category.label}</strong>
                  <span className="category-card__description">{detail.description}</span>
                </span>
                <span className="category-card__hint">
                  <i aria-hidden="true">i</i>
                  Haz clic para saber más
                </span>
                <span
                  className="category-card__line"
                  style={{ background: `var(${category.colorToken})` }}
                  aria-hidden="true"
                />
              </button>
            )
          })}
        </div>
      </section>

      {selectedCategory && (
        <div
          className={`category-dialog-backdrop ${isClosing ? 'is-closing' : ''}`}
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) closeCategory()
          }}
          role="presentation"
        >
          <section
            className={`category-dialog ${isClosing ? 'is-closing' : ''}`}
            role="dialog"
            aria-modal="true"
            aria-labelledby="category-dialog-title"
            aria-describedby="category-dialog-meaning"
          >
            <header className="category-dialog__header">
              <span
                className="category-dialog__icon"
                style={{
                  color: `var(${selectedCategory.colorToken})`,
                  background: `var(${selectedCategory.softToken})`,
                }}
                aria-hidden="true"
              >
                {selectedDetail.icon}
              </span>
              <div>
                <span>Concepto de privacidad</span>
                <h2 id="category-dialog-title">{selectedCategory.label}</h2>
              </div>
            </header>

            <div className="category-dialog__sections">
              <div>
                <h3>¿Qué significa?</h3>
                <p id="category-dialog-meaning">{selectedDetail.meaning}</p>
              </div>
              <div>
                <h3>¿Por qué es importante?</h3>
                <p>{selectedDetail.importance}</p>
              </div>
              <div className="category-dialog__example">
                <h3>Ejemplo</h3>
                <p>{selectedDetail.example}</p>
              </div>
            </div>

            <button
              type="button"
              className="category-dialog__close"
              onClick={closeCategory}
              ref={closeButtonRef}
            >
              Cerrar
            </button>
          </section>
        </div>
      )}
    </>
  )
}
