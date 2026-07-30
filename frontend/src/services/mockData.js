// ============================================================
//  mockData.js — Datos de ejemplo (MOCK)
// ------------------------------------------------------------
//  QUÉ HACE: conserva únicamente los datos simulados de
//  estadísticas e historial. Esos endpoints no existen en el
//  backend. El análisis principal siempre usa POST /api/analyze.
// ============================================================

/** Análisis recientes que se muestran en la home. */
export const MOCK_RECENT = [
  { company: 'Google',  initial: 'G', analyzedAt: 'Hace 1 h',  slug: 'google' },
  { company: 'Spotify', initial: 'S', analyzedAt: 'Hace 3 h',  slug: 'spotify' },
  { company: 'OpenAI',  initial: 'O', analyzedAt: 'Hace 5 h',  slug: 'openai' },
  { company: 'Booking', initial: 'B', analyzedAt: 'Hace 1 día', slug: 'booking' },
]

/** Métricas globales del corpus/modelo para la home. */
export const MOCK_STATS = [
  { value: '3.852',  label: 'documentos en el corpus' },
  { value: '48.210', label: 'párrafos etiquetados' },
  { value: '0,87',   label: 'F1 medio del modelo' },
  { value: 'RGPD',   label: 'artículos mapeados' },
]
