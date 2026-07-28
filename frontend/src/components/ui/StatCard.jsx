// ============================================================
//  StatCard.jsx — Tarjeta de métrica grande
// ------------------------------------------------------------
//  QUÉ HACE: muestra un número destacado con su descripción
//  (documentos del corpus, F1 del modelo…). El filete de
//  color superior cambia según `tone`.
//
//  PROPS:
//   · value (string)  — el número/dato grande ("3.852")
//   · label (string)  — descripción ("documentos en el corpus")
//   · tone  ('primary' | 'secondary' | 'accent' | 'amber')
// ============================================================
import './StatCard.css'

export default function StatCard({ value, label, tone = 'primary' }) {
  return (
    <div className={`stat stat--${tone}`}>
      <b className="stat__value">{value}</b>
      <span className="stat__label">{label}</span>
    </div>
  )
}
