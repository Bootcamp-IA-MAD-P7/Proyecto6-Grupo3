# Revisión técnica de PrivacyLens

Esta revisión corresponde al 31 de julio de 2026, sobre la rama `dev`, en el estado posterior a los commits `49c9332`, `09d037d` y `b0ea83a`.

Método. Cada afirmación de este documento viene de leer el archivo correspondiente o de ejecutar un comando sobre el repositorio, no de los README ni de las specs existentes, que se documentan aparte como lo que son, texto que alguien escribió en un momento dado y que puede haberse quedado atrás del código. Donde el código y la documentación existente dicen cosas distintas, este documento reporta las dos cosas por separado. No es un documento de recomendaciones. Es una fotografía de lo que hay.

## 1. Estructura general

El repositorio tiene tres capas de aplicación (`backend/`, `frontend/`, `extension/`) y cinco carpetas de trabajo de datos y modelos (`data/`, `scripts/`, `eda/`, `models/`, `reports/`, `artifacts/`), más `specs/` como documentación de diseño. En la raíz conviven `pyproject.toml`, `uv.lock`, `.gitignore`, `.python-version` y un `README.md` general. También hay una carpeta `.claude/` con configuración local del asistente de código, sin relación con el proyecto.

| Carpeta | Contenido |
|---|---|
| `backend/` | API FastAPI, 19 archivos Python |
| `frontend/` | SPA en React con Vite, 8 páginas y 9 componentes |
| `extension/` | Extensión de Chrome MV3, 4 archivos |
| `artifacts/` | Modelos entrenados y matrices vectorizadas, 10 archivos, 18.9 MB |
| `models/` | Scripts de entrenamiento y comparación, 7 archivos |
| `scripts/` | Pipeline de datos, 10 scripts numerados más utilidades sueltas |
| `eda/` | 4 scripts de análisis exploratorio |
| `reports/` | Métricas de modelos y figuras generadas por `eda/` y `models/` |
| `data/` | Corpus OPP-115, extensión propia y tablas procesadas, unos 364 MB en total |
| `specs/` | 6 documentos de especificación |

## 2. Backend (`backend/`)

19 archivos Python bajo `backend/app/`, más `backend/README.md`, `backend/.env` y `backend/.env.example`. `backend/__init__.py` y `backend/app/__init__.py` están vacíos, son marcadores de paquete sin lógica.

**`main.py`**. Crea la instancia de FastAPI con título "PrivacyLens API" y versión de aplicación `0.1.0` (este número es el de la instancia FastAPI, distinto del `model_version` que devuelve `/api/analyze`, que es `1.0.0`, ver `analyze.py`). Monta `CORSMiddleware` leyendo los orígenes permitidos desde `Settings`, con métodos restringidos a `GET` y `POST` y sin comodín en ningún caso. Registra los manejadores de error y monta `health_router` y `analyze_router` bajo el prefijo `/api`. No contiene lógica de negocio.

**`config.py`**. Define `Settings`, una clase de `pydantic-settings` con un único campo obligatorio, `cors_allowed_origins`, leído de `backend/.env`. La propiedad `cors_allowed_origins_list` separa la cadena por comas. `MAX_TEXT_LENGTH` está fijado en `100_000` como constante en código, no es configurable por variable de entorno. `load_settings()` envuelve la instanciación de `Settings` y, si falta la variable, lanza un `RuntimeError` con un mensaje que apunta a copiar `.env.example`. El archivo local `backend/.env` contiene únicamente `CORS_ALLOWED_ORIGINS`, sin `GOOGLE_TRANSLATE_API_KEY` todavía.

**`predictor.py`**. Es el puente entre la API y el modelo entrenado. Calcula `REPO_ROOT` como el segundo padre del propio archivo y define `MODEL_PATH` y `VECTORIZER_PATH` apuntando a `artifacts/multiclass_complementnb.joblib` y `artifacts/tfidf_vectorizer.joblib`. La función `_load()` está decorada con `@lru_cache(maxsize=1)`, así que la carga ocurre en la primera llamada a `predict_proba`, no al arrancar la aplicación. Si los archivos no existen, lanza `FileNotFoundError` con un mensaje que menciona `scripts/05_vectorize.py` y `models/12_multiclass_compare.py` como los pasos que los generan. El modelo cargado es un diccionario del que se toma la clave `model`. `_load()` compara `model.classes_` contra `CATEGORIES` y calcula `column_order` para remapear las columnas de probabilidad al orden fijo del proyecto, porque `model.classes_` viene en orden alfabético. Si el modelo no tiene alguna clase de `CATEGORIES`, lanza `ValueError`.

