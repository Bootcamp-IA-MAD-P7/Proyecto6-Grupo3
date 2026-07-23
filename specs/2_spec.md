# SPEC 2 — Spec (fuente única de verdad)

**Proyecto:** Clasificador de políticas de privacidad — Proyecto 6, Grupo 3
**Versión:** 0.2 (borrador para revisión del equipo)

> Este documento manda sobre el resto. Si el código, un notebook, una rama o una
> decisión lo contradicen, se corrige el trabajo **o** se actualiza este documento
> de forma explícita. Nunca conviven dos versiones de la verdad.
>
> Es un documento **vivo**: cuando el EDA o el entrenamiento revelen algo nuevo, se
> actualiza aquí.

---

## 1. Dataset

### 1.1 Fuente principal — OPP-115

- **Fuente:** OPP-115 (*Online Privacy Policies, 115*), del Usable Privacy Policy
  Project — Wilson et al., 2016 (CMU / Fordham / Universidad de Pittsburgh).
- **Contenido:** 115 políticas de privacidad reales **en inglés**, partidas en ~3.800
  fragmentos, con un archivo aparte de ~23.000 anotaciones hechas a mano.
- **Por qué este dataset:** las anotaciones manuales son lo que convierte el texto en
  algo aprendible. Sin ellas no hay target. Son **etiquetas de oro**.
- **Uso:** investigación y docencia, citando a Wilson et al. (2016).
- **Ubicación en el repo:** `data/dataset/`.

### 1.2 Mapeo al RGPD

- **Fuente:** Poplavska, E., Norton, T. B., Wilson, S. & Sadeh, N. (2020),
  *From Prescription to Description: Mapping the GDPR to a Privacy Policy Corpus
  Annotation Scheme*, JURIX 2020, pp. 243-246. DOI: 10.3233/FAIA200874.
- **Descarga:** `JURIX_2020_OPP-115_GDPR_v1.0.zip` (83 KB) desde
  <https://usableprivacy.org/data>.
- **Se versiona en el repo** por ser fuente citable y de tamaño mínimo.

### 1.3 Extensión del dataset (rama `feature/dataset-extension`)

Conjunto de 33 políticas actuales (julio 2026) partidas en 10.797 párrafos: 8.680 en
español y 2.117 en inglés. Incluye una **preanotación automática** generada con reglas
de palabras clave bilingües, usando la taxonomía de OPP-115.

**Rol acordado: material de evaluación y de demo, no de entrenamiento.** Aporta lo que
OPP-115 no tiene (políticas actuales, reales y en español), y es la fuente natural del
conjunto de prueba en español del §4.3.

Características a tener en cuenta antes de usarla:

| Característica | Implicación |
|---|---|
| Preanotación por reglas, sin revisión humana (confianza media 58,8%; 79% marcado para revisión) | Son **etiquetas de plata**: no se entrena ni se mide contra ellas sin validar |
| Una categoría principal por párrafo (2,8% con alternativa) | No es multi-etiqueta como nuestro esquema |
| 76% de los párrafos caen en `Other` | Coherente con dejar `Other` fuera (§2.2) |
| `Do Not Track` con 9 ejemplos frente a miles de `Other` | Desbalance extremo; imposible partir esa clase de forma fiable |
| 3.434 párrafos duplicados exactos dentro del mismo documento | **Hay que deduplicar** antes de partir (§4) |
| Granularidad más fina que OPP-115 (mediana ~20 palabras) | Si alguna vez se mezclan, hay que reagrupar párrafos |
| Campo de artículos RGPD generado por las mismas reglas léxicas | No es trazable jurídicamente; se usa el mapeo de §1.2 en su lugar |
| Sin scripts que regeneren los artefactos | Ver §12; no se pueden dejar de rastrear hasta que existan |

## 2. Definición del target

### 2.1 Tipo de clasificación — **multi-etiqueta** (multi-label)

Cada fragmento puede llevar **varias categorías a la vez**. Un mismo párrafo puede
decir "recogemos tu correo **y** lo compartimos con socios publicitarios": son dos
prácticas distintas en una frase.

**Por qué:** es como está anotado OPP-115 (~23.000 anotaciones sobre ~3.800
fragmentos, unas seis por fragmento). Forzar una sola etiqueta por fragmento
(multiclase) obligaría a descartar información real del texto.

