// ============================================================
//  App.jsx — Raíz de la aplicación y definición de rutas
// ------------------------------------------------------------
//  QUÉ HACE: monta la estructura común (fondos decorativos +
//  Navbar) y conecta cada URL con su página.
//
//  MAPA DE RUTAS:
//   /            → HomePage       (analizador — FASE 1 ✅)
//   /analisis    → AnalysisPage   (radiografía — FASE 2 🚧)
//   /modelo      → ModelPage      (métricas — FASE 3 🚧)
//   /categorias  → placeholder    (glosario — FASE 4 🚧)
//   /extension   → placeholder    (landing extensión — FASE 5 🚧)
//   *            → redirige a /
// ============================================================
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/layout/Navbar'
import HomePage from './pages/HomePage'
import AnalysisPage from './pages/AnalysisPage'
import ModelPage from './pages/ModelPage'
import PlaceholderPage from './pages/PlaceholderPage'

export default function App() {
  return (
    <BrowserRouter>
      {/* Fondos decorativos (definidos en styles/global.css) */}
      <div className="aurora" aria-hidden="true" />
      <div className="grid-bg" aria-hidden="true" />

      <Navbar />

      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/analisis" element={<AnalysisPage />} />
          <Route path="/modelo" element={<ModelPage />} />
          <Route
            path="/categorias"
            element={
              <PlaceholderPage title="Categorías">
                🚧 Glosario de las categorías de privacidad que detecta el modelo,
                explicadas en lenguaje llano. Disponible en la FASE 4.
              </PlaceholderPage>
            }
          />
          <Route
            path="/extension"
            element={
              <PlaceholderPage title="Extensión de Chrome">
                🚧 Aquí irá la página de descarga de la extensión. La extensión
                reutilizará los componentes de <code>src/components/ui</code>
                (UrlAnalyzerBox, CategoryChip, AnalysisPreviewCard).
              </PlaceholderPage>
            }
          />
          {/* Cualquier ruta desconocida vuelve a la home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </BrowserRouter>
  )
}
