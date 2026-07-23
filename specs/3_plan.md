# SPEC 3 — Plan

**Proyecto:** Clasificador de políticas de privacidad — Proyecto 6, Grupo 3
**Versión:** 0.2 (borrador para revisión del equipo)
**Plazo real restante:** 6 días de trabajo (jueves 23, viernes 24, lunes 27, martes 28, miércoles 29, jueves 30)

> Este plan organiza el trabajo en fases verificables. Cada fase debe dejar el
> proyecto en un estado **ejecutable y demostrable**, no a medias.
>
> El *qué* vive en `2_spec`. Las tareas concretas viven en **GitHub Projects**, no en
> este documento (ver anexo con la plantilla de issue).

---

## 1. Regla de prioridad

```
Primero el modelo, después el producto. Y nada nuevo el último día.
```

Los componentes que la consigna exige van primero. Lo que se corte, se corta por el
final y se documenta (§7).

## 2. Forma del plan: modelado en paralelo, después producto

**Decisión tomada:** los tres primeros días se dedican al **modelado en paralelo**,
con **una persona por modelo**, y después el equipo converge en el producto.

**Por qué:** los ≥4 modelos base diversos + el meta-modelo son el núcleo evaluable del
proyecto, y son la parte que no se puede improvisar en un día. Con cada persona
llevando un modelo, tres días de trabajo simultáneo aprovechan a todo el equipo, en
lugar de tener a la mayoría esperando a que exista un clasificador.

**El coste que asumimos:** el suelo protegido (demo incluida) no está completo hasta el
día 5. Eso concentra el riesgo de producto al final, y se mitiga con dos cosas que no
cuestan tiempo (§3): congelar el contrato de datos el día 1, y montar el esqueleto de
la interfaz en paralelo desde el primer día.

**Descartado:** la rebanada vertical (un camino completo de extremo a extremo primero,
y engordar después). Protege mejor la demo, pero dejaría a la mayoría del equipo sin
trabajo de modelado durante los primeros días, con solo tres días después para los
cuatro modelos y el meta.

## 3. Lo que hay que congelar antes de entrenar (día 1, primeras horas)

**Esto es la condición para que el plan funcione.** Cuatro personas entrenando en
paralelo solo produce cuatro modelos comparables si comparten el punto de partida:

| A congelar | Por qué |
|---|---|
| **Pipeline de preprocesado** común | Si cada uno limpia y vectoriza a su manera, las métricas no se pueden comparar |
| **Partición** train/validación/test, **por política** y con **semilla fija** | Cuatro modelos medidos sobre particiones distintas no se pueden clasificar entre sí |
| **Deduplicación** aplicada antes de partir | Un párrafo repetido a los dos lados infla las métricas de todos por igual |
| **Contrato de salida** (`2_spec` §9) | Es lo que permite que la interfaz se construya sin esperar al modelo |
| **Formato de las métricas** (macro-F1 + gap train/validación) | Para que la tabla comparativa se rellene sola y no haya que rehacer cálculos |

Sin esto, el día 4 hay cuatro modelos que no se pueden comparar ni combinar, y el
meta-modelo no es posible. **Es tarea del día 1, no del lunes.**

## 4. Frentes de trabajo

| Frente | Alcance |
|---|---|
| **Datos y modelo** | Dataset, EDA, preprocesado, partición, los ≥4 modelos base, meta-modelo, métricas |
| **Producto** | Streamlit, traducción (caché + degradación elegante), después API y extensión |
| **Legal, exposición y QA** | Mapeo RGPD, pesos del semáforo, informe, coherencia entre demo/informe/presentación |

Cómo se activan con este plan:

- **Fase A:** todo el equipo está en modelado, **una persona por modelo**. Los frentes
  de Producto y Legal existen pero solo consumen ratos sueltos (§5).
- **Fase B:** el equipo se reparte por frentes de verdad.
- La **verificación en español** (§6) es tarea de todo el equipo, en una sola sesión.
- El **Scrum Master no lleva un frente entero**: su trabajo es desatascar y mantener
  `specs/` al día.

- [ ] **TODO:** asignar personas a frentes y **dueño de cada modelo** (issue del tablero).