**Implicación técnica:** el modelo devuelve **una probabilidad por cada categoría**
(nueve decisiones binarias en paralelo), y un **umbral** decide cuáles se marcan.

### 2.2 Categorías modeladas — **nueve** (de las 10 del dataset)

| # | Categoría (id interno) | En cristiano |
|---|---|---|
| 1 | `first_party_collection_use` | Qué recoge el propio sitio y para qué |
| 2 | `third_party_sharing_collection` | Qué se comparte con o recogen terceros |
| 3 | `user_choice_control` | Qué opciones de control tiene el usuario |
| 4 | `user_access_edit_deletion` | Si puedes acceder, editar o borrar tus datos |
| 5 | `data_retention` | Cuánto tiempo guardan tus datos |
| 6 | `data_security` | Qué medidas protegen tu información |
| 7 | `policy_change` | Cómo avisan si la política cambia |
| 8 | `do_not_track` | Si respetan la señal "no me rastrees" |
| 9 | `international_specific_audiences` | Prácticas para grupos concretos |

**Decisión documentada:** la décima categoría de OPP-115, `Other`, **queda fuera del
target**. Motivos: (a) es un cajón de sastre heterogéneo (texto introductorio,
contacto, lo no cubierto) y por tanto ruidoso; (b) no aporta nada al nivel de
exposición; (c) con macro-F1, una categoría ruidosa arrastra la métrica sin aportar
valor al producto. Dato de apoyo: en la extensión del §1.3, `Other` concentra el 76%
de los párrafos.

**Importante:** "dejar fuera" significa quitar la etiqueta del target, **no borrar
fragmentos**. Los fragmentos anotados solo como `Other` se conservan con todas las
etiquetas a cero. Es el comportamiento correcto del producto: ante un párrafo de
contacto, el modelo no enciende ninguna luz.

### 2.3 Umbral de decisión

- [ ] **TODO:** fijar el umbral a partir del cual una categoría se considera presente
  (por defecto 0.5, o ajustado por categoría).

Es una decisión de producto, no un detalle técnico: un umbral bajo marca más cosas y
se equivoca por exceso; uno alto solo marca lo evidente y deja pasar prácticas reales.

## 3. Métrica y control de sobreajuste

- **Métrica principal: macro-F1.** Promedia las nueve categorías **por igual**, de
  modo que una categoría rara pero importante (p. ej. `do_not_track`) pesa lo mismo
  que una frecuente (`first_party_collection_use`). Es la métrica que manda al
  comparar modelos y elegir el meta-modelo.
- **Por qué esta y no micro-F1:** micro-F1 da más peso a las categorías con muchos
  ejemplos y produce una nota más alta y optimista. Para una herramienta de privacidad,
  pasar por alto una práctica poco frecuente pero grave es el fallo que no queremos.
- **Métricas reportadas** (en el informe, no deciden): micro-F1, F1 por categoría,
  precision y recall por categoría, matriz de confusión por categoría, y **macro-F1
  desglosada por idioma** (§4.3).
- **Regla de sobreajuste:** la diferencia de macro-F1 entre entrenamiento y
  validación debe ser **menor al 5%**. Si no, se documenta como bloqueo.

## 4. Reparto de los datos

### 4.1 Por política, no por fragmento

Las 115 políticas se reparten **enteras** entre train / validación / test. Ninguna
política puede aparecer en dos grupos a la vez.

**Por qué:** si se repartieran los fragmentos al azar, trozos de una misma política
caerían en train y en test, y el modelo acertaría en parte por reconocer el estilo y
el vocabulario de esa empresa, no por saber leer políticas. Las métricas saldrían
infladas y el modelo rendiría peor ante webs nuevas, que es el uso real.

**Contrapartida asumida:** con solo 115 unidades, el reparto de categorías queda
menos equilibrado entre grupos y hay algo más de azar. Se mitiga fijando la
**semilla aleatoria** y documentando la distribución resultante por grupo.

### 4.2 Deduplicación previa

Antes de partir hay que **eliminar duplicados exactos**. Un mismo párrafo repetido a
los dos lados de la partición produce el mismo efecto que el reparto por fragmento:
el modelo aprueba porque ya vio la respuesta. En la extensión del §1.3 se han
detectado 3.434 duplicados exactos intra-documento.

### 4.3 Conjunto de prueba en español

