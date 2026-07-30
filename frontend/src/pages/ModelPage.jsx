import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import labIllustration from '../../privaylens lab.jpg'
import './ModelPage.css'

const LABELS = [
  'first_party_collection_use',
  'third_party_sharing_collection',
  'user_choice_control',
  'user_access_edit_deletion',
  'data_retention',
  'data_security',
  'policy_change',
  'do_not_track',
  'international_specific_audiences',
]

const MULTICLASS_RESULTS = [
  { model: 'LogisticRegression', accuracy: 0.7202, macro: 0.7121, train: 0.9020, gap: 0.1899 },
  { model: 'LinearSVC', accuracy: 0.7237, macro: 0.7054, train: 0.9850, gap: 0.2796 },
  { model: 'ComplementNB', accuracy: 0.7461, macro: 0.7118, train: 0.8896, gap: 0.1778 },
]

const COMPLEMENT_NB_F1 = [
  ['Third-party sharing', 0.8308],
  ['Data retention', 0.6429],
  ['Do not track', 0.7273],
  ['Access, edit & deletion', 0.5957],
  ['User choice & control', 0.5932],
  ['Data security', 0.7812],
  ['International & audiences', 0.7407],
  ['Policy change', 0.8136],
  ['First-party collection', 0.7672],
  ['Other', 0.6250],
]

const LIGHTGBM_RESULTS = [
  ['first_party_collection_use', 0.7939, 232],
  ['third_party_sharing_collection', 0.8030, 200],
  ['user_choice_control', 0.6146, 103],
  ['user_access_edit_deletion', 0.5000, 39],
  ['data_retention', 0.4706, 22],
  ['data_security', 0.6200, 59],
  ['policy_change', 0.6857, 37],
  ['do_not_track', 1.0000, 6],
  ['international_specific_audiences', 0.7963, 61],
]

const TRAINING_STEPS = [
  ['01', 'Inspección', '01_inspect_opp115.py comprueba textos y anotaciones del corpus.'],
  ['02', 'Target', '02_build_target.py crea training_table.csv con nueve columnas binarias.'],
  ['03', 'Evaluación externa', '03_prepare_evaluation_set.py prepara español e inglés sin mezclarlos con train.'],
  ['04', 'Partición', '04_build_split.py asigna políticas completas con semilla 42.'],
  ['05', 'Vectorización', '05_vectorize.py ajusta TF-IDF solo con train y transforma los tres splits.'],
  ['06', 'Validación básica', '06_smoke_test.py comprueba train y validación.'],
  ['07', 'Modelado', 'linear_svc.py busca TF-IDF, C, pesos y algoritmo usando solo train/validation.'],
  ['08', 'Guardado', 'Solo una configuración con gap macro-F1 ≤ 0,05 puede guardarse como definitiva.'],
]

const PIPELINE_STEPS = [
  ['01', 'Entrada', 'El endpoint acepta texto o una URL.', 'ready'],
  ['02', 'Obtención', 'Las URLs se descargan con límites, validación de red y protección SSRF.', 'ready'],
  ['03', 'Idioma', 'Una heurística distingue inglés y español.', 'ready'],
  ['04', 'Traducción', 'Opus-MT está integrado, pero el presupuesto actual está fijado en 0 segundos.', 'partial'],
  ['05', 'Fragmentación', 'El original se divide por párrafos conservando start y end.', 'ready'],
  ['06', 'TF-IDF', 'El vectorizador versionado transforma cada fragmento.', 'ready'],
  ['07', 'Clasificación', 'El backend actual usa ComplementNB multiclase y elige una clase por argmax.', 'ready'],
  ['08', 'Agregación', 'Cuenta cuántos fragmentos gana cada categoría.', 'ready'],
  ['09', 'Exposición', 'Combina proporciones y pesos; los umbrales siguen marcados como provisionales.', 'partial'],
  ['10', 'Respuesta', 'Devuelve documento, categorías, fragmentos y scores al frontend.', 'ready'],
]

