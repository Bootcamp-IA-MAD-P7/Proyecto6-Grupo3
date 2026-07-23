#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Alinea el tablero de GitHub con specs/ (1_intent, 2_spec, 3_plan v0.2)
#
# QUE HACE:
#   1. Crea las etiquetas de frente / nivel / apto-junior / bloqueante
#   2. EDITA los issues que ya existen (no los borra ni los recrea)
#   3. CREA los issues nuevos que pide el plan
#
# NO asigna personas: eso se hace despues en GitHub, o con
#   gh issue edit <N> --add-assignee <usuario>
#
# ANTES DE EJECUTAR:
#   a) gh auth status          -> comprobar que estas autenticada
#   b) bash 00_listar.sh       -> ver los numeros reales de los issues
#   c) rellenar el bloque NUMEROS de abajo
#   d) leerlo entero: modifica el tablero de todo el equipo
# ---------------------------------------------------------------------------
set -uo pipefail

REPO="Bootcamp-IA-MAD-P7/Proyecto6-Grupo3"

# ===========================================================================
# NUMEROS DE LOS ISSUES QUE YA EXISTEN
# Rellena cada variable con el numero del issue correspondiente.
# Deja en blanco los que no quieras tocar: el script los salta.
# Para verlos:  gh issue list --repo "$REPO" --limit 30
# ===========================================================================
I_ROLES="1"          # "Definir roles del equipo"
I_MODELOS_INV="2"    # "Investigar y seleccionar los modelos candidatos"
I_STACK="3"          # "Definir el stack del equipo"
I_ENTORNO="4"        # "Configurar la estructura del repo y el entorno"
I_DATASET="5"        # "Descargar y versionar el dataset OPP-115"
I_EDA="6"            # "Explorar la distribucion de las 10 categorias (EDA)"
I_RGPD="7"           # "Documentar el mapeo OPP-115 -> articulos RGPD"
I_PREPRO="8"         # "Definir el pipeline de preprocesado de texto"
I_MODELOS="9"        # "Entrenar los modelos base" -> pasa a ser el modelo 1

# ---------------------------------------------------------------------------
say() { printf '\n\033[1;34m==>\033[0m %s\n' "$1"; }
skip() { printf '    (saltado: %s sin numero)\n' "$1"; }

# ===========================================================================
# 1. ETIQUETAS
# ===========================================================================
say "Creando etiquetas"

crear_label() {
  gh label create "$1" --color "$2" --description "$3" --repo "$REPO" 2>/dev/null \
    && echo "    creada: $1" \
    || echo "    ya existia: $1"
}

crear_label "frente:datos"     "1D76DB" "Dataset, EDA, preprocesado, modelos, metricas"
crear_label "frente:producto"  "0E8A16" "Streamlit, traduccion, API, extension"
crear_label "frente:legal-qa"  "5319E7" "RGPD, semaforo, informe, coherencia"
crear_label "nivel:esencial"   "B60205" "Suelo protegido: no se corta"
crear_label "nivel:extra"      "FBCA04" "Capa incremental: cortable y documentable"
crear_label "apto-junior"      "C2E0C6" "Se puede hacer con criterios claros y apoyo"
crear_label "bloqueante"       "D93F0B" "Otras tareas dependen de esta"

# ===========================================================================
# 2. EDITAR ISSUES EXISTENTES
# ===========================================================================

say "Roles y dueno de cada modelo"
if [ -n "$I_ROLES" ]; then
  gh issue edit "$I_ROLES" --repo "$REPO" \
    --title "Definir roles del equipo y dueno de cada modelo" \
    --add-label "bloqueante,nivel:esencial,apto-junior" \
    --body "$(cat <<'EOF'
**Que hay que hacer:** asignar cada persona a un frente (Datos y modelo / Producto / Legal-Exposicion-QA) y designar quien es dueno de cada modelo base.

**Frente:** los tres
**Depende de:** nada
**Apto junior:** si
**Criterio de terminado:** la tabla de frentes de `specs/3_plan.md` §4 tiene nombres, y cada modelo base tiene una persona asignada en el tablero.
**Comando de verificacion:** `gh issue list --repo REPO --label "frente:datos" --json number,assignees` devuelve dueno en cada modelo.
**Evidencia:** `specs/3_plan.md` actualizado + issues con asignacion.

