# SPEC 1 — Intent

**Proyecto:** Clasificador de políticas de privacidad — Proyecto 6, Grupo 3
**Bootcamp:** IA School, Factoría F5 Madrid
**Versión:** 0.4 (25 de julio de 2026)

> Nota de idioma: este documento está en español porque su público son personas
> (equipo que aprende, docentes) y así es más accesible. Los términos técnicos van
> en inglés. **Ratificado (24 jul):** las specs se escriben en español; la convención
> completa está en `specs/README.md`.

---

## Propósito del proyecto

Construir una solución de Machine Learning que **lea políticas de privacidad y
clasifique cada fragmento** en **nueve categorías** de prácticas de datos (las 10 del
dataset OPP-115 menos `Other`, ver `2_spec` §2.2). Sobre esa clasificación se monta
una capa propia que:

1. traduce las categorías detectadas a un **nivel de exposición** para el usuario
   (bajo / medio / alto), y
2. conecta cada categoría con el **artículo del RGPD** correspondiente, como
   contexto educativo.

El objetivo final es que **cualquier persona entienda en segundos qué hace una web
con sus datos**, sin necesidad de leer un texto legal largo.

## Problema que se quiere resolver

Las políticas de privacidad son largas, densas y escritas en lenguaje jurídico.
Casi nadie las lee, y quien las lee no siempre distingue qué implican para su
privacidad. La herramienta convierte ese texto en algo comprensible y accionable.

El problema se formula así:

- **Entrada:** el texto de una política (dividido en fragmentos), en inglés o en
  español.
- **Salida:** la(s) categoría(s) de cada fragmento → agregadas en un nivel de
  exposición y enlazadas al RGPD.
- **Decisión que apoya:** ayudar al usuario a entender y valorar qué hace un sitio
  con sus datos antes de fiarse de él.

**Principio rector:** medimos **exposición de la privacidad, no cumplimiento legal**.
Una práctica puede ser perfectamente legal según el RGPD y aun así exponer mucho al
usuario. El desarrollo de este principio está en `2_spec` §6.1.

## Por qué usamos metodología SPEC (SDD)

La carpeta `specs/` es el **contrato común del equipo**. Evita que el proyecto
dependa de decisiones improvisadas o de trabajo aislado, y sirve de referencia
compartida para un equipo con niveles técnicos distintos que aprende sobre la marcha.

Las specs definen:

- Qué se va a construir.
- Qué queda fuera de alcance.
- Cómo se decide que algo está bien hecho.
- Qué tareas corresponden a cada frente de trabajo.
- Qué evidencia debe existir antes de dar una fase por cerrada.

Regla: si una tarea, rama, notebook o decisión contradice esta especificación, se
corrige el trabajo **o** se actualiza la especificación de forma explícita. Nunca
conviven dos versiones de la verdad.

## Nivel Esencial (suelo protegido)

Es el mínimo que tiene que funcionar **sí o sí**, aunque el tiempo apriete. Ningún
nivel superior puede ponerlo en riesgo. El suelo queda protegido cuando existe:

- Dataset OPP-115 cargado y documentado.
- EDA con visualizaciones relevantes para clasificación.
- Preprocesado de texto reproducible.
- Un **clasificador multi-etiqueta funcional de las nueve categorías** (aunque sea
  un solo modelo).
- **Macro-F1** calculada, con diferencia train/validación por debajo del 5%.
- **Soporte de español mediante traducción en la inferencia**, con **degradación
  elegante**: si el servicio de traducción no está disponible, la aplicación avisa y
  sigue funcionando en inglés en lugar de fallar.
- **Entrada del MVP:** el usuario pega el texto de la política, o da la URL directa de
  la propia política. Buscar la política a partir de la URL de la web (footer) es una
  mejora de Nivel Avanzado, no del suelo.
- **Conjunto de prueba en español validado a mano**, sin el cual no se puede afirmar
  que el español funciona.

  > **⚠️ Cifra a reconciliar (decisión de equipo, pendiente).** Este documento pedía
  > 100-200 fragmentos; `3_plan` §6 planifica una sesión de 30-40. Con el tiempo real,
  > 30-40 es lo que cabe. **No urge decidirlo hoy:** la verificación en español es tarea
  > de la Fase B (martes), cuando ya exista traducción y modelo. Se cierra en la daily
  > antes de esa sesión. Nota firme: `do_not_track` tiene 1 sola fila en español y queda
  > fuera de la verificación en cualquier caso (`2_spec` §13.3).