const LAB_MODULES = [
  {
    id: 'model',
    icon: '🤖',
    title: 'El modelo',
    description: 'Cómo funciona el algoritmo que clasifica cada fragmento.',
    action: 'Explorar',
  },
  {
    id: 'performance',
    icon: '📊',
    title: 'Rendimiento',
    description: 'Conoce las métricas obtenidas durante la evaluación del modelo.',
    action: 'Ver métricas',
  },
  {
    id: 'training',
    icon: '⚙️',
    title: 'Entrenamiento',
    description: 'Cómo se prepararon los datos antes del aprendizaje.',
    action: 'Descubrir',
  },
  {
    id: 'dataset',
    icon: '📚',
    title: 'Dataset',
    description: 'Información sobre OPP-115 y el conjunto de entrenamiento.',
    action: 'Más información',
  },
  {
    id: 'pipeline',
    icon: '🔄',
    title: 'Pipeline',
    description: 'Paso a paso del proceso seguido desde una política hasta el resultado.',
    action: 'Ver proceso',
  },
]

function MetricCard({ value, label, note }) {
  return (
    <article className="lab-metric">
      <strong>{value}</strong>
      <span>{label}</span>
      {note && <small>{note}</small>}
    </article>
  )
}

function ScoreBar({ label, value }) {
  return (
    <div className="lab-score">
      <div><span>{label}</span><strong>{value.toFixed(4)}</strong></div>
      <div className="lab-score__track"><i style={{ width: `${value * 100}%` }} /></div>
    </div>
  )
}

function ModelModule() {
  return (
    <>
      <div className="lab-detail__lead">
        <div>
          <span className="lab-eyebrow">DOS ENFOQUES VERIFICABLES</span>
          <h3>Del experimento multietiqueta al modelo servido</h3>
        </div>
        <p>
          El repositorio conserva un LinearSVC multietiqueta completo, pero la API actual
          sirve un <strong>ComplementNB multiclase</strong>. Esta diferencia es importante:
          describimos el trabajo realizado sin presentar el experimento como producción.
        </p>
      </div>

      <div className="lab-columns">
        <article className="lab-info-card">
          <span className="lab-info-card__tag">EXPERIMENTO PRINCIPAL</span>
          <h4>LinearSVC + One-vs-Rest</h4>
          <p>
            TF-IDF convierte cada fragmento en números. One-vs-Rest entrena nueve
            clasificadores independientes: cada uno responde si su categoría está presente.
            Así un fragmento puede recibir varias etiquetas.
          </p>
          <ul>
            <li>Entrada: texto de un fragmento.</li>
            <li>Representación: unigramas y bigramas TF-IDF.</li>
            <li>Salida: nueve predicciones binarias.</li>
            <li>Probabilidades: calibración sigmoide cuando se solicita.</li>
          </ul>
        </article>
        <article className="lab-info-card lab-info-card--accent">
          <span className="lab-info-card__tag">BACKEND ACTUAL</span>
          <h4>ComplementNB multiclase</h4>
          <p>
            El backend carga `multiclass_complementnb.joblib`. Las nueve prácticas compiten
            con `Other` y gana una sola clase por fragmento mediante argmax.
          </p>
          <ul>
            <li>Probabilidades nativas mediante `predict_proba`.</li>
            <li>Orden de columnas validado contra las clases entrenadas.</li>
            <li>Modelo y vectorizador se cargan una sola vez.</li>
            <li>Elección documentada por empate técnico y menor sobreajuste.</li>
          </ul>
        </article>
      </div>

      <section className="lab-subsection">
        <h4>Configuración real de LinearSVC</h4>
        <div className="lab-tech-grid">
          <span><b>Semilla</b>42</span>
          <span><b>C evaluados</b>0.0001 → 1.0</span>
          <span><b>Pesos</b>None / balanced</span>
          <span><b>TF-IDF base</b>min_df 3 · max_df 0.90</span>
          <span><b>N-gramas</b>(1, 2)</span>
          <span><b>Umbral guardado</b>0.5 para las 9 etiquetas</span>
        </div>
      </section>

      <section className="lab-subsection">
        <h4>Categorías técnicas</h4>
        <div className="lab-code-list">
          {LABELS.map((label) => <code key={label}>{label}</code>)}
          <code className="is-secondary">Other · solo enfoque multiclase</code>
        </div>
      </section>

      <aside className="lab-note">
        <strong>Ventaja:</strong> los modelos lineales y probabilísticos son rápidos,
        explicables y adecuados para texto disperso. <strong>Limitación:</strong> TF-IDF no
        comprende contexto profundo; las clases están desbalanceadas y la conversión
        multiclase descarta coocurrencias reales.
      </aside>
    </>
  )
}