> Bloqueante: sin duenos no hay reparto para el viernes.
EOF
)"
else skip "I_ROLES"; fi

say "Seleccion de los 4 modelos"
if [ -n "$I_MODELOS_INV" ]; then
  gh issue edit "$I_MODELOS_INV" --repo "$REPO" \
    --title "Cerrar que 4 modelos base se entrenan (diversos)" \
    --add-label "frente:legal-qa,bloqueante,nivel:esencial" \
    --body "$(cat <<'EOF'
**Que hay que hacer:** mapear que modelos se han probado sobre OPP-115 en la literatura y elegir cuatro de **familias distintas**.

**Frente:** Legal-Exposicion-QA (investigacion) con Datos y modelo
**Depende de:** nada
**Apto junior:** con apoyo
**Criterio de terminado:** los cuatro modelos estan escritos en `specs/2_spec.md` §6, con una linea de justificacion por cada uno y su ficha de fuente. Cubren familias distintas (p. ej. lineal sobre TF-IDF, arboles, embeddings), no cuatro variantes del mismo enfoque.
**Comando de verificacion:** `grep -A20 "Enfoque de modelado" specs/2_spec.md` muestra los cuatro sin TODO.
**Evidencia:** `specs/2_spec.md` §6 + fichas de fuente.

> Urgente: el viernes se entrena. Si no esta cerrado hoy, no hay reparto.
EOF
)"
else skip "I_MODELOS_INV"; fi

say "Stack"
if [ -n "$I_STACK" ]; then
  gh issue edit "$I_STACK" --repo "$REPO" \
    --add-label "nivel:esencial,apto-junior" \
    --body "$(cat <<'EOF'
**Que hay que hacer:** dejar el stack por escrito en `specs/`.

**Ya decidido:** uv como gestor, Python 3.12, pandas/numpy/matplotlib/seaborn/jupyter, Streamlit para la demo.
**Criterio de terminado:** el stack aparece en `specs/2_spec.md` o en el README, junto a la convencion de idioma del repo.
**Comando de verificacion:** `grep -ri "streamlit" specs/ README.md` devuelve resultado.
**Evidencia:** archivo en `specs/`.
EOF
)"
else skip "I_STACK"; fi

say "Entorno (cerrar)"
if [ -n "$I_ENTORNO" ]; then
  gh issue close "$I_ENTORNO" --repo "$REPO" \
    --comment "Hecho: estructura de carpetas creada, entorno uv configurado, pyproject.toml y uv.lock versionados, .venv ignorado."
else skip "I_ENTORNO"; fi

say "Dataset OPP-115"
if [ -n "$I_DATASET" ]; then
  gh issue edit "$I_DATASET" --repo "$REPO" \
    --add-label "frente:datos,bloqueante,nivel:esencial" \
    --body "$(cat <<'EOF'
**Que hay que hacer:** descargar OPP-115 a `data/dataset/` y versionar las instrucciones de descarga.

**Frente:** Datos y modelo
**Depende de:** nada
**Apto junior:** si
**Criterio de terminado:** los fragmentos y el **archivo de anotaciones** estan disponibles localmente, y el README de `data/dataset/` explica de donde se bajan y bajo que licencia (uso de investigacion y docencia, citando Wilson et al. 2016).
**Comando de verificacion:** `ls data/dataset/` lista fragmentos y anotaciones.
**Evidencia:** `data/dataset/README.md` con la fuente y la cita.

> Ojo: descargar no es lo mismo que construir el target. Eso es otro issue.
EOF
)"
else skip "I_DATASET"; fi

say "EDA (10 -> 9 categorias)"
if [ -n "$I_EDA" ]; then
  gh issue edit "$I_EDA" --repo "$REPO" \
    --title "EDA: distribucion de las 9 categorias, desbalance y etiquetas por fragmento" \
    --add-label "frente:datos,nivel:esencial,apto-junior" \
    --body "$(cat <<'EOF'
