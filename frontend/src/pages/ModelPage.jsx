// ============================================================
//  ModelPage.jsx — Página "El modelo, explicado"
// ------------------------------------------------------------
//  ESTADO: ESQUELETO (FASE 3 del roadmap).
//
//  QUÉ HARÁ: explicar el modelo "para humanos":
//   · Métricas del corpus (StatCards, ya disponibles)
//   · F1 por categoría como barras horizontales
//   · Matriz de confusión visual con tooltips en lenguaje llano
//
//  DATOS FUTUROS: saldrán de los artefactos del backend
//  (validation_report.json, paragraph_predictions.csv…).
//  Cuando el equipo de datos los exponga vía API, esta página
//  los consumirá a través de analysisService.
// ============================================================
import StatCard from '../components/ui/StatCard'
import { MOCK_STATS } from '../services/mockData'
import './ModelPage.css'

export default function ModelPage() {
  return (
    <section className="model-page container">
      <h1 className="model-page__title">El modelo, explicado</h1>
      <p className="model-page__sub">
        Sin tablas crípticas. Así de bien entiende PrivacyLens cada categoría.
      </p>

      <div className="model-page__stats">
        {MOCK_STATS.map((s) => (
          <StatCard key={s.label} value={s.value} label={s.label} />
        ))}
      </div>

      {/* TODO(FASE 3): barras de F1 por categoría + matriz de
          confusión interactiva, alimentadas por la API real. */}
      <p className="model-page__todo">
        🚧 Las gráficas de rendimiento se activarán cuando el backend exponga
        las métricas de validación del modelo.
      </p>
    </section>
  )
}
