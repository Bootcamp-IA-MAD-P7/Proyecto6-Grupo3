// ============================================================
//  CategoryChip.jsx — Etiqueta visual de una categoría
// ------------------------------------------------------------
//  QUÉ HACE: muestra una categoría detectada ("Cookies",
//  "Third Party Sharing"…) con SU color corporativo, leído
//  del catálogo central (src/config/categories.js).
//  Se usa en: tarjeta de análisis, página de resultado,
//  dashboard del modelo y extensión de Chrome.
//
//  PROPS:
//   · categoryId (string) — id de la categoría en el catálogo
// ============================================================
import { getCategory } from '../../config/categories'
import './CategoryChip.css'

export default function CategoryChip({ categoryId }) {
  const cat = getCategory(categoryId)

  // Si el backend devuelve una categoría desconocida, la
  // mostramos en gris neutro en vez de romper la interfaz.
  if (!cat) {
    return <span className="chip chip--unknown">{categoryId}</span>
  }

  return (
    <span
      className="chip"
      style={{
        // Los colores salen SIEMPRE de los tokens del catálogo
        background: `var(${cat.softToken})`,
        borderColor: `color-mix(in srgb, var(${cat.colorToken}) 35%, transparent)`,
      }}
    >
      <i className="chip__dot" style={{ background: `var(${cat.colorToken})` }} />
      {cat.label}
    </span>
  )
}