**`stub.py`**. Genera una matriz de probabilidades pseudoaleatorias, con semilla derivada del hash SHA-256 del texto completo, así que la misma entrada produce siempre la misma salida. Su docstring dice que la matriz es `(n_fragmentos, 9)`, pero la función usa `len(CATEGORIES)`, que hoy es 10, no 9, así que ese comentario quedó desactualizado respecto a la propia función que describe. Ningún módulo del backend lo importa, ni `analyze.py`, ni `routes/analyze.py`, ni ningún otro. La única mención a este archivo fuera de sí mismo es un comentario en `predictor.py` que compara la firma de ambas funciones.

**`translation.py`**. Detecta español con una heurística simple, caracteres con tilde o ñ, signos de apertura ¿¡, o al menos tres coincidencias con una lista fija de 16 stopwords españolas. Reescrito el 31 de julio de 2026 para llamar a la API REST v2 de Google Cloud Translation vía `httpx`, en lugar de cargar un modelo local. La función `translate_fragments` lee la clave `GOOGLE_TRANSLATE_API_KEY` de las variables de entorno con `os.environ.get`. Si no está puesta, devuelve el texto sin traducir con `available=False`, sin lanzar excepción. Si está puesta, agrupa los fragmentos pendientes en lotes de hasta 100 (el límite de la API de Google es 128 valores `q` por petición) y llama al endpoint `https://translation.googleapis.com/language/translate/v2`. Mantiene una caché en memoria por hash del texto, así un fragmento repetido dentro del mismo proceso no se vuelve a traducir. Si una petición falla, ese lote se queda con el texto original y los lotes ya traducidos se conservan, la función nunca propaga la excepción hacia arriba. La función `translate()` de nivel documento existe solo por compatibilidad y no la llama nadie, `analyze.py` usa `translate_fragments` después de trocear.

**`exposure.py`**. Calcula un puntaje ponderado, la suma de `peso[categoría] × (fragmentos de esa categoría / total de fragmentos)`. Los pesos están fijos en un diccionario `WEIGHTS`. `third_party_sharing_collection` pesa 3.0, `data_retention` pesa 2.0, `first_party_collection_use` e `international_specific_audiences` pesan 1.0 cada una, `policy_change`, `do_not_track` y `Other` pesan 0.0, `data_security`, `user_choice_control` y `user_access_edit_deletion` pesan -1.0. El propio docstring explica la asimetría, lo que sube el puntaje es un hecho verificable, lo que lo baja depende de si la medida declarada es realmente efectiva, algo que el modelo no puede saber. Los umbrales son `score > 1.0` para nivel `high`, `score >= 0.5` para `medium`, el resto `low`. Si no hay fragmentos, el nivel es `unknown` en vez de forzar un valor. El docstring marca los dos umbrales como una primera estimación, calibrada revisando políticas reales, no con una métrica.

**`gdpr.py`**. Un único archivo con una única función, `gdpr_reference_for(category_id)`, que devuelve la cadena literal `"TODO"` para cualquier valor de entrada, sin excepción ni lógica condicional. El docstring remite al mapeo de Poplavska et al. (2020) como pendiente de aplicar.

**`categories.py`**. Define `CATEGORIES`, una lista de 10 cadenas en orden fijo, las nueve categorías oficiales de OPP-115 más `Other` como décima clase para fragmentos que no describen ninguna práctica de datos. El comentario en el archivo advierte que este orden mapea las columnas de la matriz de probabilidades del modelo, cambiarlo rompe esa correspondencia.

**`chunker.py`**. Divide el texto en fragmentos por párrafo, usando la expresión regular `\n\s*\n+` como separador. La función `_append_fragment` recorta espacios en los bordes de cada fragmento y calcula `start`/`end` como posiciones de carácter reales sobre el texto original, después del recorte. Un fragmento que queda vacío tras el recorte se descarta.

**`schemas.py`**. Modelos Pydantic del contrato de la API. `Label` tiene `id` y `score`. `Fragment` tiene `id`, `text`, `start`, `end` y una lista de `labels`. `Category` tiene `id`, `present`, `confidence`, `fragment_count` y `gdpr_reference`. `Exposure` tiene `level`, `score` y `disclaimer`. `Document` agrupa `source_language`, `translated`, `translation_available`, `exposure`, `categories` y `fragment_count`. `AnalyzeResponse` agrupa `model_version`, `stub`, `document` y `fragments`. `AnalyzeRequest` tiene `text` y `url`, ambos opcionales. `HealthResponse` tiene un único campo, `status`.

