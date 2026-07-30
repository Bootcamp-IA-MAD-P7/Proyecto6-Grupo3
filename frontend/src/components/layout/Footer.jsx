import { NavLink } from 'react-router-dom'
import Logo from '../brand/Logo'
import './Footer.css'

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer__inner container">
        <div className="footer__brand">
          <Logo size={30} variant="light" wordmark />
          <p>Proyecto educativo desarrollado en Factoría F5</p>
        </div>

        <nav className="footer__nav" aria-label="Navegación del pie">
          <NavLink to="/">Analizador</NavLink>
          <NavLink to="/modelo">Modelo</NavLink>
          <NavLink to="/categorias">Categorías</NavLink>
          <NavLink to="/extension">Extensión de Chrome</NavLink>
        </nav>

        <div className="footer__legal">
          <p>Los resultados son orientativos y no constituyen asesoramiento jurídico</p>
          <span>© 2026 PrivacyLens</span>
        </div>
      </div>
    </footer>
  )
}
