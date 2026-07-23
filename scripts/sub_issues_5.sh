#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Sub-issues del #5 "Descargar y versionar el dataset OPP-115"
#
# Ejecutar:  bash sub_issues_5.sh
# ---------------------------------------------------------------------------
set -uo pipefail
REPO="Bootcamp-IA-MAD-P7/Proyecto6-Grupo3"

# Por si las etiquetas no existen todavia
for l in "frente:datos|1D76DB" "frente:legal-qa|5319E7" "bloqueante|D93F0B" \
         "nivel:esencial|B60205" "nivel:extra|FBCA04" "apto-junior|C2E0C6"; do
  gh label create "${l%%|*}" --color "${l##*|}" --repo "$REPO" 2>/dev/null || true
done

# ---------------------------------------------------------------------------
# 1. La tabla de entrenamiento
# ---------------------------------------------------------------------------
gh issue create --repo "$REPO" \
  --title "Unir OPP-115 con sus anotaciones y construir la tabla de entrenamiento" \
  --label "frente:datos,bloqueante,nivel:esencial" \
  --body "Parent: #5

**Que hay que hacer:** cruzar los fragmentos de OPP-115 con su archivo de anotaciones y producir la tabla que se usara para entrenar: una fila por fragmento, nueve columnas de etiqueta (0/1).

**De aqui salen el EDA, la particion y el entrenamiento.** Es la unica fuente de entrenamiento del proyecto.

**Frente:** Datos y modelo
**Depende de:** que la descarga incluya el archivo de anotaciones
**Apto junior:** no como responsable unico
**Criterio de terminado:**
- La tabla tiene ~3.800 filas y 9 columnas de etiqueta.
- 'Other' NO es columna. Los fragmentos anotados solo como 'Other' se conservan con todo a cero.
- Queda documentada la media de etiquetas por fragmento (es el dato que justifica el multi-etiqueta).
**Comando de verificacion:** imprimir dimensiones de la tabla y media de etiquetas por fila.
**Evidencia:** script + salida con las dimensiones.

Ref: specs/2_spec.md §2"

# ---------------------------------------------------------------------------
# 2. Tabla de consulta RGPD
# ---------------------------------------------------------------------------
gh issue create --repo "$REPO" \
  --title "Bajar y versionar el mapeo RGPD (Poplavska et al. 2020)" \
  --label "frente:legal-qa,nivel:esencial,apto-junior" \
  --body "Parent: #5

**Que hay que hacer:** descargar JURIX_2020_OPP-115_GDPR_v1.0.zip (83 KB) de https://usableprivacy.org/data y versionarlo en el repo.

**Que es y que no es:** es una tabla de consulta categoria -> articulo del RGPD. NO es dato de parrafos, asi que NO se une a la tabla de entrenamiento: se consulta despues de clasificar, para mostrar el articulo al usuario.

**Frente:** Legal-Exposicion-QA
**Depende de:** nada
**Apto junior:** si
**Criterio de terminado:**
- El zip esta en el repo (pesa 83 KB, se versiona sin problema).
- Existe una tabla legible con las nueve categorias y su articulo o articulos.
- La cita esta escrita: Poplavska, Norton, Wilson & Sadeh (2020), JURIX 2020, DOI 10.3233/FAIA200874. Licencia CC BY-NC, uso de investigacion y docencia.
**Comando de verificacion:** la tabla cubre las 9 categorias sin huecos.
**Evidencia:** zip versionado + tabla.

Ref: specs/2_spec.md §1.2 y §8"

# ---------------------------------------------------------------------------
# 3. La extension como conjunto de evaluacion
# ---------------------------------------------------------------------------
gh issue create --repo "$REPO" \
  --title "Preparar la extension del dataset como conjunto de evaluacion" \
  --label "frente:datos,nivel:esencial" \
  --body "Parent: #5

**Que hay que hacer:** dejar los parrafos de la extension listos para pasarles el modelo YA ENTRENADO y medir como se comporta con texto actual y en espanol.

**Para que sirve:** es donde se responde 'detecta vocabulario nuevo?'. Se comprueba con evidencia sobre politicas de 2026, no con el corpus de 2016.

**Por que NO entra al entrenamiento (specs/2_spec.md §11):** sus etiquetas las genero una regla de palabras clave sin revision humana. Un modelo entrenado con ellas aprende a imitar esa regla, con sus errores incluidos, y las metricas dejan de decir si acierta. Para entrenar harian falta cientos de parrafos validados a mano; con seis dias no cabe.

**Frente:** Datos y modelo
**Depende de:** nada (se puede hacer en paralelo al entrenamiento)
**Apto junior:** con apoyo
**Criterio de terminado:**
- Eliminados los duplicados exactos intra-documento (hay 3.434 detectados).
- Los parrafos quedan en un formato que el modelo pueda consumir directamente.
- Separados por idioma, para poder reportar resultados de espanol y de ingles por separado.
- Las etiquetas automaticas se conservan como referencia, marcadas claramente como NO validadas.
**Comando de verificacion:** pasar una politica por el modelo entrenado y obtener categorias.
**Evidencia:** conjunto preparado + primera pasada documentada.

Nota: los 30-40 fragmentos de la sesion de verificacion del martes salen de aqui."

# ---------------------------------------------------------------------------
# 4. Binarios pesados
# ---------------------------------------------------------------------------
gh issue create --repo "$REPO" \
  --title "Resolver los archivos binarios pesados del repositorio" \
  --label "frente:datos,nivel:extra" \
  --body "Parent: #5

**Que hay que hacer:** dejar de versionar datos generados, en el orden correcto para no perderlos.

**Situacion:** ~193.000 lineas de datos generados y dos .parquet binarios en el repo. Git guarda cada version entera de un binario, para siempre; y un PR de 100.000 lineas no se revisa de verdad.

**Frente:** Datos y modelo
**Depende de:** nada
**Apto junior:** no como responsable unico
**Criterio de terminado, EN ESTE ORDEN:**
1. Existen scripts que regeneran los artefactos con un comando. **Hoy no existen: si se borran los archivos ahora, se pierden.**
2. La norma esta escrita en specs/: se versiona el script que genera los datos, no su salida. Los datos pequenos y citables si (p. ej. el zip del mapeo RGPD, 83 KB).
3. Solo entonces: 'git rm -r --cached' de los generados + patrones en .gitignore.

**Lo que NO se hace:** reescribir el historial del repositorio a mitad de proyecto. Obligaria a todo el mundo a volver a clonar y romperia los PR abiertos.

**Comando de verificacion:** ejecutar el script de regeneracion y comparar con los artefactos existentes.
**Evidencia:** scripts versionados + norma en specs/ + .gitignore actualizado.

Ref: specs/2_spec.md §12"

# ---------------------------------------------------------------------------
gh issue comment 5 --repo "$REPO" --body "Sub-issues creados (buscar 'Parent: #5'):
- [ ] Unir OPP-115 con sus anotaciones -> tabla de entrenamiento (bloqueante)
- [ ] Bajar y versionar el mapeo RGPD de Poplavska
- [ ] Preparar la extension como conjunto de evaluacion
- [ ] Resolver los archivos binarios pesados

Arquitectura de datos acordada:
- **Entrenamiento:** solo OPP-115 con sus anotaciones de oro.
- **Evaluacion:** la extension del dataset (texto actual, espanol e ingles).
- **Consulta:** el mapeo RGPD, conectado a la salida del modelo, no al entrenamiento.

Este issue se cierra cuando OPP-115 este descargado y documentado."

echo ""
echo "Listo. Revisa: gh issue list --repo $REPO --limit 40"