## 5. Fase A — Modelado en paralelo (días 1-3: jueves, viernes, lunes)

### Objetivo

Los **≥4 modelos base diversos** entrenados, medidos con el mismo criterio y
comparables entre sí, más el **meta-modelo** si el lunes da margen.

### Día 1 (jueves) — base común

- Congelar todo lo del §3. Nadie entrena antes de que exista.
- Bajar OPP-115 a `data/dataset/` y cruzar los fragmentos con el archivo de
  anotaciones (sin ese cruce no hay target).
- EDA: distribución de las nueve categorías, desbalance, cuántas etiquetas por
  fragmento.
- Cerrar **qué cuatro modelos** y quién lleva cada uno.

### Días 2-3 (viernes, lunes) — entrenamiento

- Cada persona entrena su modelo sobre el pipeline y la partición comunes.
- Cada modelo se cierra con: **macro-F1** de train y validación, **gap** calculado, y
  su fila en la **tabla comparativa** compartida.
- El lunes por la tarde: **meta-modelo por stacking** sobre los cuatro.

### En paralelo, sin robar tiempo al modelado

- **Producto:** esqueleto de Streamlit contra una **salida simulada** del §9 — que la
  pantalla exista y pinte categorías falsas. Cuando el modelo llegue, solo se cambia
  la fuente de datos.
- **Legal:** descargar y versionar el mapeo RGPD (83 KB) · esqueleto del informe ·
  README iniciado · convención de idioma escrita en `specs/`.

### Entregables

Cuatro modelos entrenados · tabla comparativa con macro-F1 y gap de cada uno ·
meta-modelo (o su bloqueo documentado) · EDA con visualizaciones · pipeline y
partición versionados · esqueleto de Streamlit.

### Verificación

- El pipeline y la partición se ejecutan desde un script y dan **el mismo resultado**
  para cualquiera del equipo (semilla fija).
- Ninguna política aparece en dos grupos de la partición (comprobable por script).
- Los cuatro modelos están medidos **sobre la misma partición**.
- La tabla comparativa está completa, con el gap de cada modelo.

### Riesgos

Cada persona preprocesa a su manera y los modelos no se pueden comparar (lo previene
el §3) · gap por encima del 5% en varios modelos · `do_not_track` sin ejemplos en algún
grupo por su escasez · el meta-modelo no cabe el lunes (se documenta y se hace el martes).

## 6. Fase B — Producto y capas (días 4-5: martes, miércoles)

Aquí se cierra el suelo protegido y se suman las capas. El equipo converge.

### Producto (prioridad máxima: aquí vive el suelo)

- Conectar el modelo real al Streamlit ya esqueletado.
- **Traducción** es→en con **caché** y **degradación elegante**: sin clave o sin red,
  avisa y sigue funcionando en inglés.
- `.env.example` versionado; ninguna clave en el repositorio.
- **API** solo si Streamlit ya está sólido.

### Legal, exposición y QA

- **Semáforo:** fijar pesos y umbrales (`2_spec` §7.2), implementarlo como reglas sobre
  la salida existente, y escribir la justificación de cada peso.
- **Mapeo RGPD:** tabla de consulta categoría → artículo desde el zip versionado, con
  texto para no juristas. Es la capa más barata: no entrena nada.
- Informe con métricas, análisis de errores y límites declarados.

### Verificación en español (todo el equipo, una sesión del martes)

**30-40 fragmentos** en español revisados a mano entre todos, repartidos entre las
categorías que más pesan en el semáforo. No es una métrica publicable: es una
**verificación**, y así se presenta ("revisamos 40 fragmentos y el modelo acertó en N").

**Descartado:** medir contra la preanotación automática de la extensión del dataset.
Diría si nuestro modelo se parece a un buscador de palabras clave, no si acierta.

### Verificación de la fase

`uv sync`, la app arranca con el comando del README **sin configurar ninguna clave** ·
una política en inglés devuelve categorías · una en español también, y con la clave
quitada avisa y sigue en inglés · el semáforo tiene pesos documentados · cada categoría
muestra su artículo del RGPD.