**`errors.py`**. Define `BackendError`, una excepción con `status_code` y `message`. Registra dos manejadores en la app, uno que serializa cualquier `BackendError` como `{"error": "<mensaje>"}` con su código, y uno genérico que convierte cualquier otra excepción no prevista en un 500 con el cuerpo fijo `{"error": "Internal server error."}`, sin más detalle. Esto último aplica también a un `FileNotFoundError` de `predictor.py` si faltan los artefactos del modelo, el mensaje descriptivo que ese archivo sí genera internamente no llega al usuario final, llega un 500 genérico.

**`fetcher.py`**. Convierte una URL en el texto de la página. `_guard_url` exige esquema `http` o `https` y hostname, resuelve el hostname con `socket.getaddrinfo` y rechaza con 400 cualquier IP privada, loopback, link-local o reservada, antes de hacer ninguna petición de red. `_download` usa un cliente `httpx` con `follow_redirects=False`, cada salto de redirección se vuelve a pasar por `_guard_url`, con un máximo de 3 saltos. El timeout es de 10 segundos, un error de red da 502, una página de más de 5 MB da 400, un 403 del sitio da 502 con un mensaje que sugiere probar la extensión de Chrome. `_extract_text` usa BeautifulSoup, elimina las etiquetas `script`, `style`, `nav`, `footer`, `header`, `form`, `noscript` y `svg`, prioriza el contenido de `main` o `article` si existen, y une los bloques de texto con doble salto de línea, que es justo el separador que usa `chunker.py`. `fetch_policy_text` exige un mínimo de 500 caracteres útiles tras la extracción, si no los alcanza responde 422 con un mensaje que menciona que la página puede cargar contenido por JavaScript o que la URL puede no apuntar directamente a la política. No ejecuta JavaScript en ningún punto, ese es el límite explícito documentado en la cabecera del archivo.

**`analyze.py`**. Orquesta una llamada completa. Detecta idioma, trocea, traduce fragmento por fragmento, llama a `predictor.predict_proba`, construye los fragmentos y categorías de respuesta, calcula la exposición y arma `AnalyzeResponse` con `model_version="1.0.0"` y `stub=False` fijos, no condicionales. `_build_fragment` toma el argmax de las probabilidades de cada fragmento, un comentario en el código lo describe así, diez clases compiten y la más alta gana, sea 0.9 o 0.4, no hay umbral de decisión. `_build_category` cuenta cuántos fragmentos ganó cada clase y calcula la confianza media de esos fragmentos.

**`routes/analyze.py`**. Expone `POST /api/analyze`. Si `text` llega vacío y hay `url`, llama a `fetch_policy_text`. Si tras eso sigue sin texto, responde 400. Si el texto supera `MAX_TEXT_LENGTH`, responde 400. En cualquier otro caso llama a `analyze_text` y devuelve su resultado.

**`routes/health.py`**. Expone `GET /api/health`, devuelve `{"status": "ok"}` sin lógica adicional.

## 3. Frontend (`frontend/`)

React 18.3.1 con React Router 6.30.0 sobre Vite 5.4.11. Sin librería de componentes ni de iconos, la interfaz es JSX y CSS propios. `package.json` no declara scripts de test ni de lint, solo `dev`, `build` y `preview`.

**Enrutamiento**. `App.jsx` define 8 rutas con `react-router-dom`, `/` (HomePage), `/analisis` (AnalysisPage), `/riesgos` (RisksPage), `/rgpd` (GdprPage), `/aprende` (LearnPage), `/modelo` (ModelPage), `/categorias` (CategoriesPage), `/extension` (ExtensionPage), y una ruta comodín que redirige a `/`. Todo queda envuelto en `Navbar` y `Footer` fijos, más dos capas decorativas, `.aurora` y `.grid-bg`. `main.jsx` monta la app en modo `StrictMode`.

