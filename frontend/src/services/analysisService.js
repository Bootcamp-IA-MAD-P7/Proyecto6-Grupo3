/// ============================================================
//  analysisService.js — Capa de acceso a datos (API)
// ------------------------------------------------------------
//  QUÉ HACE: es el ÚNICO punto del frontend que "habla" con
//  el backend. Los componentes NUNCA hacen fetch directamente;
//  siempre llaman a estas funciones.
//
//  ESTADO (30 jul): el ANÁLISIS ya usa la API real, con el
//  modelo multiclase conectado. Las estadísticas y el historial
//  siguen en mock a propósito: esos endpoints no existen en el
//  backend y no están previstos (ver MOCK_ONLY_ENDPOINTS).
//
//  CONTRATO REAL DEL BACKEND (specs/5_backend_contract.md):
//   POST /api/analyze   { url } o { text }  → contrato §9   ✅
//   GET  /api/health                        → { status }    ✅
// ============================================================

import { MOCK_RECENT, MOCK_STATS } from './mockData'

// Estos dos endpoints NO existen en el backend y no están previstos, así que
// su mock no es un interruptor temporal: es la implementación definitiva.
//   /api/analyses/recent → exigiría base de datos, y se decidió no tener
//     ninguna: la API es stateless, y no almacenar las políticas que la gente
//     analiza es coherente con el propósito del proyecto.
//   /api/stats → son las métricas del modelo, datos fijos del informe.
const MOCK_ONLY_ENDPOINTS = true

/** Pequeña ayuda: simula la latencia de red en modo mock. */
const fakeDelay = (ms = 400) => new Promise((r) => setTimeout(r, ms))

/**
 * Analiza la política de privacidad de una URL.
 * El backend descarga la página y extrae su texto (capa fetcher, con guardas
 * de SSRF). Si no consigue leerla, responde 4xx con un mensaje legible.
 * @param {string} url — URL de la política a analizar
 * @returns {Promise<object>} contrato §9: { model_version, stub, document, fragments }
 */
export async function analyzeUrl(url) {
  const res = await fetch('/api/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  })
  if (!res.ok) {
    // El backend responde { error: "<mensaje legible>" }: se muestra ese texto
    // en lugar de un código, para que el usuario sepa qué ocurrió.
    let message = `Error del servidor: ${res.status}`
    try {
      const body = await res.json()
      if (body?.error) message = body.error
      else if (typeof body?.detail === 'string') message = body.detail
    } catch {
      // respuesta sin JSON: se queda el mensaje genérico
    }
    throw new Error(message)
  }
  const body = await res.json()
  if (!body || typeof body !== 'object' || !body.document) {
    throw new Error('El servidor devolvió una respuesta de análisis incompleta.')
  }
  return body
}

/**
 * Devuelve los últimos análisis realizados (para la home
 * y, más adelante, para la extensión de Chrome).
 * Mock permanente: no hay base de datos (ver MOCK_ONLY_ENDPOINTS).
 */
export async function getRecentAnalyses() {
  if (MOCK_ONLY_ENDPOINTS) {
    await fakeDelay(150)
    return MOCK_RECENT
  }
  const res = await fetch('/api/analyses/recent')
  if (!res.ok) throw new Error(`Error del servidor: ${res.status}`)
  return res.json()
}

/** Devuelve las métricas globales del corpus y del modelo.
 *  Mock permanente: son datos fijos del informe, no vienen de la API. */
export async function getGlobalStats() {
  if (MOCK_ONLY_ENDPOINTS) {
    await fakeDelay(150)
    return MOCK_STATS
  }
  const res = await fetch('/api/stats')
  if (!res.ok) throw new Error(`Error del servidor: ${res.status}`)
  return res.json()
}
