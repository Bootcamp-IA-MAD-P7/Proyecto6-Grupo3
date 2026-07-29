"""
10_build_multiclass_target.py — paso 1 del enfoque multiclase.

QUE HACE
Convierte el target multi-etiqueta (9 columnas 0/1) en un target MULTICLASE de una sola
columna con 10 clases: las 9 practicas de datos mas `Other`. No entrena nada, no toca las
matrices TF-IDF. Solo construye la etiqueta, la verifica y la guarda.

POR QUE
La rubrica del proyecto pide clasificacion multiclase sobre las 10 categorias de OPP-115.
El corpus esta anotado multi-etiqueta (un fragmento puede describir varias practicas), asi
que derivar una sola etiqueta por fragmento exige una REGLA DE DESEMPATE explicita.

LA REGLA: PRIORIDAD POR RELEVANCIA PARA LA PRIVACIDAD
Cuando un fragmento describe varias practicas, se etiqueta con la MAS CONSECUENTE para la
exposicion del usuario. El orden no es estadistico (no es "gana la mas rara"), es de
producto, y se justifica con el principio rector del proyecto: medimos exposicion de la
privacidad, no cumplimiento legal (1_intent).

  1. third_party_sharing_collection    los datos salen de la empresa: el hecho mas grave
  2. data_retention                    cuanto tiempo permanecen
  3. do_not_track                      señal de rastreo
  4. user_access_edit_deletion         derechos RGPD arts. 15-17
  5. user_choice_control               control sobre el tratamiento
  6. data_security                     proteccion
  7. international_specific_audiences  grupos concretos y transferencias
  8. policy_change                     informativo
  9. first_party_collection_use        recogida propia: es el fondo de armario, casi
                                       siempre implicito cuando hay cualquier otra

Si ninguna de las 9 esta presente -> clase `Other` (relleno legal: introduccion,
contacto, definiciones). Son los 520 fragmentos que en el enfoque multi-etiqueta
quedaban con las 9 columnas a cero.

LO QUE SE CONSERVA SIN TOCAR
- La particion oficial: split_assignment.csv, semilla 42, por politica (issue #18).
  Ninguna fila cambia de grupo. La ausencia de group leakage se mantiene.
- Las matrices TF-IDF de artifacts/: las features son las mismas, solo cambia la y.
- La clave natural (policy, segment).

LIMITACION A DECLARAR EN EL INFORME
Los 1.147 fragmentos con 2 o mas practicas (30,2% del corpus) reciben una etiqueta que es
resultado de esta regla, no una decision de los anotadores. Se declara explicitamente: el
corpus original es multi-etiqueta y este target es una derivacion documentada.

COMO SE EJECUTA (desde la raiz del repo)
    uv run python scripts/10_build_multiclass_target.py
"""

from pathlib import Path

import pandas as pd

TRAINING_TABLE = Path("data/processed/training_table.csv")
SPLIT_ASSIGNMENT = Path("data/processed/split_assignment.csv")
OUT = Path("data/processed/multiclass_target.csv")

# Orden de prioridad. NO reordenar sin actualizar el docstring y el informe: cambiarlo
# cambia el target y por tanto todas las metricas.
PRIORITY = [
    "third_party_sharing_collection",
    "data_retention",
    "do_not_track",
    "user_access_edit_deletion",
    "user_choice_control",
    "data_security",
    "international_specific_audiences",
    "policy_change",
    "first_party_collection_use",
]
OTHER = "Other"
CLASSES = PRIORITY + [OTHER]


def require(path: Path) -> Path:
    """Un archivo que falta es un crash, no un fallback (2_spec §6.2)."""
    if not path.exists():
        raise FileNotFoundError(
            f"No existe {path}. Ejecuta antes scripts/02_build_target.py y "
            f"scripts/04_build_split.py, desde la raiz del repo."
        )
    return path


def assign_class(row) -> str:
    """Devuelve la primera practica presente segun PRIORITY, u `Other` si no hay ninguna."""
    for name in PRIORITY:
        if row[name] == 1:
            return name
    return OTHER


