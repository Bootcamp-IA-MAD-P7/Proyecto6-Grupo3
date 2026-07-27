// ============================================================
//  RecentAnalyses.jsx — Lista de análisis recientes
// ------------------------------------------------------------
//  QUÉ HACE: muestra las últimas políticas analizadas como
//  tarjetas clicables. Los avatares son monocromos con tintes
//  de la paleta (rotando por posición) — NUNCA colores de
//  marca de terceros (decisión de identidad del equipo).
//
//  PROPS:
//   · items (array) — [{ company, initial, analyzedAt, slug }]
//   · onSelect(slug) — callback al hacer clic en una tarjeta
// ============================================================
import './RecentAnalyses.css'

export default function RecentAnalyses({ items = [], onSelect }) {
  return (
    <section className="recent container">
      <h2 className="recent__title">ANÁLISIS RECIENTES</h2>

      <div className="recent__grid">
        {items.map((item, index) => (
          <button
            key={item.slug}
            type="button"
            className="rcard"
            data-tint={index % 4} /* rota 4 tintes de la paleta */
            onClick={() => onSelect?.(item.slug)}
          >
            <span className="rcard__logo">{item.initial}</span>
            <span className="rcard__info">
              <h4>{item.company}</h4>
              <span>{item.analyzedAt}</span>
            </span>
            <span className="rcard__arrow">→</span>
          </button>
        ))}
      </div>
    </section>
  )
}
