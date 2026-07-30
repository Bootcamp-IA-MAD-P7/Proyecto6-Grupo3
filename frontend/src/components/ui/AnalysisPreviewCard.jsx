import CategoryChip from './CategoryChip'
import './AnalysisPreviewCard.css'

const EXPOSURE_LABELS = {
  low: 'Exposición baja',
  medium: 'Exposición media',
  high: 'Exposición alta',
  unknown: 'Exposición desconocida',
}

function normalizeExposureLevel(level) {
  return Object.hasOwn(EXPOSURE_LABELS, level) ? level : 'unknown'
}

function formatCategoryId(id) {
  if (!id || typeof id !== 'string') return 'Categoría sin identificar'
  return id
    .split('_')
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

function hasNumericValue(value) {
  return value !== null && value !== undefined && value !== '' && Number.isFinite(Number(value))
}

function formatScore(value) {
  return hasNumericValue(value) ? Number(value).toFixed(3) : 'No disponible'
}

function categoryCoverage(fragmentCount, documentFragmentCount) {
  const count = Number(fragmentCount)
  const total = Number(documentFragmentCount)
  if (!Number.isFinite(count) || !Number.isFinite(total) || total <= 0) return 0
  return Math.max(0, (count / total) * 100)
}

function HomePlaceholder() {
  return (
    <div className="preview preview--placeholder" aria-label="Vista previa del análisis">
      <div className="preview__back" aria-hidden="true" />
      <article className="analysis-card">
        <header className="analysis-card__head">
          <div className="analysis-card__title">
            <span className="analysis-card__logo" aria-hidden="true">P</span>
            <div>
              <h3>PrivacyLens</h3>
              <span className="analysis-card__domain">Análisis de privacidad</span>
            </div>
          </div>
          <span className="analysis-card__badge">Preparado</span>
        </header>

        <div className="analysis-card__summary">
          <small>RESULTADO DEL ANÁLISIS</small>
          Introduce una política para consultar su exposición, categorías y fragmentos.
        </div>

        <div className="analysis-card__empty">
          El resultado real aparecerá aquí cuando solicites un análisis.
        </div>
      </article>
    </div>
  )
}

export default function AnalysisPreviewCard({ analysis, variant = 'result' }) {
  if (variant === 'placeholder') return <HomePlaceholder />
  if (!analysis || typeof analysis !== 'object') return null

  const document = analysis.document ?? {}
  const categories = Array.isArray(document.categories) ? document.categories : []
  const fragments = Array.isArray(analysis.fragments) ? analysis.fragments : []
  const fragmentCount = hasNumericValue(document.fragment_count)
    ? Number(document.fragment_count)
    : fragments.length
  const exposure = document.exposure ?? {}
  const exposureLevel = normalizeExposureLevel(exposure.level)

  return (
    <div className="preview preview--result">
      <div className="preview__back" aria-hidden="true" />

      <article className="analysis-card">
        <header className="analysis-card__head">
          <div className="analysis-card__title">
            <span className="analysis-card__logo" aria-hidden="true">P</span>
            <div>
              <h3>Resultado del análisis</h3>
              <span className="analysis-card__domain">
                {fragmentCount} {fragmentCount === 1 ? 'fragmento' : 'fragmentos'}
                {analysis.model_version ? ` · Modelo ${analysis.model_version}` : ''}
              </span>
            </div>
          </div>
          <span className="analysis-card__badge">✓ Analizado</span>
        </header>

        <section
          className={`analysis-card__exposure analysis-card__exposure--${exposureLevel}`}
          aria-labelledby="exposure-title"
        >
          <div>
            <small id="exposure-title">NIVEL DE EXPOSICIÓN</small>
            <strong>{EXPOSURE_LABELS[exposureLevel]}</strong>
          </div>
          {hasNumericValue(exposure.score) && (
            <span className="analysis-card__exposure-score">
              Score {Number(exposure.score).toFixed(2)}
            </span>
          )}
          <p>
            {exposure.disclaimer ||
              'El backend no ha proporcionado un aviso para este resultado.'}
          </p>
        </section>

        <section className="analysis-card__section" aria-labelledby="categories-title">
          <div className="analysis-card__section-head">
            <div>
              <small>CATEGORÍAS</small>
              <h4 id="categories-title">Temas detectados en la política</h4>
            </div>
            <span>{categories.length} recibidas</span>
          </div>

          {categories.length > 0 ? (
            <div className="analysis-card__categories">
              {categories.map((category, index) => {
                const coverage = categoryCoverage(category?.fragment_count, fragmentCount)
                const usefulGdprReference =
                  typeof category?.gdpr_reference === 'string' &&
                  category.gdpr_reference.trim() &&
                  category.gdpr_reference.trim().toUpperCase() !== 'TODO'

                return (
                  <article
                    className="analysis-category"
                    key={`${category?.id ?? 'category'}-${index}`}
                  >
                    <div className="analysis-category__title">
                      <CategoryChip categoryId={category?.id || 'unknown'} />
                      <span
                        className={`analysis-category__presence ${
                          category?.present ? 'is-present' : ''
                        }`}
                      >
                        {category?.present ? 'Presente' : 'No presente'}
                      </span>
                    </div>
                    <h5>{formatCategoryId(category?.id)}</h5>
                    <div className="analysis-category__coverage">
                      <span style={{ width: `${Math.min(coverage, 100)}%` }} />
                    </div>
                    <p>
                      <strong>{coverage.toFixed(1)}%</strong> de la política dedicado a este
                      tema
                    </p>
                    <dl>
                      <div>
                        <dt>Fragmentos</dt>
                        <dd>
                          {hasNumericValue(category?.fragment_count)
                            ? Number(category.fragment_count)
                            : 0}
                        </dd>
                      </div>
                      <div>
                        <dt>Valor de confianza</dt>
                        <dd>{formatScore(category?.confidence)}</dd>
                      </div>
                    </dl>
                    {usefulGdprReference && (
                      <p className="analysis-category__gdpr">
                        RGPD: {category.gdpr_reference}
                      </p>
                    )}
                  </article>
                )
              })}
            </div>
          ) : (
            <p className="analysis-card__empty">
              No se han recibido categorías para este análisis.
            </p>
          )}
        </section>

        <section className="analysis-card__section" aria-labelledby="fragments-title">
          <div className="analysis-card__section-head">
            <div>
              <small>FRAGMENTOS</small>
              <h4 id="fragments-title">Evidencias del documento</h4>
            </div>
            <span>{fragments.length} recibidos</span>
          </div>

          {fragments.length > 0 ? (
            <div className="analysis-card__fragments">
              {fragments.map((fragment, index) => {
                const labels = Array.isArray(fragment?.labels) ? fragment.labels : []
                return (
                  <article className="analysis-fragment" key={fragment?.id ?? index}>
                    <div className="analysis-fragment__meta">
                      <strong>Fragmento {fragment?.id ?? index}</strong>
                      <span>
                        Posiciones{' '}
                        {hasNumericValue(fragment?.start) ? fragment.start : '—'}
                        {' – '}
                        {hasNumericValue(fragment?.end) ? fragment.end : '—'}
                      </span>
                    </div>
                    <blockquote>{fragment?.text || 'Fragmento sin texto.'}</blockquote>
                    {labels.length > 0 ? (
                      <div className="analysis-fragment__labels">
                        {labels.map((label, labelIndex) => (
                          <div key={`${label?.id ?? 'label'}-${labelIndex}`}>
                            <CategoryChip categoryId={label?.id || 'unknown'} />
                            <span>Score {formatScore(label?.score)}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="analysis-fragment__empty">Sin etiquetas asociadas.</p>
                    )}
                  </article>
                )
              })}
            </div>
          ) : (
            <p className="analysis-card__empty">
              No se han recibido fragmentos para este análisis.
            </p>
          )}
        </section>
      </article>
    </div>
  )
}
