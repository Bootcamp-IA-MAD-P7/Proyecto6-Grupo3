import React from 'react'
import './AnalysisPreviewCard.css'

// Mapeo de IDs de categorías del backend a textos legibles
const CATEGORY_LABELS = {
  first_party_collection_use: 'Recolección y Uso (Primera parte)',
  third_party_sharing_collection: 'Compartición con Terceros',
  user_choice_control: 'Control del Usuario',
  user_access_edit_deletion: 'Acceso y Supresión',
  data_retention: 'Retención de Datos',
  data_security: 'Seguridad de Datos',
  policy_change: 'Cambios de Política',
  do_not_track: 'Do Not Track',
  international_specific_audiences: 'Audiencias Internacionales',
  Other: 'Otros'
}



export default function AnalysisPreviewCard({ analysis }) {
  console.log('🔍 [API COMPLETA RECIBIDA EN COMPONENTE]:', analysis) //este codigo sirve para probar si trae el backend inspeccionando
 
  // 1. Si no hay objeto de análisis, no renderizar nada
  if (!analysis) return null

  // 2. Extracción ultra-segura con fallbacks (evita que cualquier campo sea undefined)
  const documentData = analysis?.document || {}
  const exposure = documentData?.exposure || analysis?.exposure || {}
  const rawCategories = documentData?.categories || analysis?.categories || []
  const fragments = analysis?.fragments || []

  

  // 3. Filtrar solo las categorías activas (si viene formato objeto API real)
  // O mantenerlas si vienen como un array de strings (formato mock antiguo)
  const activeCategories = Array.isArray(rawCategories)
    ? rawCategories.filter((cat) => (typeof cat === 'object' ? cat?.present === true : true))
    : []

  // 4. Obtención segura del primer fragmento (Línea 34 blindada)
  const firstFragment = Array.isArray(fragments) && fragments.length > 0 ? fragments[0] : null
  const firstLabel = firstFragment?.labels?.[0]?.id || ''

  const riskLevel = exposure?.level || 'low'
  const score = exposure?.score ?? 0
  const disclaimer = exposure?.disclaimer || ''
 
  
  return (
    <div className={`analysis-card risk-${riskLevel}`}>
      <div className="analysis-card__header">
        <h2>
          Nivel de Riesgo: <span className="risk-tag">{String(riskLevel).toUpperCase()}</span>
        </h2>
        <span className="analysis-card__score">Score: {score}</span>
      </div>

      {disclaimer && <p className="analysis-card__disclaimer">{disclaimer}</p>}

      <div className="analysis-card__categories">
        <h3>Categorías Detectadas ({activeCategories.length})</h3>
        {activeCategories.length === 0 ? (
          <p>No se detectaron categorías de riesgo.</p>
        ) : (
          <ul className="category-tags">
            {activeCategories.map((cat, index) => {
              const catId = typeof cat === 'object' ? cat?.id : cat
              const confidence = typeof cat === 'object' ? cat?.confidence : null

              return (
                <li key={catId || index} className="category-tag-item">
                  <span className="category-name">
                    {CATEGORY_LABELS[catId] || catId}
                  </span>
                  {confidence !== null && confidence !== undefined && (
                    <span className="category-confidence">
                      ({(confidence * 100).toFixed(0)}%)
                    </span>
                  )}
                </li>
              )
            })}
          </ul>
        )}
      </div>

      {firstFragment?.text && (
        <div className="analysis-card__evidence">
          <h4>Evidencia destacada:</h4>
          <blockquote>"{firstFragment.text}"</blockquote>
          {firstLabel && <small>Categoría: {CATEGORY_LABELS[firstLabel] || firstLabel}</small>}
        </div>
      )}
    </div>
  )
}