## 7. Fase C — Cierre y defensa (día 6: jueves 30)

**Día de congelación: no entra nada nuevo.** Solo se arregla lo que esté roto.

- Informe cerrado: métricas, macro-F1, tabla comparativa de los cuatro modelos,
  resultado de la verificación en español, análisis de errores y **límites declarados**
  (que el semáforo es una estimación).
- Presentaciones de negocio y técnica, alineadas con lo que el código hace de verdad.
- Capturas y checklist de entrega.
- Ensayo completo de la demo, de principio a fin, **como si el wifi fallara**.
- README revisado por alguien que no lo escribió.

### Verificación

Las métricas del informe, del código y de la presentación **coinciden** · la demo
funciona de principio a fin · no se promete ninguna funcionalidad que no exista ·
cada persona sabe defender su parte.

## 8. Orden de corte (si el tiempo aprieta)

Decidido de antemano para no improvisar el último día. Se corta de arriba abajo:

1. **Extensión de Chrome** — la más cara y la más frágil; se documenta como pendiente.
2. **API** — si Streamlit ya demuestra el producto, la API es infraestructura.
3. **Meta-modelo** — se conservan los cuatro base y su comparativa.
4. **Mapeo RGPD** — barato, así que solo se corta en caso extremo.

**No se cortan nunca:** la demo de Streamlit funcionando, los ≥4 modelos base con su
comparativa, el informe, ni el semáforo (es el diferencial del proyecto).

Lo que se corta **se documenta** como trabajo pendiente con su motivo. Un alcance
recortado y explicado se defiende; una funcionalidad prometida y ausente, no.

## 9. Riesgos del plan

| Riesgo | Mitigación |
|---|---|
| El suelo no existe hasta el día 5 | Esqueleto de Streamlit desde el día 1 contra la salida simulada del §9 |
| Cuatro modelos no comparables entre sí | Congelar pipeline, partición y semilla el día 1 (§3) |
| El producto no cabe en dos días | Orden de corte decidido de antemano (§8) |
| `main` y `dev` divergen | Unificar el flujo a un solo camino **hoy**, antes de que cuatro personas empiecen a entrenar en ramas distintas |
| Datos generados pesados en el repo | Norma escrita (`2_spec` §12); no se reescribe el historial a mitad de proyecto |
| La presentación promete más que el código | El frente de QA revisa la coherencia el día 6 |
| Todo se junta el último día | El día 6 es de congelación: nada nuevo entra |

---

## Anexo — Plantilla de issue (el tablero es la fuente de las tareas)

```markdown
**Qué hay que hacer:** (verbo en infinitivo, una sola cosa)
**Frente:** Datos y modelo / Producto / Legal-Exposición-QA
**Archivos afectados:**
**Depende de:**
**Apto junior:** sí / con apoyo / no como responsable único
**Criterio de terminado:**
**Comando de verificación:**
**Evidencia:** (archivo, captura, métrica o notebook que lo demuestra)
```

Los dos campos que no se saltan son **comando de verificación** y **evidencia**: son
lo que convierte "creo que está hecho" en algo comprobable, y lo que hace que las
dailies asíncronas funcionen.

## Pendientes (TODO)

- [ ] Asignar personas a frentes y **dueño de cada modelo**.
- [ ] Confirmar en la consigna si los ≥4 modelos + meta son requisito calificable.
- [ ] Cerrar **qué cuatro modelos** (investigación sobre la literatura).
- [ ] Unificar el flujo de ramas **hoy**, antes de empezar a entrenar en paralelo.
- [ ] Fijar hora de la sesión de verificación en español (martes).

## Cambios respecto a la versión 0.1

- La forma del plan pasa de **rebanada vertical** a **modelado en paralelo primero**,
  con una persona por modelo (días 1-3) y producto después (días 4-5).
- Nuevo §3: lo que hay que congelar **antes** de que nadie entrene. Es la condición
  para que cuatro modelos entrenados en paralelo sean comparables y combinables.
- El esqueleto de Streamlit se adelanta al día 1 contra una salida simulada, para
  compensar que el suelo no se cierra hasta el día 5.
- Días y fechas concretas en lugar de sprints de una semana.
