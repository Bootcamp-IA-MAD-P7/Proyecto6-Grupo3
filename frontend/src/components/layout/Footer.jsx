import { Link, NavLink } from 'react-router-dom'
import Logo from '../brand/Logo'
import './Footer.css'

const PROJECT_REPOSITORY_URL =
  'https://github.com/Bootcamp-IA-MAD-P7/Proyecto6-Grupo3'

const INTERNAL_LINKS = [
  { to: '/', label: 'Analizador', end: true },
  { to: '/riesgos', label: 'Riesgos' },
  { to: '/rgpd', label: 'RGPD' },
  { to: '/aprende', label: 'Aprende' },
  { to: '/modelo', label: 'PrivacyLens Lab' },
  { to: '/categorias', label: 'Categorías' },
  { to: '/extension', label: 'Extensión de Chrome' },
]

const EXTERNAL_LINKS = [
  {
    href: 'https://www.aepd.es/',
    label: 'Agencia Española de Protección de Datos',
  },
  {
    href: 'https://www.incibe.es/ciudadania',
    label: 'INCIBE Ciudadanía',
  },
  {
    href: PROJECT_REPOSITORY_URL,
    label: 'GitHub del proyecto',
  },
]

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer__inner container">
        <section className="footer__brand" aria-labelledby="footer-brand-title">
          <Link to="/" className="footer__logo" aria-label="PrivacyLens, volver al inicio">
            <Logo size={30} variant="light" wordmark />
          </Link>
          <h2 id="footer-brand-title">Comprende antes de aceptar.</h2>
          <p>
            PrivacyLens utiliza inteligencia artificial para ayudar a comprender qué ocurre
            con los datos personales dentro de una política de privacidad.
          </p>
        </section>

        <nav className="footer__column footer__nav" aria-label="Navegación del pie">
          <h2>Navegación</h2>
          <div className="footer__links">
            {INTERNAL_LINKS.map((link) => (
              <NavLink to={link.to} end={link.end} key={link.to}>
                {link.label}
              </NavLink>
            ))}
          </div>
        </nav>

        <section className="footer__column footer__resources" aria-labelledby="footer-resources-title">
          <h2 id="footer-resources-title">Recursos</h2>
          <div className="footer__links">
            {EXTERNAL_LINKS.map((link) => (
              <a
                href={link.href}
                target="_blank"
                rel="noopener noreferrer"
                key={link.href}
              >
                <span>{link.label}</span>
                <span className="footer__external-icon" aria-hidden="true">↗</span>
              </a>
            ))}
          </div>
        </section>

        <section className="footer__column footer__project" aria-labelledby="footer-project-title">
          <h2 id="footer-project-title">Proyecto</h2>
          <p>
            Proyecto educativo desarrollado durante el Bootcamp de IA y Machine Learning de
            Factoría F5.
          </p>
          <p className="footer__disclaimer">
            Los resultados son orientativos y no constituyen asesoramiento jurídico.
          </p>
          <span className="footer__copyright">© 2026 PrivacyLens</span>
        </section>
      </div>
    </footer>
  )
}
