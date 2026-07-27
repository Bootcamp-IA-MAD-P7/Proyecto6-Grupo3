// ============================================================
//  analysisService.js — Capa de acceso a datos (API)
// ------------------------------------------------------------
//  QUÉ HACE: es el ÚNICO punto del frontend que "habla" con
//  el backend. Los componentes NUNCA hacen fetch directamente;
//  siempre llaman a estas funciones.
//
//  CÓMO CONECTAR CON EL BACKEND (cuando esté listo):
//   1. Cambiar USE_MOCK a false.
//   2. Verificar el proxy '/api' en vite.config.js.
//   3. Ajustar los nombres de campos si la API difiere.
//
//  CONTRATO ESPERADO DEL BACKEND (propuesta):
//   POST /api/analyze        { url }  → AnalysisResult
//   GET  /api/analyses/recent         → RecentAnalysis[]
//   GET  /api/stats                   → GlobalStats
// ============================================================

import { MOCK_ANALYSIS, MOCK_RECENT, MOCK_STATS } from './mockData'

// 🔀 Interruptor mock ↔ API real
const USE_MOCK = true

/** Pequeña ayuda: simula la latencia de red en modo mock. */
const fakeDelay = (ms = 400) => new Promise((r) => setTimeout(r, ms))

/**
 * Analiza la política de privacidad de una URL.
 * @param {string} url — URL de la política a analizar
 * @returns {Promise<object>} resultado del análisis
 */
export async function analyzeUrl(url) {
  if (USE_MOCK) {
    await fakeDelay()
    // En mock devolvemos siempre el mismo análisis de ejemplo,
    // pero conservamos la URL que pidió el usuario.
    return { ...MOCK_ANALYSIS, requestedUrl: url }
  }
  const res = await fetch('/api/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  })
  if (!res.ok) throw new Error(`Error del servidor: ${res.status}`)
  return res.json()
}

/**
 * Devuelve los últimos análisis realizados (para la home
 * y, más adelante, para la extensión de Chrome).
 */
export async function getRecentAnalyses() {
  if (USE_MOCK) {
    await fakeDelay(150)
    return MOCK_RECENT
  }
  const res = await fetch('/api/analyses/recent')
  if (!res.ok) throw new Error(`Error del servidor: ${res.status}`)
  return res.json()
}

/** Devuelve las métricas globales del corpus y del modelo. */
export async function getGlobalStats() {
  if (USE_MOCK) {
    await fakeDelay(150)
    return MOCK_STATS
  }
  const res = await fetch('/api/stats')
  if (!res.ok) throw new Error(`Error del servidor: ${res.status}`)
  return res.json()
}