**Que hay que hacer:** analisis exploratorio sobre el target ya construido.

**Frente:** Datos y modelo
**Depende de:** construir el target multi-etiqueta
**Apto junior:** si
**Criterio de terminado:** el notebook muestra (1) distribucion de las **nueve** categorias, (2) el desbalance entre la mas y la menos frecuente, (3) **cuantas etiquetas lleva cada fragmento** de media, y (4) conclusiones escritas, no solo graficos.
**Comando de verificacion:** el notebook se ejecuta de arriba abajo sin errores y sin celdas con TODO.
**Evidencia:** notebook en `eda/` + figuras.

> Cambio respecto a la version anterior: son **nueve** categorias, no diez. `Other` queda fuera del target (specs/2_spec.md §2.2). La media de etiquetas por fragmento es el dato que justifica el enfoque multi-etiqueta.
EOF
)"
else skip "I_EDA"; fi

say "Preprocesado (bloqueante)"
if [ -n "$I_PREPRO" ]; then
  gh issue edit "$I_PREPRO" --repo "$REPO" \
    --title "Congelar el pipeline de preprocesado de texto (comun a los 4 modelos)" \
    --add-label "frente:datos,bloqueante,nivel:esencial" \
    --body "$(cat <<'EOF'
**Que hay que hacer:** un pipeline de limpieza y vectorizacion **unico**, ejecutable desde script, que usaran los cuatro modelos.

**Frente:** Datos y modelo
**Depende de:** construir el target multi-etiqueta
**Apto junior:** no como responsable unico
**Criterio de terminado:** el pipeline vive en un script versionado, es determinista, y dos personas distintas obtienen exactamente el mismo resultado al ejecutarlo.
**Comando de verificacion:** ejecutar el script dos veces y comparar hashes de la salida.
**Evidencia:** script + salida documentada.

> Bloqueante y critico: si cada persona preprocesa a su manera, los cuatro modelos no son comparables y el meta-modelo no es posible (specs/3_plan.md §3).
EOF
)"
else skip "I_PREPRO"; fi

say "Mapeo RGPD (cambia de naturaleza, pasa a Fase B)"
if [ -n "$I_RGPD" ]; then
  gh issue edit "$I_RGPD" --repo "$REPO" \
    --title "Aplicar el mapeo OPP-115 -> RGPD de Poplavska et al. (2020)" \
    --add-label "frente:legal-qa,nivel:extra,apto-junior" \
    --body "$(cat <<'EOF'
**Que hay que hacer:** convertir el mapeo publicado en una tabla de consulta categoria -> articulo, con texto explicativo para no juristas.

**Frente:** Legal-Exposicion-QA
**Depende de:** descargar y versionar el zip del mapeo (83 KB)
**Apto junior:** si
**Criterio de terminado:** cada una de las nueve categorias tiene su articulo (o articulos) del RGPD y una explicacion en lenguaje llano. La fuente esta citada.
**Comando de verificacion:** la tabla cubre las 9 categorias sin huecos.
**Evidencia:** tabla en `specs/` + zip versionado.

> Ya no hay que investigar desde cero: el mapeo existe publicado (JURIX 2020, DOI 10.3233/FAIA200874), se descarga de usableprivacy.org/data y pesa 83 KB.
> NO se usa el campo de articulos RGPD de la extension del dataset: sale de reglas lexicas y no es trazable juridicamente (specs/2_spec.md §8).
EOF
)"
else skip "I_RGPD"; fi

say "Modelos base: el issue paraguas pasa a ser el modelo 1"
if [ -n "$I_MODELOS" ]; then
  gh issue edit "$I_MODELOS" --repo "$REPO" \
    --title "Entrenar modelo base 1" \
    --add-label "frente:datos,nivel:esencial" \
    --body "$(cat <<'EOF'
**Que hay que hacer:** entrenar un modelo base multi-etiqueta de las 9 categorias sobre el pipeline y la particion comunes.

