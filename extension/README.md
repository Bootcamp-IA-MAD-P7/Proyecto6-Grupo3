# Extensión de Chrome de PrivacyLens

Extensión Manifest V3 que analiza la pestaña activa del navegador contra el backend real de PrivacyLens, sin pasar por el frontend. Se abre desde el icono de la extensión, no se dispara sola al cargar una página.

## Componentes

| Archivo | Responsabilidad |
|---|---|
| `manifest.json` | Permisos, orígenes autorizados y punto de entrada del popup |
| `popup.html` | Estructura visual, semáforo, resumen, categorías, evidencia |
| `popup.js` | Toda la lógica, captura de la pestaña, llamada a la API, render |
| `popup.css` | Estilo con efecto de cristal esmerilado sobre fondo translúcido |
| `fazt.png` | Icono de la extensión |

## Instalación

En `chrome://extensions`, con el modo desarrollador activado, "Cargar descomprimida" y seleccionar esta carpeta. No está publicada en la Chrome Web Store, se instala como paquete sin empaquetar.

## Configuración

`BACKEND_URL`, en `popup.js`, es una constante fija con el backend desplegado en Render. Cambiarla requiere editar el archivo y añadir el nuevo origen a `host_permissions` en `manifest.json`, sin esa coincidencia exacta el navegador bloquea la petición aunque el código esté bien. Hoy `host_permissions` trae tres orígenes, el backend de Render y dos variantes de `localhost:8000` para desarrollo local.

Los permisos declarados son `activeTab` y `scripting`, ninguno de los dos concede acceso hasta que la persona hace clic en el icono de la extensión, ese gesto es lo que dispara el análisis, no la apertura de la pestaña.

## Funcionamiento real

1. Al abrir el popup, lee la URL y el título de la pestaña activa.
2. Si la URL no es `http` o `https`, muestra un error y no continúa.
3. Llama a `POST /api/analyze` con solo la URL, deja que el backend la descargue y extraiga el texto con sus propias guardas contra SSRF.
4. Si el backend responde 422, típico de páginas que cargan contenido con JavaScript, captura con `chrome.scripting.executeScript` el texto ya renderizado en la pestaña y reintenta la petición con ese texto además de la URL.
5. Si la petición falla por cualquier otro motivo, o el reintento también falla, muestra el mensaje de error real y un botón para reintentar, no sustituye el resultado por datos de ejemplo.
6. Con una respuesta válida, muestra el semáforo según el nivel de exposición, el puntaje numérico, el aviso legal que trae la respuesta, las categorías presentes con su confianza, y como evidencia el fragmento más fuerte de la categoría con más peso en el cálculo de exposición, no simplemente el primer párrafo del documento.

El tiempo de espera de cada petición es de 60 segundos, con un aviso que se actualiza cada 8 segundos mientras dura, porque el backend en Render puede tardar en reactivarse tras estar inactivo.

## Modo demo

Si el popup se abre fuera del contexto de una extensión de Chrome, por ejemplo al previsualizar `popup.html` directamente en un navegador normal, no hay `chrome.tabs` disponible. En ese caso se muestran datos de ejemplo fijos, con el título del sitio marcado como "(demo)" y un aviso explícito de que no es un análisis real.

## Limitaciones actuales

- Sin extensión no analiza nada por sí sola, el análisis depende de que la persona pulse el icono, no se dispara al abrir o navegar una página.
- Analiza la pestaña que esté activa en ese momento, si es la home del sitio en vez de la página de la política de privacidad, analiza la home.
- Los pesos por categoría que usa para elegir la evidencia están copiados a mano en `popup.js`, en `CATEGORY_WEIGHTS`, como espejo de `backend/app/exposure.py`. Un cambio en esos pesos del backend no se refleja aquí solo, hay que actualizar los dos archivos.
- El icono declarado en `manifest.json` es uno solo, sin el juego de tamaños 16, 48 y 128 que pide la Chrome Web Store para publicar.