Como el español entra en el suelo protegido (§5), hace falta poder **demostrar** que
funciona, no solo afirmarlo: un conjunto de **100-200 fragmentos en español con
etiquetas validadas a mano**, tomados de la extensión del §1.3.

Se usa **solo para evaluar**, nunca para entrenar, y produce una macro-F1 separada
por idioma.

- [ ] **TODO (decisión de equipo):** validar una muestra ya preanotada (más rápido,
  con riesgo de dejarse llevar por la sugerencia) o etiquetar en limpio sin ver la
  preanotación (más lento, y de paso mide qué tal lo hacen las reglas).

## 5. Idiomas: inglés y español

**Ruta acordada: traducir en la inferencia.** El modelo se entrena y vive **en
inglés**. Si llega una política en español, se traduce y luego se clasifica.

**Por qué esta ruta:**

- Las etiquetas de oro solo existen en inglés, así que entrenar en español no está
  disponible.
- No toca el modelo: la elección de los ≥4 modelos base (§6) queda intacta y
  representaciones como TF-IDF siguen siendo válidas.
- Solo necesitamos detectar **de qué tema** habla un fragmento, no extraer una
  obligación legal con precisión jurídica; para eso la traducción automática basta.

**Rutas descartadas:** (A) modelo multilingüe con transferencia entre idiomas — obliga
a embeddings neuronales más pesados y lentos; (B) traducir el corpus de entrenamiento
— hereda errores de traducción y duplica el preprocesado.

**Reglas de implementación:**

1. **La traducción es interna y desechable.** Al usuario se le devuelve **su texto
   original**. Si la extensión de Chrome resalta un párrafo, resalta el español que la
   persona está viendo, no una traducción que no aparece en la página.
2. **Degradación elegante (requisito del suelo).** Si el servicio de traducción no
   responde o no hay clave configurada, la aplicación **avisa y sigue funcionando en
   inglés**. Nunca se cae. Esto es lo que permite que otra persona pueda ejecutar el
   proyecto desde el README sin registrarse en ningún servicio.
3. **Caché de traducciones**, indexada por hash del texto, para no consumir cuota
   traduciendo lo mismo repetidamente durante el desarrollo y la demo.
4. **Credenciales:** la clave va en `.env` (ignorado por git), con un `.env.example`
   versionado que documenta los nombres de las variables sin valores.
5. Solo se traduce cuando se detecta español; el inglés no pasa por el traductor.

- [ ] **TODO:** elegir proveedor de traducción y comprobar cuotas y límites de su
  capa gratuita (cuántas políticas caben al mes).

## 6. Enfoque de modelado

- **≥4 modelos base diversos** (distintas familias y representaciones del texto) +
  un **meta-modelo por stacking** que aprende a combinarlos.
- **Por qué cuatro y diversos:** cuatro modelos que se equivocan en lo mismo no
  aportan más que uno. Lo que hace útil al ensamble es que fallen en cosas distintas.
  La diversidad importa más que la cantidad.
- El meta-modelo es trabajo del Sprint 2.

- [ ] **TODO:** elegir los cuatro. Depende de la investigación pendiente sobre qué se
  ha probado con OPP-115 en la literatura (issue del tablero), para decidir con datos.

## 7. Capa de exposición (el semáforo)

> **Esta capa NO sale del dataset.** OPP-115 dice qué prácticas describe una
> política (descriptivo), no si son buenas o malas. El semáforo es una capa propia
> del equipo, con reglas transparentes y justificables.

### 7.1 Principio: exposición ≠ cumplimiento

Una web puede cumplir el RGPD al 100% y aun así exponerte mucho: declara que
comparte tus datos con decenas de socios, que los retiene indefinidamente, y tú
"consientes". Un semáforo de *cumplimiento* pintaría eso verde.

**Nuestro semáforo mide exposición real de la privacidad**, no conformidad legal.
La pregunta que pesa cada categoría es *"¿por cuántas manos pasan mis datos, cuánto
tiempo se quedan, y me dejan control?"*, no *"¿es legal?"*.

### 7.2 Mecanismo: puntuación ponderada por impacto

Cada categoría detectada suma o resta puntos de exposición; el total cae en
bajo / medio / alto según unos umbrales.

