// ============================================================
//  categories.js — Catálogo de categorías de privacidad
// ------------------------------------------------------------
//  QUÉ HACE: define las categorías que el modelo puede
//  detectar en una política de privacidad, con el color que
//  le corresponde en TODA la interfaz (chips, barras, matriz
//  de confusión, extensión…). Así una categoría siempre se
//  ve del mismo color en cualquier pantalla.
//
//  ⚠️ TODO(backend): la taxonomía definitiva sale del dataset
//  OPP-115 + PrivacyLens Extended (ver paragraph_predictions.csv
//  y privacy_insights.csv). Cuando el equipo de datos la
//  confirme, hay que alinear `id` y `label` con ella.
// ============================================================

export const CATEGORIES = [
  { id: 'cookies',           label: 'Cookies',                    colorToken: '--color-secondary', softToken: '--color-blue-soft' },
  { id: 'data_collection',   label: 'Data Collection',            colorToken: '--color-primary',   softToken: '--color-navy-soft' },
  { id: 'third_party',       label: 'Third Party Sharing',        colorToken: '--color-accent',    softToken: '--color-teal-soft' },
  { id: 'data_retention',    label: 'Data Retention',             colorToken: '--color-indigo',    softToken: '--color-indigo-soft' },
  { id: 'data_security',     label: 'Data Security',              colorToken: '--color-secondary', softToken: '--color-blue-soft' },
  { id: 'user_rights',       label: 'User Rights',                colorToken: '--color-amber',     softToken: '--color-amber-soft' },
  { id: 'intl_transfer',     label: 'International Transfer',     colorToken: '--color-primary',   softToken: '--color-navy-soft' },
  { id: 'children_privacy',  label: "Children's Privacy",         colorToken: '--color-accent',    softToken: '--color-teal-soft' },
  { id: 'tracking',          label: 'Tracking & Profiling',       colorToken: '--color-indigo',    softToken: '--color-indigo-soft' },
  { id: 'policy_change',     label: 'Policy Change',              colorToken: '--color-amber',     softToken: '--color-amber-soft' },
]

/** Devuelve la categoría por id (o undefined si no existe). */
export function getCategory(id) {
  return CATEGORIES.find((c) => c.id === id)
}