**Páginas conectadas a la API real**. Solo dos. `HomePage.jsx` llama a `getRecentAnalyses()` y `getGlobalStats()` de `analysisService.js`, que devuelven siempre datos fijos de `mockData.js`, con un comentario explícito en el código de que esos dos endpoints no existen en el backend y no está previsto que existan. El formulario de URL de esta página no analiza nada, navega a `/analisis` pasando la URL por el estado de la ruta. `AnalysisPage.jsx` es la única página que llama a `analyzeUrl()`, la función que sí habla con `POST /api/analyze`. Lee la URL del estado de navegación que le pasó `HomePage`. Un comentario en la cabecera del archivo la describe como "ESQUELETO funcional (FASE 2)" y menciona un mock que ya no está en uso, el import real es la función de `analysisService.js` que llama a la API de verdad.

**Páginas estáticas**. Las otras seis páginas no importan `analysisService` en ningún punto, todo su contenido es texto y datos fijos en el propio archivo `.jsx`. `RisksPage.jsx` tiene un array de 6 riesgos con descripción, significado, efecto y recomendaciones. `GdprPage.jsx` tiene 8 derechos y 3 pasos para ejercerlos. `LearnPage.jsx` enlaza a AEPD, INCIBE, la Comisión Europea y un vídeo de YouTube. `ModelPage.jsx` muestra métricas de los modelos entrenados, con las 9 categorías oficiales, resultados de LogisticRegression, LinearSVC y ComplementNB multiclase, y de LightGBM, y menciona en su propio texto que el backend en producción usa ComplementNB multiclase y que `TIME_BUDGET_SECONDS` del traductor estaba en 0.0, una referencia que en el momento de escribir esta página describía correctamente el estado del código, y que dejó de ser cierta el 31 de julio con la reescritura de `translation.py`. `CategoriesPage.jsx` renderiza la lista de `config/categories.js` combinada con un diccionario local de icono, significado, importancia y ejemplo. `ExtensionPage.jsx` es una maqueta visual fija de cómo se vería un análisis, con textos de ejemplo, sin relación con la extensión real de `extension/`.

**`PlaceholderPage.jsx`**. Componente genérico que recibe `title` y `children`. No lo importa ningún otro archivo del proyecto, confirmado por búsqueda de texto en `src/`. No aparece en ninguna ruta de `App.jsx`.

**Componentes**. `Logo.jsx` es un SVG con colores fijos en el propio JS, `#1D3557` o `#FFFFFF` según la variante, y `#2A9D8F` fijo para el elemento de lupa. `Footer.jsx` y `Navbar.jsx` tienen enlaces internos que coinciden con las rutas de `App.jsx`, más enlaces externos fijos a AEPD, INCIBE y al repositorio de GitHub del proyecto. `AnalysisPreviewCard.jsx` lee `analysis.document.exposure` y `analysis.document.categories` con alternativas de respaldo, y tiene un `console.log` de depuración activo en el código. `CategoryChip.jsx` recibe un `categoryId` y busca su definición en `config/categories.js`, si no la encuentra renderiza un chip gris con clase `chip--unknown`. `RecentAnalyses.jsx`, `StatCard.jsx` y `UrlAnalyzerBox.jsx` son componentes de presentación, reciben props y no llaman a la API directamente.

**`config/categories.js` frente a la taxonomía real del backend**. Este archivo define 10 identificadores propios, `cookies`, `data_collection`, `third_party`, `data_retention`, `data_security`, `user_rights`, `intl_transfer`, `children_privacy`, `tracking`, `policy_change`. Comparado con la lista real de `backend/app/categories.py`, solo tres coinciden textualmente, `data_retention`, `data_security` y `policy_change`. Los otros siete identificadores del frontend no tienen equivalente textual en el backend, y siete identificadores del backend, `first_party_collection_use`, `third_party_sharing_collection`, `user_choice_control`, `user_access_edit_deletion`, `do_not_track`, `international_specific_audiences` y `Other`, no aparecen en este archivo. El propio archivo trae un comentario `TODO(backend)` señalando que la alineación está pendiente. Es efecto directo de esto que `CategoryChip.jsx` no encuentra la mayoría de categorías reales y cae al chip gris. Aparte, `AnalysisPreviewCard.jsx` y `ModelPage.jsx` sí usan, cada uno en su propio diccionario local, los identificadores reales del backend, así que dentro del mismo frontend conviven dos taxonomías distintas para el mismo concepto.

**`services/mockData.js`**. Exporta `MOCK_RECENT`, cuatro registros de empresa (Google, Spotify, OpenAI, Booking), y `MOCK_STATS`, cuatro cifras fijas de portada, "3.852 documentos en el corpus", "48.210 párrafos etiquetados", "0,87 F1 medio del modelo", "artículos RGPD mapeados". Un comentario en el archivo aclara que estos dos conjuntos no vienen de ningún endpoint real.