| Dirección | Categorías | Razón |
|---|---|---|
| **Suben** | `third_party_sharing_collection` (fuerte), `first_party_collection_use`, `data_retention` | Los datos se esparcen o permanecen |
| **Bajan** | `data_security`, `user_choice_control`, `user_access_edit_deletion`, `do_not_track` | Protegen o devuelven control al usuario |
| **Contexto** (poco peso) | `policy_change`, `international_specific_audiences` | Informan, pero no cambian la exposición por sí solas |

**Ruta descartada:** reglas por simple presencia ("si aparece X → amarillo"). Más
simple, pero no gradúa: una web con una práctica dudosa pesaría igual que otra con
cinco.

- [ ] **TODO:** fijar los pesos numéricos exactos y los umbrales de corte.

### 7.3 Limitación asumida (y declarada al usuario)

El modelo detecta **qué temas** trata una política, **no si los trata bien o mal**.
`data_retention` etiqueta igual un "borramos a los 30 días" que un "guardamos para
siempre"; que aparezca `do_not_track` puede significar que lo respetan o que no.
El detalle fino vive en los subatributos de OPP-115, que quedan fuera de alcance (§11).

Consecuencias que asumimos de forma explícita:

1. El semáforo es una **estimación por presencia de temas**, no una lectura cláusula
   por cláusula. La interfaz debe **decírselo al usuario** con claridad.
2. Las categorías que **suben** la exposición se pesan con **más confianza** que las
   que la bajan: que el tema aparezca no garantiza que la práctica sea buena.
3. Para compensar la caja negra, la salida incluye **qué fragmento activó qué
   categoría**, para que el usuario pueda juzgar por sí mismo (§9).

## 8. Capa RGPD (educativa, separada del semáforo)

El RGPD **no puntúa** el semáforo. Se muestra al lado, como contexto:
*"esta práctica se relaciona con el artículo X del RGPD — este es tu derecho"*.

**Por qué separada:** si el artículo sumara puntos, volveríamos a medir cumplimiento,
que es justo lo que decidimos no hacer (§7.1).

**Fuente:** el mapeo de Poplavska et al. (2020) del §1.2, publicado y auditable.
No se usa el campo de artículos RGPD de la extensión (§1.3), porque sale de un motor
de reglas léxicas y no de una tabla citable: no se podría defender ante una pregunta
de "¿de dónde sale que este párrafo es el artículo 28?".

- [ ] **TODO:** aplicar el mapeo descargado y fijar el artículo (o artículos) que se
  muestra para cada una de las nueve categorías, con texto explicativo para no
  juristas.

## 9. Contrato de salida del modelo

Este contrato lo consumen **tres** piezas: la API, la demo de Streamlit y la
extensión de Chrome. Se define **completo desde el principio** para no tener que
rehacerlo cuando llegue la extensión.

Nivel de detalle acordado: **documento + fragmento**.

```json
{
  "model_version": "0.1.0",
  "document": {
    "source_language": "es",
    "translated": true,
    "exposure": {
      "level": "high",
      "score": 0.72,
      "disclaimer": "Estimación basada en los temas detectados, no en una lectura cláusula por cláusula."
    },
    "categories": [
      {
        "id": "third_party_sharing_collection",
        "present": true,
        "confidence": 0.91,
        "fragment_count": 7,
        "gdpr_reference": "TODO"
      }
    ],
    "fragment_count": 84
  },
  "fragments": [
    {
      "id": 12,
      "text": "Podemos compartir tu información con nuestros socios publicitarios.",
      "start": 4210,
      "end": 4276,
      "labels": [
        { "id": "third_party_sharing_collection", "score": 0.88 }
      ]
    }
  ]
}
```

Notas del contrato:

- Los **nombres de campo van en inglés**, según la convención de idioma del repo.
- `text`, `start` y `end` se refieren **siempre al documento original**, no a su
  traducción (§5, regla 1). Las posiciones son lo que permite a la extensión resaltar
  el párrafo en la página.
- `translated` indica si el fragmento pasó por el traductor, para poder desglosar
  métricas y avisar al usuario.
- El bloque `fragments` permite a la extensión resaltar el párrafo concreto.
  **Streamlit no está obligado a pintarlo en el MVP**: el campo existe desde el
  principio, la interfaz lo muestra cuando dé tiempo.
- `confidence` a nivel de documento y `score` a nivel de fragmento salen de las
  probabilidades del modelo multi-etiqueta.