# ------------------------------------------------------- 1) cargar y cruzar
df = pd.read_csv(require(TRAINING_TABLE))
split = pd.read_csv(require(SPLIT_ASSIGNMENT))

missing = [c for c in ["policy", "segment", *PRIORITY] if c not in df.columns]
if missing:
    raise KeyError(f"Faltan columnas en training_table.csv: {missing}")

# validate="one_to_one": pandas grita si hay claves duplicadas o que no cruzan, en lugar
# de multiplicar filas en silencio.
data = df.merge(split, on=["policy", "segment"], validate="one_to_one")

# ------------------------------------------------------- 2) construir la etiqueta
data["label"] = data.apply(assign_class, axis=1)

n_practicas = data[PRIORITY].sum(axis=1)
n_empates = int((n_practicas >= 2).sum())

print("=== target multiclase construido ===")
print(f"filas            : {len(data)}")
print(f"clases           : {data['label'].nunique()} de {len(CLASSES)} esperadas")
print(f"fragmentos con 1 practica  : {int((n_practicas == 1).sum())}")
print(f"fragmentos con 0 practicas : {int((n_practicas == 0).sum())}  -> Other")
print(f"fragmentos con 2+ (empates resueltos por la regla): {n_empates} "
      f"({100*n_empates/len(data):.1f}%)")

# ------------------------------------------------------- 3) distribucion global
print("\n=== distribucion de clases ===")
vc = data["label"].value_counts()
print(f"{'clase':36s} {'n':>6s} {'%':>7s}")
for c in CLASSES:
    n = int(vc.get(c, 0))
    print(f"{c:36s} {n:6d} {100*n/len(data):6.1f}%")
print(f"\ndesbalance: {vc.max()/vc.min():.1f}:1")
print(f"clase mayoritaria: {vc.idxmax()} con {100*vc.max()/len(data):.1f}%")
print(f"  -> ese % es el SUELO de accuracy: un modelo que prediga siempre esa clase")
print(f"     lo alcanza sin aprender nada. Cualquier modelo debe superarlo.")

# --------------------------- 4) verificacion que PUEDE fallar: cobertura por split
print("\n=== las 10 clases en los tres grupos de la particion ===")
tab = pd.crosstab(data["label"], data["split"]).reindex(index=CLASSES, fill_value=0)
for col in ["train", "val", "test"]:
    if col not in tab.columns:
        raise ValueError(f"El split '{col}' no aparece en split_assignment.csv")
print(tab[["train", "val", "test"]].to_string())

vacias = []
for c in CLASSES:
    for col in ["train", "val", "test"]:
        if tab.loc[c, col] == 0:
            vacias.append((c, col))

if vacias:
    detalle = ", ".join(f"{c} sin ejemplos en {col}" for c, col in vacias)
    raise ValueError(
        f"COBERTURA INSUFICIENTE: {detalle}. Una clase ausente de train no se puede "
        f"aprender; ausente de val no se puede medir. Opciones: cambiar de semilla y "
        f"DEJAR REGISTRO de las probadas (2_spec §4.4), o fusionar la clase con otra y "
        f"documentarlo. NO mover filas a mano."
    )

print("\nOK: las 10 clases estan presentes en train, val y test.")

flojas = [c for c in CLASSES if tab.loc[c, "val"] < 10]
if flojas:
    print("\nAVISO — clases con menos de 10 ejemplos en val:")
    for c in flojas:
        print(f"  {c}: {tab.loc[c,'val']} en val. Su F1 sera inestable: un solo fallo lo")
        print(f"     mueve mucho. Se reporta SIEMPRE con el numero de ejemplos al lado.")

# ------------------------------------------------------- 5) guardar
data[["policy", "segment", "label", "split"]].to_csv(OUT, index=False)
print(f"\nEscrito: {OUT}")
print("  columnas: policy, segment, label, split")
print("  el orden de filas es el de training_table.csv, asi que la columna `label`")
print("  se alinea posicionalmente con las matrices X_*.npz de artifacts/.")
