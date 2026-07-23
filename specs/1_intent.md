# SPEC 1 — Intent

**Proyecto:** Clasificador de políticas de privacidad — Proyecto 6, Grupo 3
**Bootcamp:** IA School, Factoría F5 Madrid
**Versión:** 0.2 (borrador para revisión del equipo)

> Nota de idioma: este documento está en español porque su público son personas
> (equipo que aprende, docentes) y así es más accesible. Los términos técnicos van
> en inglés. El idioma de las propias specs queda por ratificar (ver TODO al final).

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
- **Conjunto de prueba en español validado a mano** (100-200 fragmentos), sin el cual
  no se puede afirmar que el español funciona.
- **Demo en Streamlit** que recibe una política y devuelve la clasificación.
- Informe técnico con interpretación del rendimiento y de los límites.
- README con instalación, ejecución y estructura del proyecto.

> **Nota de alcance para ratificar:** al incorporar el español, el suelo protegido
> ha crecido (añade un servicio externo y una tarea de etiquetado manual) mientras
> que la capa de exposición —el diferencial del proyecto— sigue en Nivel Medio. El
> equipo debería confirmar que este reparto es el que quiere.

## Niveles incrementales (aspiración)

Se construyen **encima** del suelo, y solo cuando el suelo es verificable, en este
orden de prioridad:

- **Nivel Medio:** capa de **exposición** (bajo/medio/alto) — es el diferencial del
  proyecto y lo primero que se suma; y los **≥4 modelos base diversos + meta-modelo
  por stacking**.
- **Nivel Avanzado:** **mapeo al RGPD** integrado en la salida; **API** que sirve el
  modelo.
- **Nivel Aspiracional:** **extensión de Chrome** que lee la política de la web
  visitada y muestra el resultado sin copiar y pegar; presentaciones pulidas.

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
  cerrar cada sprint.

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

- Instalar dependencias (`uv sync`) y ejecutar la demo de Streamlit.
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

- [ ] Ratificar en qué idioma se escriben las specs.
- [ ] Ratificar el alcance del suelo protegido (ver nota en Nivel Esencial).
- [ ] Definir los **roles** del equipo y el dueño de cada modelo (issue del tablero).
- [ ] Unificar el flujo de ramas (`main` y `dev` han avanzado por caminos distintos).
- [ ] Acordar por escrito la norma de datos generados y convertir los procesos
      existentes en scripts reproducibles.

## Cambios respecto a la versión 0.1

- Nueve categorías en lugar de diez (`Other` fuera del modelo).
- Target definido como multi-etiqueta y métrica principal fijada en macro-F1
  (ambos TODO cerrados; el detalle vive en `2_spec`).
- El **español entra en el suelo protegido** vía traducción en la inferencia, con
  degradación elegante y conjunto de prueba validado a mano.
- Añadido el principio rector "exposición ≠ cumplimiento".
- Añadidos principios de equipo sobre datos en el repositorio, etiquetas de oro vs.
  de plata y gestión de credenciales.