**Frente:** Datos y modelo
**Depende de:** pipeline congelado + particion con semilla fija
**Apto junior:** con apoyo
**Criterio de terminado:** macro-F1 de train y de validacion calculadas, **gap** anotado, y la fila del modelo rellenada en la tabla comparativa. Si el gap supera el 5%, se documenta como bloqueo en lugar de ocultarlo.
**Comando de verificacion:** el script de entrenamiento se ejecuta y devuelve las metricas.
**Evidencia:** metricas + fila en la tabla comparativa.

> Partido en cuatro issues (uno por modelo y por persona) para que cada uno tenga su tarjeta, su metrica y su evidencia.
EOF
)"
else skip "I_MODELOS"; fi

# ===========================================================================
# 3. CREAR ISSUES NUEVOS
# ===========================================================================

nuevo() {
  local titulo="$1" etiquetas="$2" cuerpo="$3"
  gh issue create --repo "$REPO" --title "$titulo" --label "$etiquetas" --body "$cuerpo" \
    && echo "    creado: $titulo"
}

say "Fase A - hoy"

nuevo "Construir el target multi-etiqueta (fragmentos x 9 categorias)" \
  "frente:datos,bloqueante,nivel:esencial" \
"$(cat <<'EOF'
**Que hay que hacer:** cruzar los fragmentos de OPP-115 con el archivo de anotaciones para producir la matriz de target: una fila por fragmento, nueve columnas binarias.

**Frente:** Datos y modelo
**Depende de:** descargar OPP-115
**Apto junior:** no como responsable unico
**Criterio de terminado:** existe la matriz con ~3.800 filas y 9 columnas. `Other` **no** es columna; los fragmentos anotados solo como `Other` se conservan con todo a cero. La media de etiquetas por fragmento queda documentada.
**Comando de verificacion:** imprimir dimensiones de la matriz y media de etiquetas por fila.
**Evidencia:** script + salida con las dimensiones.

> Sin este cruce el texto es mudo: no hay nada que aprender. Ver specs/2_spec.md §2.
EOF
)"

nuevo "Deduplicar y crear la particion por politica con semilla fija" \
  "frente:datos,bloqueante,nivel:esencial" \
"$(cat <<'EOF'
**Que hay que hacer:** eliminar duplicados exactos y repartir las 115 politicas **enteras** entre train / validacion / test.

**Frente:** Datos y modelo
**Depende de:** construir el target multi-etiqueta
**Apto junior:** no como responsable unico
**Criterio de terminado:** ninguna politica aparece en dos grupos. La semilla esta fijada y escrita. La distribucion de las 9 categorias por grupo queda documentada. Los duplicados exactos se eliminan **antes** de partir.
**Comando de verificacion:** un script comprueba que la interseccion de identificadores de politica entre los tres grupos esta vacia.
**Evidencia:** script de particion + tabla de distribucion por grupo.

> Si se parte por fragmento, trozos de la misma politica caen en train y test, el modelo reconoce el estilo de la empresa y las metricas salen infladas (specs/2_spec.md §4).
EOF
)"

nuevo "Congelar el contrato de salida del modelo" \
  "frente:producto,bloqueante,nivel:esencial" \
"$(cat <<'EOF'
**Que hay que hacer:** dejar el contrato de `specs/2_spec.md` §9 cerrado y revisado por los tres frentes.

**Frente:** Producto
**Depende de:** nada
**Apto junior:** con apoyo
**Criterio de terminado:** existe un JSON de ejemplo valido. `text`, `start` y `end` se refieren siempre al **documento original**, no a su traduccion. Los tres frentes lo han leido y confirmado.
**Comando de verificacion:** el JSON de ejemplo se parsea sin errores.
**Evidencia:** `specs/2_spec.md` §9 + JSON de ejemplo.

> Es lo que permite que la interfaz se construya sin esperar al modelo, y lo que evita que API, Streamlit y extension asuman cosas distintas.
EOF
)"

nuevo "Esqueleto de Streamlit contra salida simulada" \
  "frente:producto,nivel:esencial,apto-junior" \
"$(cat <<'EOF'
**Que hay que hacer:** montar la pantalla de la demo pintando una salida **falsa** con el formato del contrato, sin modelo detras.

