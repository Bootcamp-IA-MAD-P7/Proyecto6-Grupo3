# Frontend de PrivacyLens

Aplicación pública construida con React 18, React Router 6 y Vite 5. No utiliza una librería de componentes ni dependencias de iconos; la interfaz se implementa con JSX, CSS y recursos locales.

## Páginas y rutas

| Ruta | Componente | Estado |
|---|---|---|
| `/` | `HomePage` | Home y formulario de URL con contenido de demostración |
| `/analisis` | `AnalysisPage` | Resultado preliminar basado en el mock |
| `/riesgos` | `RisksPage` | Seis riesgos y diálogos educativos |
| `/rgpd` | `GdprPage` | Ocho derechos y guía práctica |
| `/aprende` | `LearnPage` | Recursos y hábitos educativos |
| `/modelo` | `ModelPage` | PrivacyLens Lab; tarjetas visuales aún sin navegación interna |
| `/categorias` | `CategoriesPage` | Catálogo interactivo y diálogos explicativos |
| `/extension` | `ExtensionPage` | Presentación visual de la futura extensión |

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

`src/services/analysisService.js` centraliza el acceso a datos. El valor actual es:

```js
const USE_MOCK = true
```

Por tanto:

- `analyzeUrl`, `getRecentAnalyses` y `getGlobalStats` devuelven datos locales.
- La Home mantiene una tarjeta visual con `MOCK_ANALYSIS`.
- El backend no se consulta desde la interfaz actual.

El código alternativo usa `POST /api/analyze`, `GET /api/analyses/recent` y `GET /api/stats`, pero el backend real solo implementa el primero para texto y no ofrece los dos endpoints GET de datos. Desactivar el mock requiere adaptar el formulario y el componente de resultados al contrato real; no basta con cambiar el booleano.

Durante desarrollo, Vite reenvía `/api/*` a `http://localhost:8000`.

## Instalación y ejecución

```bash
cd frontend
npm install
npm run dev
```

Build y previsualización:

```bash
npm run build
npm run preview
```

No hay suite de tests ni scripts de lint definidos en `package.json`.

## Responsive y accesibilidad

- Navbar y footer compartidos.
- Cuadrículas adaptativas para escritorio, tablet y móvil.
- Diálogos de riesgos y categorías cerrables mediante botón, clic exterior y Escape.
- Navegación interna con `Link` y `NavLink`.

## Limitaciones actuales

- El análisis visible es demostrativo.
- `AnalysisPage` es una presentación preliminar, no la radiografía completa descrita en especificaciones antiguas.
- Los botones de los módulos de PrivacyLens Lab no ejecutan acciones.
- La página de Extensión no implica que exista un paquete Chrome instalable.