**`services/analysisService.js`**. Único punto del frontend que hace `fetch`. Desde el 31 de julio de 2026, `analyzeUrl()` construye la URL de la petición con `${API_BASE_URL}/api/analyze`, donde `API_BASE_URL` viene de `import.meta.env.VITE_API_BASE_URL`, con cadena vacía como valor por defecto. En desarrollo local, con esa variable sin definir, la petición sale como ruta relativa y depende del proxy de `vite.config.js`. En un build de producción esa variable tiene que estar puesta en tiempo de compilación, porque Vite la incorpora al bundle en ese momento, no en tiempo de ejecución. `getRecentAnalyses()` y `getGlobalStats()` están detrás de una constante `MOCK_ONLY_ENDPOINTS = true`, que un comentario describe como definitiva y no como interruptor temporal, porque esos dos endpoints no existen en el backend.

**`vite.config.js`**. Define el proxy de desarrollo, todo lo que llega a `/api` se reenvía al `target` configurado, con `changeOrigin: true`. Desde el 31 de julio de 2026 el `target` es `https://privacylensproject.onrender.com`.

**`styles/tokens.css`**. Define la paleta de color del proyecto por variable CSS. `--color-bg` es `#F8FAFC`, `--color-card` es `#FFFFFF`, `--color-primary` es `#1D3557`, `--color-secondary` es `#457B9D`, `--color-accent` es `#2A9D8F`, `--color-text` es `#1F2937`, `--color-muted` es `#64748B`, `--color-border` es `#E2E8F0`, `--color-amber` es `#F59E0B`, `--color-amber-deep` es `#D97706`, `--color-amber-soft` es `#FEF6E7`, `--color-indigo` es `#6C7FC4`, `--color-indigo-soft` es `#EEF1FA`, `--color-teal-soft` es `#E6F6F4`, `--color-blue-soft` es `#EAF2F8`, `--color-navy-soft` es `#E9EDF4`. También define las familias tipográficas, Manrope para títulos e Inter para cuerpo, radios de borde y sombras. `global.css` aplica esas variables al fondo y tipografía base, y define los fondos decorativos.

## 4. Extensión de Chrome (`extension/`)

Manifest V3, 4 archivos, `manifest.json`, `popup.html`, `popup.js`, `popup.css`, más el icono `fazt.png`. Reescrita el 31 de julio de 2026 dentro de esta misma sesión de trabajo, documentado aquí en el estado en que quedó.

**`manifest.json`**. Permisos `activeTab` y `scripting`. `host_permissions` con tres orígenes, `https://privacylensproject.onrender.com/*`, `http://localhost:8000/*` y `http://127.0.0.1:8000/*`. Un único icono declarado, sin variantes de tamaño 16/48/128.

**`popup.js`**. Se ejecuta al abrir el popup, sin disparador en la apertura de una pestaña ni service worker en segundo plano, así que el análisis ocurre cuando la persona hace clic en el icono de la extensión, no automáticamente al cargar una página. `BACKEND_URL` es una constante fija con el dominio de Render. El flujo de `init()` primero intenta `POST /api/analyze` mandando solo `url`, dejando que el propio backend descargue y extraiga el texto con `fetcher.py`. Si la respuesta es 422, ejecuta `chrome.scripting.executeScript` para leer `document.body.innerText` de la pestaña activa y reintenta la petición añadiendo ese texto capturado. Si la petición falla por cualquier otro motivo, o si el segundo intento también falla, se muestra un mensaje de error real en la interfaz, con un botón para reintentar, en vez de sustituir el resultado por datos de ejemplo. El timeout de cada petición es de 60 segundos, con un aviso que cambia cada 8 segundos mientras se espera. El conjunto `mockDataset` con datos de ejemplo de Spotify solo se usa si el popup se abre fuera del contexto de una extensión de Chrome, por ejemplo al previsualizar el HTML directamente, y en ese caso el título del sitio se marca como "(demo)". La función `adaptarRespuestaFastAPI` elige el fragmento de evidencia a partir de la categoría con mayor peso en `CATEGORY_WEIGHTS`, una copia local de los pesos de `backend/app/exposure.py`, no simplemente el primer párrafo del documento.

**`popup.html`**. Estructura con semáforo de tres luces, cabecera con avatar, nombre y URL del sitio, caja de resumen con puntaje de exposición y aviso legal, contenedor de categorías, caja de evidencia con cita y enlace, y un botón de reintento oculto por defecto.