**Frente:** Producto
**Depende de:** contrato de salida congelado
**Apto junior:** si
**Criterio de terminado:** la app arranca, se pega un texto y se ven categorias (inventadas). Cuando el modelo real este listo, solo se cambia la fuente de datos.
**Comando de verificacion:** `uv run streamlit run <ruta>` abre la app y muestra categorias.
**Evidencia:** captura de la pantalla funcionando.

> Compensa que el suelo no se cierre hasta el dia 5: el martes no se empieza de cero.
EOF
)"

nuevo "Unificar el flujo de ramas (main y dev divergen)" \
  "bloqueante,nivel:esencial" \
"$(cat <<'EOF'
**Que hay que hacer:** dejar un solo camino de integracion y alinear las dos ramas principales.

**Frente:** los tres
**Depende de:** nada
**Apto junior:** con apoyo
**Criterio de terminado:** `main` y `dev` tienen historia comun, esta escrito cual es la rama de integracion, y el equipo lo sabe. A partir de ahi: rama por tarea -> PR -> rama de integracion.
**Comando de verificacion:** `git log --oneline --graph origin/main origin/dev` no muestra dos lineas paralelas sin punto de union.
**Evidencia:** grafo del log + la norma escrita.

> Urgente hoy: cuatro personas entrenando en paralelo sobre ramas divergentes es trabajo perdido garantizado.
EOF
)"

nuevo "Definir el formato de la tabla comparativa de modelos" \
  "frente:legal-qa,nivel:esencial,apto-junior" \
"$(cat <<'EOF'
**Que hay que hacer:** crear la tabla vacia que rellenara cada dueno de modelo, con columnas acordadas.

**Frente:** Legal-Exposicion-QA
**Depende de:** nada
**Apto junior:** si
**Criterio de terminado:** la tabla tiene, como minimo: modelo, familia, representacion del texto, macro-F1 train, macro-F1 validacion, gap, observaciones. Vive en un solo archivo compartido.
**Comando de verificacion:** el archivo existe con las columnas y una fila por modelo previsto.
**Evidencia:** archivo de la tabla.

> Definirla antes evita que cada persona reporte metricas en formato distinto y haya que rehacer los calculos.
EOF
)"

say "Fase A - modelos 2, 3 y 4"

for n in 2 3 4; do
  nuevo "Entrenar modelo base $n" \
    "frente:datos,nivel:esencial" \
"$(cat <<EOF
**Que hay que hacer:** entrenar el modelo base $n (familia distinta a los demas) sobre el pipeline y la particion comunes.

**Frente:** Datos y modelo
**Depende de:** pipeline congelado + particion con semilla fija + seleccion de los 4 modelos
**Apto junior:** con apoyo
**Criterio de terminado:** macro-F1 de train y validacion, **gap** anotado, y fila rellenada en la tabla comparativa. Si el gap supera el 5%, se documenta como bloqueo.
**Comando de verificacion:** el script de entrenamiento se ejecuta y devuelve las metricas.
**Evidencia:** metricas + fila en la tabla comparativa.

> La diversidad importa mas que la cantidad: este modelo debe pertenecer a una familia distinta de los otros tres.
EOF
)"
done

nuevo "Entrenar el meta-modelo por stacking" \
  "frente:datos,nivel:extra" \
"$(cat <<'EOF'
**Que hay que hacer:** entrenar un meta-modelo que combine las predicciones de los cuatro modelos base.

**Frente:** Datos y modelo
**Depende de:** los cuatro modelos base
**Apto junior:** no como responsable unico
**Criterio de terminado:** el meta supera a los base en macro-F1, o se justifica por estabilidad, o se documenta que no mejora. Cumple el gap por debajo del 5%.
**Comando de verificacion:** metricas del meta comparadas con las de los base en la misma particion.
**Evidencia:** fila del meta en la tabla comparativa.

> Cortable (specs/3_plan.md §8): si no cabe, se conservan los cuatro base y su comparativa.
EOF
)"

say "Fase B - producto y capas"

nuevo "Traduccion es->en con cache y degradacion elegante" \
  "frente:producto,nivel:esencial" \