- **Web (PrivacyLens, React + Vite)** que recibe una política y muestra la
  clasificación. Sustituye a la demo de Streamlit de versiones anteriores.
- **API** que sirve el modelo y que la web consume. **Sube al suelo protegido:** sin
  ella la web no funciona, así que deja de ser Nivel Avanzado.
- **Seguridad mínima del backend, como requisito del suelo y no como mejora** (ver
  `2_spec` §11.1): cero secretos en el repo, límite de tamaño del texto de entrada,
  CORS restringido al origen de la web, y saneo de cualquier texto que la web renderice.
- Informe técnico con interpretación del rendimiento y de los límites.
- README con instalación, ejecución y estructura del proyecto.

> **Nota de alcance para ratificar.** El suelo protegido ha crecido dos veces: con el
> español (servicio de traducción + etiquetado manual) y ahora con el cambio de
> Streamlit a web React + API. Montar API + web + modelo es más trabajo que una demo
> Streamlit que llamaba a Python directamente, aunque es más sólido como producto
> final. Mientras tanto la capa de exposición —el diferencial del proyecto— sigue en
> Nivel Medio. El equipo debería confirmar conscientemente que este reparto es el que
> quiere: si el tiempo aprieta, el suelo es más caro de defender que antes.

## Niveles incrementales (aspiración)

Se construyen **encima** del suelo, y solo cuando el suelo es verificable, en este
orden de prioridad:

- **Nivel Medio:** capa de **exposición** (bajo/medio/alto) — es el diferencial del
  proyecto y lo primero que se suma; y los **≥4 modelos base diversos + meta-modelo
  por stacking**.
- **Nivel Avanzado:** **mapeo al RGPD** integrado en la salida; **búsqueda automática
  de la política** en el footer de una web cuando el usuario da la URL en lugar del
  texto (scraping). Esta búsqueda sigue enlaces y descarga páginas externas: es una
  superficie de entrada con riesgo de SSRF y de contenido malicioso, y se diseña como
  capa **separada** de la API de clasificación (`2_spec` §11.1).
- **Nivel Aspiracional:** **extensión de Chrome** que lee la política de la web
  visitada y muestra el resultado sin copiar y pegar; presentaciones pulidas. La
  extensión resuelve por otra vía el problema que ataca el scraper: lee el texto
  directo del navegador.

Si un nivel superior no llega a completarse, se documenta como trabajo pendiente,
pero nunca a costa de romper el suelo.

## Principios de trabajo del equipo

- Primero una entrega mínima ejecutable; mejoras incrementales después.
- **Convención de idioma del repo:** todo lo interno en inglés (carpetas, archivos,
  mensajes de commit, ramas, comentarios de código); las conversaciones (issues,
  dailies) y los entregables para humanos (informe, presentación) pueden ir en
  español.
- **Entorno con uv:** `pyproject.toml` + `uv.lock` versionados; `.venv/` ignorado.
  Flujo: tras `git pull` → `uv sync`; añadir librería → `uv add X` + commit.
- **Datos en el repositorio:** se versiona **el script que genera** los datos, no su
  salida. Los datos pequeños y citables (p. ej. el mapeo del RGPD, 83 KB) sí se
  versionan porque son fuente, no producto.
- **Etiquetas de oro vs. de plata:** solo se entrena y se mide contra etiquetas
  revisadas por personas. Las etiquetas generadas automáticamente sirven para
  explorar, para arrancar un etiquetado manual o para la demo, nunca como verdad de
  referencia sin validar.
- **Credenciales:** ninguna clave de API se sube al repositorio. Van en `.env`
  (ignorado), con un `.env.example` versionado que documenta los nombres.
- Ramas limpias, commits descriptivos y pull requests revisables, con un solo camino
  de integración.
- Cada tarea se cierra con **evidencia verificable** (comando, captura o artefacto).
- Las decisiones técnicas relevantes se registran en `specs/`, no se quedan en el
  chat ni en el Discord.
