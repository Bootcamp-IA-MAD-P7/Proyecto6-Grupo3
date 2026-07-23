"""
03_prepare_evaluation_set.py — Prepara data/dataset_extension como conjunto de EVALUACION.

Cierra el issue #33: deduplica, convierte al esquema de scripts/02_build_target.py
(policy, segment, text + 9 columnas binarias con los mismos nombres internos) y
separa los parrafos por idioma para poder reportar macro-F1 por separado (2_spec §4.3).

NUNCA usar la salida de este script para entrenar (2_spec.md §11 y §1.3): las
etiquetas son de plata (regla lexica bilingue, sin revision humana). Por eso se
marca cada fila con label_source="silver_rules_not_validated".

Lee de  data/dataset_extension/Agent4/privacylens_dataset_v1_1.csv
Escribe en  data/processed/evaluation_es.csv  y  data/processed/evaluation_en.csv
Uso:    uv run python scripts/03_prepare_evaluation_set.py
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

SOURCE = Path("data/dataset_extension/Agent4/privacylens_dataset_v1_1.csv")
OUT = Path("data/processed")

LABEL_SOURCE = "silver_rules_not_validated"

# Mismos nombres internos que scripts/02_build_target.py (COLUMN). 'Other' NO es
# columna (2_spec §2.2): un parrafo solo-Other queda con las nueve a cero.
CATEGORY_COLUMN = {
    "First Party Collection/Use": "first_party_collection_use",
    "Third Party Sharing/Collection": "third_party_sharing_collection",
    "User Choice/Control": "user_choice_control",
    "User Access, Edit & Deletion": "user_access_edit_deletion",
    "Data Retention": "data_retention",
    "Data Security": "data_security",
    "Policy Change": "policy_change",
    "Do Not Track": "do_not_track",
    "International & Specific Audiences": "international_specific_audiences",
}
LABEL_COLUMNS = list(CATEGORY_COLUMN.values())

LANG_FILES = {"es": "evaluation_es.csv", "en": "evaluation_en.csv"}


def read_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def dedupe_intra_document(rows: list[dict]) -> tuple[list[dict], int]:
    """Elimina duplicados exactos de 'text' dentro del mismo document_id (2_spec §4.2)."""
    seen: dict[str, set[str]] = defaultdict(set)
    kept: list[dict] = []
    removed = 0
    for row in rows:
        doc = row["document_id"]
        text = row["text"]
        if text in seen[doc]:
            removed += 1
            continue
        seen[doc].add(text)
        kept.append(row)
    return kept, removed


def labels_for(row: dict) -> dict[str, int]:
    cats = {row["categoria_principal"], row["categoria_alternativa"]}
    cats.discard("")
    cats.discard("Other")
    unknown = cats - CATEGORY_COLUMN.keys()
    if unknown:
        raise SystemExit(f"Categorias no reconocidas: {unknown} — revisar CATEGORY_COLUMN")
    return {col: (1 if name in cats else 0) for name, col in CATEGORY_COLUMN.items()}


def convert(row: dict) -> dict:
    out = {
        "policy": row["document_id"],
        "segment": int(row["paragraph_number"]),
        "text": row["text"],
    }
    out.update(labels_for(row))
    out["language"] = row["paragraph_language"]
    out["label_source"] = LABEL_SOURCE
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if not SOURCE.exists():
        raise SystemExit(f"No existe {SOURCE} — revisa la ruta")

    rows = read_rows(SOURCE)
    n_before = len(rows)

    deduped, removed = dedupe_intra_document(rows)
    n_after = len(deduped)

    converted = [convert(row) for row in deduped]

    by_lang: dict[str, list[dict]] = defaultdict(list)
    for row in converted:
        by_lang[row["language"]].append(row)

    other_langs = sorted(set(by_lang) - set(LANG_FILES))
    if other_langs:
        n_other = sum(len(by_lang[lang]) for lang in other_langs)
        print(f"AVISO: idiomas fuera de es/en, no escritos: {other_langs} ({n_other} filas)")

    fieldnames = ["policy", "segment", "text"] + LABEL_COLUMNS + ["language", "label_source"]

    written: dict[str, Path] = {}
    for lang, filename in LANG_FILES.items():
        out_path = OUT / filename
        lang_rows = by_lang.get(lang, [])
        with out_path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(lang_rows)
        written[lang] = out_path

    # --- resumen -------------------------------------------------------------
    print(f"filas antes del dedupe  : {n_before}")
    print(f"filas despues del dedupe: {n_after}")
    print(f"duplicados eliminados   : {removed}")
    print()
    for lang in LANG_FILES:
        print(f"filas en {lang}: {len(by_lang.get(lang, []))}")
    print()
    print("distribucion de categorias por idioma (filas con la etiqueta a 1):")
    header = f"{'categoria':<35}" + "".join(f"{lang:>8}" for lang in LANG_FILES)
    print(header)
    for name, col in CATEGORY_COLUMN.items():
        counts = [sum(r[col] for r in by_lang.get(lang, [])) for lang in LANG_FILES]
        print(f"{name:<35}" + "".join(f"{c:>8}" for c in counts))

    for lang, path in written.items():
        print(f"\nescrito ({lang}): {path}")


if __name__ == "__main__":
    main()
