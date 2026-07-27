// ============================================================
//  mockData.js — Datos de ejemplo (MOCK)
// ------------------------------------------------------------
//  QUÉ HACE: alimenta la interfaz mientras el backend de
//  inferencia no está disponible. TODOS los datos de este
//  archivo son ficticios y existen solo para desarrollo.
//
//  ⚠️ Cuando el equipo de backend entregue la API, estos
//  datos dejarán de usarse automáticamente al cambiar
//  USE_MOCK a false en analysisService.js. NINGÚN componente
//  importa este archivo directamente: siempre pasan por el
//  servicio. Así el cambio a datos reales es transparente.
// ============================================================

/** Análisis de ejemplo (el que se muestra en la tarjeta flotante de la home). */
export const MOCK_ANALYSIS = {
  company: 'Spotify',
  url: 'https://spotify.com/legal/privacy-policy',
  analyzedAt: 'hace 2 min',
  summary:
    'Describe prácticas habituales: comparte datos con proveedores, usa cookies de seguimiento y explica cómo ejercer tus derechos.',
  categories: ['cookies', 'third_party', 'data_retention', 'user_rights'],
  evidence: {
    quote: '“We share information with third-party service providers...”',
    section: 'Apartado 4.2',
    categoryId: 'third_party',
  },
  gdprArticles: ['Art. 6', 'Art. 13', 'Art. 14'],
}

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