"$(cat <<'EOF'
**Que hay que hacer:** traducir al ingles los fragmentos en espanol antes de clasificarlos, de forma interna y desechable.

**Frente:** Producto
**Depende de:** contrato de salida congelado
**Apto junior:** con apoyo
**Criterio de terminado:** (1) al usuario se le devuelve su **texto original**, no la traduccion; (2) hay **cache** indexada por hash del texto; (3) **degradacion elegante**: sin clave o sin red, la app avisa y sigue funcionando en ingles en lugar de caerse; (4) la clave vive en `.env` (ignorado) y hay un `.env.example` versionado.
**Comando de verificacion:** arrancar la app **sin** clave configurada: debe funcionar en ingles y avisar sobre el espanol.
**Evidencia:** captura del aviso + `.env.example` en el repo.

> Requisito del suelo: es lo que permite que otra persona ejecute el proyecto desde el README sin registrarse en ningun servicio (specs/2_spec.md §5).
EOF
)"

nuevo "Fijar pesos y umbrales del semaforo de exposicion" \
  "frente:legal-qa,nivel:extra" \
"$(cat <<'EOF'
**Que hay que hacer:** convertir las categorias detectadas en un nivel de exposicion bajo/medio/alto, con pesos y cortes justificados.

**Frente:** Legal-Exposicion-QA
**Depende de:** un clasificador funcionando
**Apto junior:** con apoyo
**Criterio de terminado:** cada peso tiene una linea de justificacion basada en **impacto sobre la privacidad**, no en gravedad legal. Los umbrales estan escritos. La interfaz muestra el aviso de que es una **estimacion**.
**Comando de verificacion:** con una salida de ejemplo, el semaforo devuelve el nivel esperado.
**Evidencia:** tabla de pesos + justificacion en `specs/2_spec.md` §7.

> Legal != expuesto: una practica puede cumplir el RGPD y aun asi exponerte mucho. Esta capa no sale del dataset, la disena el equipo.
EOF
)"

nuevo "Sesion de verificacion en espanol (30-40 fragmentos, todo el equipo)" \
  "frente:legal-qa,nivel:esencial,apto-junior" \
"$(cat <<'EOF'
**Que hay que hacer:** revisar a mano entre todo el equipo 30-40 fragmentos en espanol y comprobar si el modelo acierta.

**Frente:** todo el equipo, una sola sesion
**Depende de:** clasificador + traduccion funcionando
**Apto junior:** si
**Criterio de terminado:** hay un recuento del tipo "revisamos N fragmentos y el modelo acerto en M", presentado como **verificacion** y no como metrica publicable. Los fragmentos salen de la extension del dataset.
**Comando de verificacion:** la hoja de revision esta completa y contabilizada.
**Evidencia:** hoja de revision + parrafo en el informe.

> NO se mide contra la preanotacion automatica de la extension: eso diria si nuestro modelo se parece a un buscador de palabras clave, no si acierta (specs/2_spec.md §4.3).
EOF
)"

nuevo "Escribir la norma de datos generados en specs/" \
  "nivel:esencial,apto-junior" \
"$(cat <<'EOF'
**Que hay que hacer:** dejar por escrito que se versiona en el repositorio y que no.

**Frente:** los tres
**Depende de:** nada
**Apto junior:** si
**Criterio de terminado:** la norma esta en `specs/`: se versiona **el script que genera** los datos, no su salida; los datos pequenos y citables si (p. ej. el mapeo RGPD de 83 KB). Incluye la secuencia: (1) convertir procesos en scripts, (2) acordar la norma, (3) solo entonces dejar de rastrear.
**Comando de verificacion:** `grep -ri "datos generados" specs/` devuelve la norma.
**Evidencia:** archivo en `specs/`.

> No se reescribe el historial a mitad de proyecto: obligaria a todo el mundo a volver a clonar y romperia los PR abiertos.
EOF
)"

say "Listo. Revisa el tablero:"
echo "    gh issue list --repo $REPO --limit 40"
echo ""
echo "Para asignar personas (se hace ahora, no en este script):"
echo "    gh issue edit <N> --repo $REPO --add-assignee <usuario>"
