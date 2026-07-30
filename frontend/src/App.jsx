import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/layout/Navbar'
import Footer from './components/layout/Footer'
import HomePage from './pages/HomePage'
import AnalysisPage from './pages/AnalysisPage'
import RisksPage from './pages/RisksPage'
import GdprPage from './pages/GdprPage'
import ModelPage from './pages/ModelPage'
import CategoriesPage from './pages/CategoriesPage'
import ExtensionPage from './pages/ExtensionPage'

export default function App() {
  return (
    <BrowserRouter>
      <div className="aurora" aria-hidden="true" />
      <div className="grid-bg" aria-hidden="true" />

      <Navbar />

      <main className="app-main">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/analisis" element={<AnalysisPage />} />
          <Route path="/riesgos" element={<RisksPage />} />
          <Route path="/rgpd" element={<GdprPage />} />
          <Route path="/modelo" element={<ModelPage />} />
          <Route path="/categorias" element={<CategoriesPage />} />
          <Route path="/extension" element={<ExtensionPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      <Footer />
    </BrowserRouter>
  )
}