**`popup.css`**. Estilo con efecto de cristal esmerilado, `backdrop-filter: blur`, sobre fondo translúcido. Variables propias de color para el semáforo, `--red-luz #EF4444`, `--yellow-luz #F59E0B`, `--green-luz #10B981`, `--luz-disabled #CBD5E1`, y para las etiquetas de categoría, en azul, verde, morado y amarillo.

## 5. Artefactos entrenados (`artifacts/`)

10 archivos, 18.9 MB en total.

| Archivo | Tamaño | Generado por | Usado en producción |
|---|---|---|---|
| `multiclass_complementnb.joblib` | 2.25 MB | `models/12_multiclass_compare.py` | Sí, `backend/app/predictor.py` |
| `tfidf_vectorizer.joblib` | 331 KB | `scripts/05_vectorize.py` | Sí, `backend/app/predictor.py` |
| `multiclass_logreg.joblib` | 1.07 MB | `models/12_multiclass_compare.py` | No |
| `lightgbm_model.joblib` | 6.89 MB | `models/03_lightgbm.py` | No |
| `complement_nb_model.joblib` | 4.82 MB | `models/02_complement_nb.py` | No |
| `linear_svc_model.joblib` | 926 KB | `models/linear_svc.py` | No |
| `X_train.npz` | 1.83 MB | `scripts/05_vectorize.py` | No, insumo intermedio |
| `X_test.npz` | 424 KB | `scripts/05_vectorize.py` | No, insumo intermedio |
| `X_val.npz` | 416 KB | `scripts/05_vectorize.py` | No, insumo intermedio |
| `y_train.npy`, `y_val.npy`, `y_test.npy` | 23 KB, 5.3 KB, 6 KB | `scripts/05_vectorize.py` | No, insumo intermedio |

`multiclass_logreg.joblib` y `multiclass_complementnb.joblib` vienen del mismo script, que guarda solo el modelo ganador de cada ejecución. Coexisten porque el script se corrió más de una vez, con marcas de tiempo distintas el mismo día.

## 6. Modelos y experimentos (`models/`)

7 archivos. `02_complement_nb.py` entrena `OneVsRestClassifier(ComplementNB)` multietiqueta sobre las 9 categorías, con búsqueda de `alpha` entre 0.1, 0.5 y 1.0, selecciona por macro-F1 en validación. `03_lightgbm.py` entrena 9 cabezas binarias LightGBM, una por categoría, con selección de características chi2 y parada temprana, guarda métricas en `reports/lightgbm_metrics.json`. `04_deberta.py` hace fine-tuning de `microsoft/deberta-v3-small` con `transformers` y `torch`, sobre texto crudo sin TF-IDF, no guarda modelo ni fila de reporte, solo imprime resultados en consola. `11_multiclass_baseline.py` entrena una regresión logística multinomial de 10 clases como referencia del enfoque multiclase. `12_multiclass_compare.py` entrena y compara LogisticRegression, LinearSVC y ComplementNB en modo multiclase, guarda `reports/multiclass_comparison.csv` y el artefacto del ganador. `linear_svc.py` es un barrido de configuraciones TF-IDF con LinearSVC y LogisticRegression calibrada, en modo multietiqueta. `metrics.py` no entrena nada, expone funciones de métricas compartidas por los cuatro scripts multietiqueta, con umbral fijo de 0.5.

## 7. Pipeline de datos (`scripts/`)

Numerado del 01 al 06 para el pipeline multietiqueta principal. `01_inspect_opp115.py` lee el corpus OPP-115 y solo imprime su estructura, no escribe nada. `02_build_target.py` construye `data/processed/training_table.csv`, 9 columnas binarias, sin incluir `Other`. `03_prepare_evaluation_set.py` genera `evaluation_es.csv` y `evaluation_en.csv` a partir de `data/dataset_extension/`, como conjuntos separados del entrenamiento. `04_build_split.py` genera `split_assignment.csv`, partición 70/15/15 por política, semilla 42. `05_vectorize.py` ajusta el `TfidfVectorizer` solo con train y escribe el vectorizador y las matrices `X`/`y`. `06_smoke_test.py` es una prueba desechable de que el pipeline funciona, solo consola.

Numerado 10 en adelante para la rama multiclase. `10_build_multiclass_target.py` deriva `multiclass_target.csv` con una regla de prioridad que resuelve cada fragmento a una sola clase, más `Other`. `13_coverage_report.py` mide cobertura léxica del vocabulario OPP-115 sobre `dataset_extension`, solo consola. `check_alignment.py` verifica que las tablas CSV y las matrices `.npz`/`.npy` están alineadas antes de entrenar.