## 10. Qué muestra cada pieza

| Pieza | Muestra | Nivel |
|---|---|---|
| **Streamlit** (demo) | Categorías detectadas + aviso de estimación + aviso si la traducción no está disponible | Esencial |
| **Informe técnico** | Métricas, macro-F1 global y por idioma, análisis de errores, límites | Esencial |
| **Semáforo** | Nivel de exposición bajo/medio/alto | Medio |
| **API** | El contrato completo del §9 | Avanzado |
| **Extensión de Chrome** | Semáforo en la web visitada + resaltado por fragmento | Aspiracional |

## 11. Fuera de alcance

Queda **explícitamente fuera** de este proyecto:

- Leer los **subatributos** de OPP-115 (el detalle fino de cada práctica).
- Emitir juicios de **cumplimiento legal** o asesoramiento jurídico.
- **Idiomas distintos del inglés y el español.**
- **Entrenar con etiquetas generadas automáticamente** sin validación humana.
- Capa MLOps (Champion/Challenger, A/B testing, data drift, auto-reemplazo).
- Despliegue en la nube, Docker, CI/CD.

## 12. Datos generados en el repositorio

**Norma:** se versiona **el script que genera** los datos, no su salida. Los datos
pequeños y citables (p. ej. el mapeo del RGPD, 83 KB) sí se versionan: son fuente,
no producto.

**Por qué:** git no sabe comparar archivos binarios, así que guarda cada versión
entera para siempre; y un pull request de 100.000 líneas no se revisa de verdad.

**Secuencia acordada** (el orden importa: hoy no existen scripts que regeneren los
artefactos, así que quitarlos ahora significaría perderlos):

1. Convertir los procesos existentes en scripts reproducibles.
2. Acordar la norma por escrito en `specs/`.
3. Solo entonces dejar de rastrear los archivos generados.

No se reescribe el historial del repositorio a mitad de sprint: obligaría a todo el
mundo a volver a clonar y rompería los pull requests abiertos.

## 13. Criterios de cierre por nivel

**Esencial (suelo protegido):** dataset documentado · EDA con visualizaciones ·
preprocesado reproducible · clasificador multi-etiqueta de las nueve categorías
funcionando · macro-F1 con gap train/validación <5% · español vía traducción con
degradación elegante · conjunto de prueba en español validado a mano · demo en
Streamlit · informe técnico · README ejecutable sin necesidad de claves.

**Medio:** capa de exposición implementada y justificada · ≥4 modelos base +
meta-modelo por stacking.

**Avanzado:** mapeo RGPD integrado en la salida · API sirviendo el contrato del §9.

**Aspiracional:** extensión de Chrome · presentaciones pulidas.

---

## 14. Pendientes (TODO)

- [ ] Pipeline de **preprocesado de texto** (limpieza + vectorización).
- [ ] **Umbral** de decisión multi-etiqueta (§2.3).
- [ ] Elegir los **≥4 modelos base** tras la investigación en la literatura (§6).
- [ ] **Pesos y umbrales** del semáforo (§7.2).
- [ ] **Mapeo RGPD** categoría → artículo + texto para no juristas (§8).
- [ ] **Proveedor de traducción** y sus cuotas (§5).
- [ ] **Cómo etiquetar** el conjunto de prueba en español (§4.3).
- [ ] Ratificar el **idioma** de las specs.

## 15. Cambios respecto a la versión 0.1

- Añadido §1.3: la extensión del dataset, su rol acordado (evaluación y demo) y sus
  características a tener en cuenta.
- Añadido §1.2 con la fuente concreta del mapeo RGPD, ya localizada.
- Nuevo §5: idiomas. El español entra vía traducción en la inferencia, con reglas de
  implementación (traducción interna, degradación elegante, caché, credenciales).
- Nuevo §4.2 (deduplicación) y §4.3 (conjunto de prueba en español).
- Nuevo §12: norma de datos generados en el repositorio, con la secuencia a seguir.
- §9: el contrato ahora devuelve **posiciones del texto original** y campos de idioma.
  TODO de "texto vs. posición" cerrado.
- §11: el español sale de "fuera de alcance"; entra la prohibición de entrenar con
  etiquetas sin validar.
- Añadidas las rutas descartadas y su motivo en §2.1, §5, §7.2 y §8.
