"""
02_build_target.py — Construye la tabla de entrenamiento de OPP-115.

Cruza los fragmentos (sanitized_policies) con las anotaciones consolidadas
(consolidation/threshold-0.75) y produce una tabla: una fila por fragmento,
nueve columnas de etiqueta (0/1). 'Other' NO es columna (2_spec §2.2).

Lee de  data/dataset/   ·   Escribe en  data/processed/
Uso:    uv run python scripts/02_build_target.py
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

# --- Configuracion (decisiones documentadas en specs/2_spec.md) -------------
DATASET = Path("data/dataset")
CONSOLIDATION = DATASET / "consolidation" / "threshold-0.75-overlap-similarity"
POLICIES = DATASET / "sanitized_policies"
OUT = Path("data/processed")

SEPARATOR = "|||"  # separador de fragmentos dentro de cada HTML

# Las 9 categorias del target. 'Other' queda fuera a proposito.
CATEGORIES = [
    "First Party Collection/Use",
    "Third Party Sharing/Collection",
    "User Choice/Control",
    "User Access, Edit and Deletion",
    "Data Retention",
    "Data Security",
    "Policy Change",
    "Do Not Track",
    "International and Specific Audiences",
]

# nombre de columna interno (ingles, sin espacios) por categoria
COLUMN = {
    "First Party Collection/Use": "first_party_collection_use",
    "Third Party Sharing/Collection": "third_party_sharing_collection",
    "User Choice/Control": "user_choice_control",
    "User Access, Edit and Deletion": "user_access_edit_deletion",
    "Data Retention": "data_retention",
    "Data Security": "data_security",
    "Policy Change": "policy_change",
    "Do Not Track": "do_not_track",
    "International and Specific Audiences": "international_specific_audiences",
}

# columnas del CSV de anotaciones (sin cabecera)
COL_POLICY_ID = 3
COL_SEGMENT = 4
COL_CATEGORY = 5


def read_fragments(html_path: Path) -> list[str]:
    """Devuelve la lista de fragmentos de una politica, limpiando el HTML."""
    text = html_path.read_text(encoding="utf-8", errors="replace")
    fragments = text.split(SEPARATOR)
    # quitar etiquetas HTML y espacios sobrantes
    return [re.sub(r"<[^>]+>", " ", f).strip() for f in fragments]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    if not CONSOLIDATION.exists():
        raise SystemExit(f"No existe {CONSOLIDATION} — revisa la ruta")

    unknown_categories: set[str] = set()
    rows: list[dict] = []
    n_policies = 0

    for ann_path in sorted(CONSOLIDATION.glob("*.csv")):
        # el HTML homologo tiene el mismo nombre base
        html_path = POLICIES / (ann_path.stem + ".html")
        if not html_path.exists():
            print(f"AVISO: sin HTML para {ann_path.name} — se salta")
            continue

        fragments = read_fragments(html_path)
        n_policies += 1

        # etiquetas por fragmento: {n_fragmento: set(categorias)}
        labels: dict[int, set[str]] = {}
        with ann_path.open(encoding="utf-8", errors="replace", newline="") as fh:
            for row in csv.reader(fh):
                if len(row) <= COL_CATEGORY:
                    continue
                seg = int(row[COL_SEGMENT])
                cat = row[COL_CATEGORY].strip()
                if cat == "Other":
                    continue  # decision 2_spec §2.2: fuera del target
                if cat not in COLUMN:
                    unknown_categories.add(cat)
                    continue
                labels.setdefault(seg, set()).add(cat)

        policy_name = ann_path.stem
        for i, fragment in enumerate(fragments):
            if not fragment:
                continue
            row_out = {
                "policy": policy_name,
                "segment": i,
                "text": fragment,
            }
            cats = labels.get(i, set())
            for cat in CATEGORIES:
                row_out[COLUMN[cat]] = 1 if cat in cats else 0
            rows.append(row_out)

    # --- verificacion (criterios del issue #31) -----------------------------
    label_cols = [COLUMN[c] for c in CATEGORIES]
    n_rows = len(rows)
    n_labels = sum(sum(r[c] for c in label_cols) for r in rows)
    n_with_any = sum(1 for r in rows if any(r[c] for c in label_cols))

    print(f"politicas procesadas : {n_policies}")
    print(f"filas (fragmentos)   : {n_rows}")
    print(f"columnas de etiqueta : {len(label_cols)}")
    print(f"media etiquetas/fila : {n_labels / n_rows:.2f}")
    print(f"fragmentos con alguna etiqueta: {n_with_any} "
          f"({100 * n_with_any / n_rows:.1f}%)")
    print("\netiquetas por categoria:")
    for c in label_cols:
        print(f"  {sum(r[c] for r in rows):>6}  {c}")

    if unknown_categories:
        print("\nOJO — categorias en los CSV que no reconoci (revisar escritura):")
        for c in sorted(unknown_categories):
            print(f"  {c!r}")

    # --- escribir ------------------------------------------------------------
    out_path = OUT / "training_table.csv"
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["policy", "segment", "text"] + label_cols)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nescrito: {out_path}")


if __name__ == "__main__":
    main()