Sueltos, sin numeración de pipeline, tres archivos `.sh`, `alinear_tablero_v2.sh`, `sub_issues_5.sh`, `34_untrack_external.sh`, descritos en `scripts/README.md` como utilidades de coordinación del propio repositorio, no parte del pipeline de datos.

## 8. Análisis exploratorio (`eda/`)

4 scripts en formato de celdas Jupytext. `01_target_distribution.py` mide desbalance entre las 9 categorías y guarda `reports/figures/target_distribution.png`. `02_target_multilabel.py` mide número de etiquetas por fragmento y coocurrencia entre categorías, guarda `multilabel_distribution.png` y `cooccurrence_heatmap.png`. `03_text_length_vocab.py` mide longitud de texto y tamaño de vocabulario. `04_text_split_rare_classes.py` audita si el split oficial tiene fuga de información entre política y fragmento, y mide la frecuencia de `do_not_track` en los conjuntos de evaluación en español e inglés, guarda `reports/figures/51_particion_politicas.png`.

## 9. Informes (`reports/`)

`lightgbm_metrics.json`, con claves de macro-F1, micro-F1, gap de sobreajuste, F1 por categoría en validación y número de árboles usados por categoría, generado por `models/03_lightgbm.py`. `multiclass_comparison.csv`, con una fila por modelo, LogisticRegression, LinearSVC, ComplementNB, columnas de accuracy y macro-F1 en train y validación más una columna de F1 por cada una de las 10 clases, generado por `models/12_multiclass_compare.py`. Carpeta `figures/` con 5 PNG, cada uno trazable a uno de los scripts de `eda/`.

## 10. Datos (`data/`)

Unos 364 MB en total, en tres ramas.

**`data/dataset/`**, unos 323 MB, 7.332 archivos. `original_policies/` guarda 6.486 archivos, 218 MB, páginas web completas descargadas, HTML más recursos (imágenes, CSS, JavaScript), organizadas en 114 subcarpetas por empresa más un lote adicional de 1.065 archivos. `annotations/` tiene 115 CSV con las anotaciones humanas originales de OPP-115. `consolidation/` tiene 345 CSV en tres subcarpetas según umbral de solapamiento, 0.5, 0.75 y 1.0. `sanitized_policies/` tiene 115 HTML limpios, uno por política. `pretty_print/` y `pretty_print_uniquified/` son variantes de esos mismos 115 documentos.

**`data/dataset_extension/`**, unos 37 MB, 851 archivos, organizados en carpetas `Agent0` a `Agent4`, cada una correspondiente a una etapa de un pipeline propio del equipo, no de OPP-115. `Agent0` reúne el catálogo de 33 empresas validadas como fuente. `Agent1` guarda los documentos descargados y limpiados, crudos y procesados, con metadatos y hash SHA-256 por documento. `Agent2` guarda la segmentación en 10.797 párrafos, con estructura, entidades e incrustaciones TF-IDF de 256 dimensiones. `Agent3` guarda la preclasificación automática por reglas, con categoría, confianza, evidencia literal y artículos RGPD asociados. `Agent4/external_datasets/` guarda dos corpus de terceros usados como referencia, `JURIX_2020_OPP115_GDPR`, con las matrices de mapeo entre categorías OPP-115 y artículos RGPD de Poplavska et al. (2020), y `MAPP_Corpus`, un corpus bilingüe inglés-alemán de políticas de aplicaciones móviles de Arora et al. (2022). El archivo principal de esta rama es `privacylens_dataset_v1_1.parquet`, 10.797 filas por 26 columnas, con espejo en `.csv`.

**`data/processed/`**, 4 MB, 6 archivos, `training_table.csv`, `split_assignment.csv`, `evaluation_es.csv`, `evaluation_en.csv`, `multiclass_target.csv` y un `README.md`.

No hay ningún archivo de código, `.py` ni `.ipynb`, dentro de `data/`, confirmado por búsqueda en toda la carpeta.

## 11. Especificaciones (`specs/`)

6 documentos. Todos describen, de forma consistente entre sí, un sistema anterior al que existe hoy en el código. Se listan aquí por lo que dicen, no por si siguen siendo ciertos, eso se trata en la tarea siguiente.

