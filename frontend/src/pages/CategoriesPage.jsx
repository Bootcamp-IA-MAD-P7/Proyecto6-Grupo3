import { CATEGORIES } from '../config/categories'
import './CategoriesPage.css'

const CATEGORY_DETAILS = {
  cookies: { icon: '◎', description: 'Uso de cookies y tecnologías similares en el sitio.' },
  data_collection: { icon: '↓', description: 'Información que la organización recoge y utiliza.' },
  third_party: { icon: '↗', description: 'Datos compartidos o recopilados por terceros.' },
  data_retention: { icon: '◷', description: 'Plazos y criterios para conservar la información.' },
  data_security: { icon: '◇', description: 'Medidas empleadas para proteger los datos.' },
  user_rights: { icon: '✓', description: 'Opciones para acceder, modificar o eliminar datos.' },
  intl_transfer: { icon: '↔', description: 'Transferencias de información entre países.' },
  children_privacy: { icon: '○', description: 'Tratamiento de datos de menores y audiencias específicas.' },
  tracking: { icon: '⌁', description: 'Seguimiento, perfilado y señales de no rastreo.' },
  policy_change: { icon: '↻', description: 'Cómo se comunican los cambios de la política.' },
}

export default function CategoriesPage() {
  return (
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
            <article className="category-card" key={category.id}>
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
              <div>
                <h2>{category.label}</h2>
                <p>{detail.description}</p>
              </div>
              <span
                className="category-card__line"
                style={{ background: `var(${category.colorToken})` }}
                aria-hidden="true"
              />
            </article>
          )
        })}
      </div>
    </section>
  )
}
