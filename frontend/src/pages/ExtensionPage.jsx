import { Link } from 'react-router-dom'
import './ExtensionPage.css'

export default function ExtensionPage() {
  return (
    <section className="extension-page container">
      <div className="extension-page__copy">
        <span className="page-heading__eyebrow">Extensión de Chrome</span>
        <h1>PrivacyLens, también mientras navegas.</h1>
        <p>
          La extensión reutilizará la experiencia de PrivacyLens para analizar políticas
          de privacidad sin abandonar la página que estás visitando.
        </p>
        <div className="extension-page__actions">
          <Link className="primary-link" to="/">Probar el analizador</Link>
          <span className="extension-page__status"><i /> En desarrollo</span>
        </div>
        <ul className="extension-page__features">
          <li>Lectura rápida de categorías</li>
          <li>Evidencias dentro del documento</li>
          <li>Resultado claro y orientativo</li>
        </ul>
      </div>

      <div className="browser-mockup" aria-label="Vista previa de la extensión de Chrome">
        <div className="browser-mockup__top">
          <div className="browser-mockup__dots"><i /><i /><i /></div>
          <div className="browser-mockup__address">empresa.com/privacidad</div>
          <span className="browser-mockup__lens">L</span>
        </div>
        <div className="browser-mockup__body">
          <div className="browser-mockup__document">
            <span />
            <span />
            <span />
            <span />
            <span />
          </div>
          <aside className="extension-card">
            <div className="extension-card__head">
              <span className="extension-card__mark">L</span>
              <div>
                <b>PrivacyLens</b>
                <small>Análisis completado</small>
              </div>
              <span className="extension-card__signal" />
            </div>
            <div className="extension-card__score">
              <span>Exposición estimada</span>
              <b>Media</b>
            </div>
            <div className="extension-card__result">
              <small>CATEGORÍA DETECTADA</small>
              <strong>Third Party Sharing</strong>
              <p>Se identifican referencias al intercambio de datos con terceros.</p>
            </div>
            <button type="button">Ver análisis completo</button>
          </aside>
        </div>
      </div>
    </section>
  )
}
