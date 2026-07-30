// ============================================================
//  Navbar.jsx — Barra de navegación flotante (glassmorphism)
// ------------------------------------------------------------
//  QUÉ HACE: cabecera común a todas las páginas. Usa
//  react-router (<NavLink>) para marcar la página activa.
//  Es "sticky": queda fija arriba con efecto cristal.
// ============================================================
import { NavLink } from 'react-router-dom'
import Logo from '../brand/Logo'
import './Navbar.css'

export default function Navbar() {
  return (
    <nav className="navbar">
      {/* Logo + nombre: enlaza a la home */}
      <NavLink to="/" className="navbar__brand">
        <Logo size={30} wordmark />
      </NavLink>

      <div className="navbar__links">
        <NavLink to="/" end className="navbar__link">
          Analizador
        </NavLink>
        <NavLink to="/riesgos" className="navbar__link">
          Riesgos
        </NavLink>
        <NavLink to="/rgpd" className="navbar__link">
          RGPD
        </NavLink>
        <NavLink to="/aprende" className="navbar__link">
          Aprende
        </NavLink>
        <NavLink to="/modelo" className="navbar__link">
          Modelo
        </NavLink>
        <NavLink to="/categorias" className="navbar__link">
          Categorías
        </NavLink>
        {/* CTA destacado: lleva a la página de la extensión */}
        <NavLink to="/extension" className="navbar__cta">
          Extensión de Chrome
        </NavLink>
      </div>
    </nav>
  )
}