function PerformanceModule() {
  return (
    <>
      <div className="lab-detail__lead">
        <div><span className="lab-eyebrow">VALIDACIÓN VERSIONADA</span><h3>Resultados sin abrir test</h3></div>
        <p>
          La tabla procede de `reports/multiclass_comparison.csv`. Se entrenó con train y se
          seleccionó con validation; el conjunto test no aparece en estas cifras.
        </p>
      </div>

      <div className="lab-metrics">
        <MetricCard value="0,7461" label="Mejor accuracy val" note="ComplementNB" />
        <MetricCard value="0,7121" label="Mejor macro-F1 val" note="LogisticRegression" />
        <MetricCard value="0,1778" label="Menor gap macro" note="ComplementNB" />
        <MetricCard value="0,3454" label="Suelo de accuracy" note="Clase mayoritaria" />
      </div>

      <div className="lab-table-wrap">
        <table className="lab-table">
          <thead><tr><th>Modelo</th><th>Accuracy val</th><th>Macro-F1 val</th><th>Macro-F1 train</th><th>Gap</th></tr></thead>
          <tbody>
            {MULTICLASS_RESULTS.map((row) => (
              <tr key={row.model}>
                <th>{row.model}</th><td>{row.accuracy.toFixed(4)}</td>
                <td>{row.macro.toFixed(4)}</td><td>{row.train.toFixed(4)}</td><td>{row.gap.toFixed(4)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <section className="lab-subsection">
        <h4>F1 por clase · ComplementNB multiclase</h4>
        <div className="lab-score-grid">
          {COMPLEMENT_NB_F1.map(([label, value]) => <ScoreBar key={label} label={label} value={value} />)}
        </div>
      </section>

      <section className="lab-subsection">
        <h4>Soporte disponible · experimento LightGBM multietiqueta</h4>
        <div className="lab-table-wrap">
          <table className="lab-table lab-table--compact">
            <thead><tr><th>Etiqueta</th><th>F1 validation</th><th>Positivos en validation</th></tr></thead>
            <tbody>
              {LIGHTGBM_RESULTS.map(([label, f1, support]) => (
                <tr key={label}><th><code>{label}</code></th><td>{f1.toFixed(4)}</td><td>{support}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="lab-caption">
          `do_not_track` obtiene 1,0000 sobre solo 6 positivos: el propio informe advierte
          que no es una cifra robusta. LightGBM registra macro-F1 validation 0,6982,
          micro-F1 0,7343 y gap 0,2808.
        </p>
      </section>

      <aside className="lab-note lab-note--warning">
        No hay un informe versionado con la tabla completa de la última búsqueda de
        `linear_svc.py`; por eso no se reproducen cifras recordadas de ejecuciones locales.
      </aside>
    </>
  )
}

function TrainingModule() {
  return (
    <>
      <div className="lab-detail__lead">
        <div><span className="lab-eyebrow">PROCESO REPRODUCIBLE</span><h3>Entrenamiento por políticas, no por filas</h3></div>
        <p>
          Una política completa pertenece a un único split. Esto evita que fragmentos casi
          iguales de la misma empresa aparezcan a la vez en entrenamiento y validación.
        </p>
      </div>

      <div className="lab-metrics">
        <MetricCard value="2.550" label="Fragmentos train" note="80 políticas" />
        <MetricCard value="579" label="Fragmentos validation" note="17 políticas" />
        <MetricCard value="663" label="Fragmentos test" note="18 políticas" />
        <MetricCard value="42" label="Semilla del split" note="70 / 15 / 15" />
      </div>

      <div className="lab-process">
        {TRAINING_STEPS.map(([number, title, text]) => (
          <article key={number}><span>{number}</span><div><h4>{title}</h4><p>{text}</p></div></article>
        ))}
      </div>

      <div className="lab-columns">
        <article className="lab-info-card">
          <h4>Búsqueda de hiperparámetros</h4>
          <p>
            El script compara LinearSVC y LogisticRegression, dos opciones de
            `class_weight`, diez valores de C y variantes de min_df, max_df, n-gramas,
            límite de features y sublinear_tf.
          </p>
        </article>
        <article className="lab-info-card">
          <h4>Umbrales y artefactos</h4>
          <p>
            El payload guarda modelo, vectorizador, clases, métricas y un array de
            umbrales. El código actual lo rellena con 0,5 para las nueve etiquetas; no hay
            ajuste individual versionado.
          </p>
        </article>
      </div>

      <aside className="lab-note">
        No existe una deduplicación explícita dentro de `02_build_target.py`. El split por
        política reduce la fuga entre grupos, pero no equivale a deduplicar el corpus.
      </aside>
    </>
  )
}

function DatasetModule() {
  return (
    <>
      <div className="lab-detail__lead">
        <div><span className="lab-eyebrow">FUENTE ACADÉMICA</span><h3>OPP-115 es el dataset principal</h3></div>
        <p>
          Fue creado por Wilson y colaboradores y presentado en ACL 2016. Reúne políticas
          web en inglés anotadas por especialistas mediante la taxonomía OPP-115.
        </p>
      </div>

      <div className="lab-metrics">
        <MetricCard value="115" label="Políticas OPP-115" />
        <MetricCard value="3.792" label="Fragmentos finales" />
        <MetricCard value="9" label="Etiquetas binarias" />
        <MetricCard value="Inglés" label="Idioma de entrenamiento" />
      </div>

      <div className="lab-columns">
        <article className="lab-info-card">
          <span className="lab-info-card__tag">ENTRENAMIENTO ACTUAL</span>
          <h4>OPP-115 procesado</h4>
          <p>
            `02_build_target.py` cruza HTML saneado con anotaciones consolidadas al umbral
            0,75. Cada fila conserva policy, segment, text y nueve indicadores 0/1.
          </p>
          <ul>
            <li>Permite varias etiquetas por fragmento.</li>
            <li>`Other` equivale a las nueve columnas a cero.</li>
            <li>La pareja policy + segment es la clave.</li>
            <li>No hay deduplicación explícita en el constructor.</li>
          </ul>
        </article>
        <article className="lab-info-card lab-info-card--accent">
          <span className="lab-info-card__tag">EVALUACIÓN Y DEMO</span>
          <h4>PrivacyLens Extended Dataset 2026</h4>
          <p>
            33 políticas actuales de fuentes oficiales, segmentadas y preanotadas por
            reglas en español e inglés. Sus etiquetas son de plata y requieren revisión.
          </p>
          <ul>
            <li>10.797 párrafos · 16 sectores.</li>
            <li>21 políticas en español y 12 en inglés.</li>
            <li>3.434 duplicados exactos intradocumento declarados.</li>
            <li>No se incorpora al entrenamiento actual.</li>
          </ul>
        </article>
      </div>

      <aside className="lab-note lab-note--warning">
        La extensión se transforma en `evaluation_es.csv` y `evaluation_en.csv`. No forma
        parte de train, validation ni test de OPP-115 y no debe tratarse como gold standard
        sin validación humana.
      </aside>
    </>
  )
}

function PipelineModule() {
  return (
    <>
      <div className="lab-detail__lead">
        <div><span className="lab-eyebrow">DE LA POLÍTICA A LA INTERFAZ</span><h3>Pipeline extremo a extremo</h3></div>
        <p>
          El flujo conserva el texto original y sus posiciones. La traducción, cuando se
          usa, es interna: nunca sustituye los fragmentos que recibe el frontend.
        </p>
      </div>

      <div className="lab-pipeline" role="list">
        {PIPELINE_STEPS.map(([number, title, text, status]) => (
          <article className={`lab-pipeline__step is-${status}`} key={number} role="listitem">
            <span className="lab-pipeline__number">{number}</span>
            <div><h4>{title}</h4><p>{text}</p></div>
            <small>{status === 'ready' ? 'Implementado' : 'Parcial / provisional'}</small>
          </article>
        ))}
      </div>

      <aside className="lab-note lab-note--warning">
        El motor Opus-MT está programado, pero `TIME_BUDGET_SECONDS = 0.0`; en la práctica
        los fragmentos españoles pueden continuar sin traducir. Los umbrales del semáforo
        también figuran como provisionales en el código.
      </aside>
    </>
  )
}

const MODULE_CONTENT = {
  model: ModelModule,
  performance: PerformanceModule,
  training: TrainingModule,
  dataset: DatasetModule,
  pipeline: PipelineModule,
}

export default function ModelPage() {
  const [activeModule, setActiveModule] = useState(null)
  const detailRef = useRef(null)
  const selected = LAB_MODULES.find((module) => module.id === activeModule)
  const DetailContent = activeModule ? MODULE_CONTENT[activeModule] : null

  useEffect(() => {
    if (!activeModule) return
    detailRef.current?.focus()
    detailRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, [activeModule])

  const closeModule = () => {
    const previous = activeModule
    setActiveModule(null)
    requestAnimationFrame(() => document.getElementById(`lab-card-${previous}`)?.focus())
  }

  return (
    <div className="lab-page">
      <section className="lab-hero">
        <div className="lab-hero__inner container">
          <div className="lab-hero__copy">
            <span className="lab-eyebrow">LABORATORIO DE IA</span>
            <h1>PrivacyLens Lab</h1>
            <p>
              Descubre cómo la inteligencia artificial analiza una política de privacidad y
              la transforma en información comprensible para cualquier persona.
            </p>
          </div>
          <div className="lab-hero__visual">
            <img src={labIllustration} alt="Panel tecnológico con visualizaciones de datos e inteligencia artificial" />
            <span className="lab-hero__status"><i aria-hidden="true" />Sistema preparado</span>
          </div>
        </div>
      </section>

      <section className="lab-intro container">
        <span className="lab-intro__mark" aria-hidden="true">AI</span>
        <p>
          PrivacyLens utiliza técnicas de <strong>Procesamiento del Lenguaje Natural</strong> y{' '}
          <strong>Machine Learning</strong> para identificar automáticamente distintos tipos
          de información presentes en una política de privacidad.
        </p>
      </section>

      <section className="lab-modules container" id="lab-modules">
        <header className="lab-section-heading">
          <span className="lab-eyebrow">MÓDULOS DEL LABORATORIO</span>
          <h2>Explora cómo aprende PrivacyLens</h2>
          <p>Cada módulo abre una parte diferente del proceso de inteligencia artificial.</p>
        </header>

        <div className="lab-grid">
          {LAB_MODULES.map((module, index) => (
            <button
              id={`lab-card-${module.id}`}
              className={`lab-card lab-card--${index + 1}`}
              key={module.id}
              type="button"
              aria-label={`Abrir módulo: ${module.title}`}
              aria-expanded={activeModule === module.id}
              aria-controls="lab-detail"
              onClick={() => setActiveModule(module.id)}
            >
              <span className="lab-card__top">
                <span className="lab-card__index">{String(index + 1).padStart(2, '0')}</span>
                <span className="lab-card__icon" aria-hidden="true">{module.icon}</span>
              </span>
              <span className="lab-card__title">{module.title}</span>
              <span className="lab-card__description">{module.description}</span>
              <span className="lab-card__action">{module.action} <span aria-hidden="true">→</span></span>
            </button>
          ))}
        </div>
      </section>

      {DetailContent && (
        <section
          className="lab-detail container"
          id="lab-detail"
          ref={detailRef}
          tabIndex="-1"
          aria-labelledby="lab-detail-title"
        >
          <header className="lab-detail__header">
            <button type="button" className="lab-detail__back" onClick={closeModule}>
              ← Volver a PrivacyLens Lab
            </button>
            <div>
              <span className="lab-eyebrow">MÓDULO {String(LAB_MODULES.indexOf(selected) + 1).padStart(2, '0')}</span>
              <h2 id="lab-detail-title">{selected.title}</h2>
            </div>
          </header>
          <DetailContent />
        </section>
      )}

      <section className="lab-cta container">
        <div>
          <span className="lab-eyebrow">PRUEBA EL SISTEMA</span>
          <h2>¿Quieres ver la IA en acción?</h2>
          <p>Pon a prueba PrivacyLens analizando una política de privacidad real.</p>
        </div>
        <Link to="/" className="lab-cta__button">Ir al Analizador</Link>
      </section>
    </div>
  )
}