**`1_intent.md`**. Define propósito, usuarios, alcance y principios. En su sección de límites actuales afirma que la interfaz funciona con datos simulados y no consume el backend, que el backend no descarga URLs ni ejecuta modelos entrenados, que traducción, exposición y mapeo RGPD son placeholders, y que no existe extensión de Chrome instalable en la rama.

**`2_spec.md`**. Especificación funcional en 9 secciones. Describe `USE_MOCK = true` en el frontend, un backend que responde 501 si se manda solo `url`, un `stub` que produce probabilidades simuladas para nueve categorías, y una exposición fija en nivel `medium` con puntaje 0.5.

**`3_plan.md`**. Registra el estado por área en el momento en que se escribió, y una lista de 7 puntos pendientes para integración, entre ellos conectar el backend a un modelo real, sustituir los mocks del frontend, y decidir si implementar traducción, exposición y referencias RGPD.

**`4_data_contract.md`**. Contrato de las tablas de `data/processed/`, columnas exactas de `training_table.csv`, tamaños de la partición congelada (train 2.550 filas de 80 políticas, val 579 filas de 17 políticas, test 663 filas de 18 políticas), y 7 reglas obligatorias sobre cómo tratar esos datos, no recrear la partición, no ajustar TF-IDF con validación o test, no mezclar `dataset_extension` con entrenamiento.

**`5_backend_contract.md`**. Contrato de la API con un ejemplo completo de respuesta JSON. Ese ejemplo trae `model_version: "0.1.0"`, `stub: true`, exposición fija con el mismo disclaimer literal que sigue en el código actual, y `gdpr_reference: "TODO"`. Documenta una tabla de errores donde enviar solo `url` da 501, y una lista de 6 pasos pendientes antes de sustituir el stub por un modelo real.

**`README.md`** (de `specs/`). Índice de los cinco documentos anteriores, con una nota final que dice que el experimento multiclase no sustituye automáticamente el contrato multietiqueta del backend, y que cualquier cambio de enfoque debe alinear código, artefactos, categorías del frontend y contrato de API.

## 12. README existentes fuera de `specs/`

16 archivos README además del de `specs/`. Trece documentan partes propias del proyecto, la raíz, `backend/`, `frontend/`, `data/`, `data/dataset/`, `data/dataset_extension/`, `data/dataset_extension/Agent0/`, `data/dataset_extension/Agent1/`, `data/processed/`, `eda/`, `models/`, `reports/` y `scripts/`. Los tres restantes documentan datasets de terceros incluidos como referencia dentro de `data/dataset_extension/Agent4/external_datasets/`, el `readme.txt` de `data/dataset/`, el `readme.txt` de `MAPP_Corpus` y el `readme.pdf` de `JURIX_2020_OPP115_GDPR`, y no son texto propio del equipo, documentan el dataset de origen tal como lo entregaron sus autores.

Todos los README propios del proyecto describen, igual que las specs, un sistema con `USE_MOCK = true` en el frontend, un backend con `stub.py` como fuente de probabilidades, análisis por URL respondiendo 501, y sin extensión de Chrome empaquetable. El `README.md` raíz enlaza además a `https://privacylens-project.onrender.com/` y `https://privacylensproject.onrender.com/docs` como URLs públicas del proyecto ya desplegado, algo que convive en el mismo documento con la afirmación de que el análisis por URL no está implementado.

## 13. Configuración de raíz

**`pyproject.toml`**. Python 3.12 o superior. Desde el 31 de julio de 2026, `torch`, `transformers`, `sentencepiece` y `accelerate` están en un grupo opcional `training`, separados de las dependencias base, porque solo los usa `models/04_deberta.py`, un script que no corre en el backend desplegado.

**`uv.lock`**. Regenerado el 31 de julio de 2026 junto con el cambio anterior en `pyproject.toml`.

**`.gitignore`**. Ignora `artifacts/*` en general, con dos excepciones explícitas, `multiclass_complementnb.joblib` y `tfidf_vectorizer.joblib`, los dos artefactos que carga `predictor.py`. Ignora `.env` en cualquier carpeta del repositorio.

**`.python-version`**. Fija la versión de Python usada por herramientas que la leen automáticamente, como `uv`.

## 14. Commits recientes en `dev` relacionados con lo anterior

`49c9332`, extensión de Chrome reescrita, proxy de Vite corregido. `09d037d`, `translation.py` reescrito sobre la API de Google, dependencias pesadas movidas a extra opcional. `b0ea83a`, `analysisService.js` con URL de backend configurable por variable de entorno.
