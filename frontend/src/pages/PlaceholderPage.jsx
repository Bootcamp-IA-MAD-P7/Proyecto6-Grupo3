// ============================================================
//  PlaceholderPage.jsx — Página genérica "en construcción"
// ------------------------------------------------------------
//  QUÉ HACE: da una respuesta elegante a las rutas que aún
//  no tienen página propia (/categorias, /extension), para
//  que la navegación nunca rompa durante el desarrollo.
//  Se eliminará cuando esas páginas existan de verdad.
// ============================================================
import './ModelPage.css' // reutiliza los estilos de cabecera de página

export default function PlaceholderPage({ title, children }) {
  return (
    <section className="model-page container">
      <h1 className="model-page__title">{title}</h1>
      <p className="model-page__todo">{children}</p>
    </section>
  )
}