- **Glosario compartido vivo** (Google Doc), congelado en `specs/GLOSSARY.md` al
  cerrar cada sprint. **Pendiente:** el archivo `specs/GLOSSARY.md` todavía no existe,
  y se han acumulado tres sesiones de términos. Sprint 1 cierra esta semana.

## Manejo de distintos niveles técnicos

El equipo aprende entre sí y tiene niveles técnicos distintos. La planificación debe
dar a cada persona tareas útiles, claras y verificables, sin hacer a nadie de perfil
más bajo responsable único de un componente crítico. Cada ticket indica si es
**apto junior**.

La validación manual del conjunto de prueba en español es un buen ejemplo de tarea
apta para cualquier nivel: no requiere programar, obliga a entender las nueve
categorías a fondo y produce evidencia que el proyecto necesita.

## Estado deseado al finalizar

Al terminar, el repositorio debe permitir:

- Instalar dependencias (`uv sync`), levantar la API y abrir la web PrivacyLens.
- Clasificar una política **en inglés o en español**.
- Reproducir el entrenamiento o explicar cómo se generó el modelo.
- Consultar métricas y evidencia del rendimiento, incluida la del español.
- (Aspiracional) llamar a la API y usar la extensión de Chrome.
- Mostrar una demo clara para la audiencia y una explicación técnica del código.

## Audiencia del documento

- Integrantes del equipo.
- Docentes o evaluadores.
- Asistentes de IA que colaboren en el repositorio.
- Cualquier persona que necesite entender el alcance antes de programar.

Regla principal: **primero un suelo esencial estable, después mejoras incrementales.**

---

## Pendientes (TODO)

- [x] ~~Ratificar en qué idioma se escriben las specs~~ — español; ver `specs/README.md`.
- [x] ~~Unificar el flujo de ramas~~ — hecho el 23 de julio (#21). `dev` es la rama por
      defecto.
- [x] ~~Acordar por escrito la norma de datos generados y convertir los procesos
      existentes en scripts reproducibles~~ — norma en `2_spec` §12.1; los scripts
      01-05 existen.
- [ ] Ratificar el alcance del suelo protegido, ahora que incluye API + web + seguridad.
- [ ] **Reconciliar el tamaño del conjunto de prueba en español** (decisión de Fase B).
- [ ] Definir los **roles** del equipo y el **dueño de cada modelo** (#1).
- [ ] Crear `specs/GLOSSARY.md` al cerrar el Sprint 1.
- [ ] Cerrar en el tablero los issues #48-#51 y #6 (trabajo hecho y en `dev`, issues aún
      abiertos) y el #20 (Streamlit, ya sin objeto).

## Cambios respecto a la versión 0.3 (25 de julio de 2026)

- **Streamlit eliminado.** El MVP es una **web React + Vite (PrivacyLens)** que consume
  una **API**. La API sube al suelo protegido.
- **Seguridad del backend entra como requisito del suelo**, no como trabajo futuro
  (`2_spec` §11.1).
- Entrada del MVP aclarada: pegar texto o URL directa de la política. La búsqueda en el
  footer (scraping) es Nivel Avanzado, capa separada, con riesgo de SSRF anotado.
- La contradicción del tamaño del conjunto en español se marca como decisión de Fase B,
  sin borrar ninguna cifra.

## Cambios respecto a la versión 0.2 (24 de julio de 2026)

- Ratificado el idioma de las specs (español) y remitida la convención completa al
  `README` de `specs/`.
- Marcada la contradicción del tamaño del conjunto de prueba en español (100-200 aquí
  frente a 30-40 en `3_plan`).
- Cerrados tres TODO: idioma de las specs, flujo de ramas y norma de datos generados.
- Señalado que `specs/GLOSSARY.md` sigue sin existir.

## Cambios respecto a la versión 0.1

- Nueve categorías en lugar de diez (`Other` fuera del modelo).
- Target definido como multi-etiqueta y métrica principal fijada en macro-F1
  (ambos TODO cerrados; el detalle vive en `2_spec`).
- El **español entra en el suelo protegido** vía traducción en la inferencia, con
  degradación elegante y conjunto de prueba validado a mano.
- Añadido el principio rector "exposición ≠ cumplimiento".
- Añadidos principios de equipo sobre datos en el repositorio, etiquetas de oro vs.
  de plata y gestión de credenciales.
