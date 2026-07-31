# Frontend de PrivacyLens

Aplicación pública construida con React 18, React Router 6 y Vite 5. No utiliza una librería de componentes ni dependencias de iconos, la interfaz se implementa con JSX, CSS y recursos locales.

## Páginas y rutas

| Ruta | Componente | Estado |
|---|---|---|
| `/` | `HomePage` | Home, formulario de URL, análisis recientes y estadísticas de ejemplo |
| `/analisis` | `AnalysisPage` | Resultado real, llama a `POST /api/analyze` |
| `/riesgos` | `RisksPage` | Seis riesgos y diálogos educativos |
| `/rgpd` | `GdprPage` | Ocho derechos y guía práctica |
| `/aprende` | `LearnPage` | Recursos y hábitos educativos |
| `/modelo` | `ModelPage` | PrivacyLens Lab, métricas reales de los modelos comparados |
| `/categorias` | `CategoriesPage` | Catálogo interactivo y diálogos explicativos |
| `/extension` | `ExtensionPage` | Presentación visual de la extensión, sin lógica real |

Las rutas desconocidas redirigen a `/`.

## Estructura

```text
src/
├── components/
│   ├── brand/       Logo
│   ├── layout/      Navbar y footer globales
│   └── ui/          Tarjetas, formulario y elementos reutilizables
├── config/          Catálogo visual de categorías
├── pages/           Vistas y estilos por página
├── services/        API y datos de demostración
├── styles/          Tokens y estilos globales
├── App.jsx          Enrutamiento
└── main.jsx         Entrada de React
```

Las imágenes utilizadas por las páginas se encuentran en la raíz de `frontend/`.

## Datos y backend

`src/services/analysisService.js` es el único punto del frontend que hace `fetch`.

`analyzeUrl(url)` llama a `POST /api/analyze` de verdad. La URL del backend sale de `import.meta.env.VITE_API_BASE_URL`, con cadena vacía por defecto. En desarrollo local, con esa variable sin definir, la petición sale como ruta relativa y depende del proxy de `vite.config.js`, que reenvía `/api/*` al backend configurado ahí. En un build de producción, esa variable tiene que estar puesta en el entorno de build, porque Vite la incorpora al bundle en ese momento, no en tiempo de ejecución, un build sin esa variable manda las peticiones contra el propio dominio del frontend.

`getRecentAnalyses()` y `getGlobalStats()` devuelven siempre el contenido fijo de `src/services/mockData.js`. Un comentario en el propio archivo lo marca como definitivo, no como interruptor temporal, esos dos endpoints no existen en el backend y no está previsto que existan.

`config/categories.js` define una taxonomía visual propia de diez identificadores para la página `/categorias`, con fines educativos. Solo tres de esos identificadores coinciden textualmente con las categorías reales que devuelve la API, `data_retention`, `data_security` y `policy_change`. `CategoryChip.jsx` cae a un estado gris de "categoría desconocida" para el resto.

## Instalación y ejecución

```bash
cd frontend
npm install
npm run dev
```

Build y previsualización.

```bash
npm run build
npm run preview
```

Para un build de producción, fije `VITE_API_BASE_URL` en el entorno donde se ejecuta `npm run build`, no basta con ponerla después del build. No hay suite de tests ni scripts de lint definidos en `package.json`.

## Responsive y accesibilidad

- Navbar y footer compartidos.
- Cuadrículas adaptativas para escritorio, tablet y móvil.
- Diálogos de riesgos y categorías cerrables mediante botón, clic exterior y Escape.
- Navegación interna con `Link` y `NavLink`.

## Limitaciones actuales

- Análisis recientes y estadísticas de la portada siguen siendo datos de ejemplo, por decisión de diseño documentada en el propio código, no porque falte conectarlos.
- La taxonomía visual de `/categorias` no coincide con las categorías reales del backend, salvo tres identificadores.
- Los botones de los módulos de PrivacyLens Lab no ejecutan acciones, las métricas que muestran sí son reales.
- La página de Extensión es una maqueta visual, no refleja el comportamiento real de la extensión instalada, que vive en `extension/` y se documenta aparte.
