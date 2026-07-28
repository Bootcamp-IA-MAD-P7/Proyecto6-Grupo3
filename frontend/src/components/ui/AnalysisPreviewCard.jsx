// ============================================================
//  AnalysisPreviewCard.jsx — Tarjeta flotante de análisis
// ------------------------------------------------------------
//  QUÉ HACE: la tarjeta inclinada de la home que muestra un
//  EJEMPLO de resultado de análisis (resumen IA + categorías
//  + evidencia). Es el "escaparate" del producto: el visitante
//  entiende qué hace PrivacyLens sin leer nada más.
//
//  DECISIÓN DE DISEÑO (documentada para el equipo):
//   · Turquesa → "RESUMEN DE LA IA" (la máquina habla)
//   · Ámbar    → "EVIDENCIA DEL DOCUMENTO" (el texto legal habla)
//
//  PROPS:
//   · analysis (object) — resultado con la forma de
//     MOCK_ANALYSIS (ver src/services/mockData.js)
// ============================================================
import CategoryChip from './CategoryChip'
import './AnalysisPreviewCard.css'

export default function AnalysisPreviewCard({ analysis }) {
  if (!analysis) return null

  return (
    <div className="preview">
      {/* Sombra/tarjeta decorativa detrás, ligeramente rotada */}
      <div className="preview__back" aria-hidden="true" />

      <article className="analysis-card">
        {/* --- Cabecera: empresa analizada + estado --- */}
        <header className="analysis-card__head">
          <div className="analysis-card__title">
            {/* Avatar monocromo: SIN colores corporativos de marca
                (decisión de identidad: solo habla la paleta PrivacyLens) */}
            <span className="analysis-card__logo">{analysis.company[0]}</span>
            <div>
              <h3>{analysis.company}</h3>
              <span className="analysis-card__domain">{analysis.url.replace('https://', '')}</span>
            </div>
          </div>
          <span className="analysis-card__badge">✓ Analizado</span>
        </header>

        {/* --- Resumen en lenguaje llano (voz de la IA: turquesa) --- */}
        <div className="analysis-card__summary">
          <small>RESUMEN DE LA IA</small>
          {analysis.summary}
        </div>

        {/* --- Categorías detectadas (cada una con su color) --- */}
        <div className="analysis-card__chips">
          {analysis.categories.map((id) => (
            <CategoryChip key={id} categoryId={id} />
          ))}
        </div>

        {/* --- Evidencia literal del documento (voz del texto: ámbar) --- */}
        <blockquote className="analysis-card__evidence">
          <small>EVIDENCIA DEL DOCUMENTO</small>
          {analysis.evidence.quote}
          <b>
            {analysis.evidence.section} · Ver en el documento →
          </b>
        </blockquote>
      </article>
    </div>
  )
}
