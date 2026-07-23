"""
01_inspect_opp115.py — Mira que trajo el zip de OPP-115.

Solo LEE e imprime. No escribe ni modifica nada.

Uso:
    uv run python scripts/01_inspect_opp115.py
    uv run python scripts/01_inspect_opp115.py --root data/dataset/OPP-115
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

SEP = "-" * 72


def print_tree(root: Path, max_depth: int = 2) -> None:
    """Imprime que carpetas hay y cuantos archivos tiene cada una."""
    print(f"\n{SEP}\nESTRUCTURA DE {root}\n{SEP}")
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if len(rel.parts) - 1 > max_depth:
            continue
        if path.is_dir():
            n = sum(1 for _ in path.glob("*"))
            exts = Counter(p.suffix for p in path.glob("*") if p.is_file())
            ext_str = ", ".join(f"{c}x{e or 'sin ext'}" for e, c in exts.most_common(4))
            print(f"{'  ' * (len(rel.parts) - 1)}[dir] {rel}/  ({n} elementos: {ext_str})")


def inspect_csv(path: Path) -> None:
    """Muestra un CSV de anotaciones: lineas crudas y campos numerados."""
    print(f"\n{SEP}\nMUESTRA DE {path.name}\n{SEP}")
    with path.open(encoding="utf-8", errors="replace", newline="") as fh:
        rows = list(csv.reader(fh))
    if not rows:
        print("  (vacio)")
        return
    print(f"  filas: {len(rows)}   columnas: {len(rows[0])}")
    print("\n  primera fila, campo por campo:")
    for i, cell in enumerate(rows[0]):
        print(f"    [{i}] {cell[:90]}")


def find_categories(annotations_dir: Path) -> None:
    """Cuenta que textos aparecen en las anotaciones: ahi estan las categorias."""
    print(f"\n{SEP}\nCATEGORIAS ENCONTRADAS\n{SEP}")
    counter: Counter[str] = Counter()
    files = sorted(annotations_dir.glob("*.csv"))
    for path in files:
        with path.open(encoding="utf-8", errors="replace", newline="") as fh:
            for row in csv.reader(fh):
                for cell in row:
                    cell = cell.strip()
                    if (
                        3 < len(cell) < 60
                        and not cell.startswith(("{", "http", "www"))
                        and any(c.isupper() for c in cell)
                        and not cell.isdigit()
                    ):
                        counter[cell] += 1
    print(f"  archivos de anotacion: {len(files)}")
    print("\n  candidatos a 'categoria' (25 mas frecuentes):")
    for value, n in counter.most_common(25):
        print(f"    {n:>7}  {value}")
    print("\n  >>> Busca las 10 categorias y anota como se escriben EXACTAMENTE.")


def inspect_policy_text(policies_dir: Path) -> None:
    """Comprueba como estan separados los fragmentos dentro de una politica."""
    print(f"\n{SEP}\nTEXTO DE LAS POLITICAS\n{SEP}")
    files = sorted(p for p in policies_dir.glob("*") if p.is_file())
    print(f"  archivos: {len(files)}")
    if not files:
        return
    text = files[0].read_text(encoding="utf-8", errors="replace")
    print(f"  ejemplo: {files[0].name}  ({len(text)} caracteres)")
    for sep in ("|||", "\n\n", "<br>"):
        n = text.count(sep)
        print(f"    separador {sep!r}: {n} veces -> {n + 1} fragmentos")
    print("\n  primeros 300 caracteres:")
    print("   ", text[:300].replace("\n", " / "))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="data/dataset",
                        help="carpeta donde se descomprimio OPP-115")
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        raise SystemExit(f"No existe {root}. Pasa la ruta con --root")

    print_tree(root)

    ann_dirs = [d for d in root.rglob("*") if d.is_dir() and "annotation" in d.name.lower()]
    pol_dirs = [d for d in root.rglob("*") if d.is_dir()
                and any(k in d.name.lower() for k in ("polic", "sanitiz", "document"))]

    print(f"\n{SEP}\nCARPETAS DETECTADAS\n{SEP}")
    print("  anotaciones:", [str(d.relative_to(root)) for d in ann_dirs] or "NO ENCONTRADA")
    print("  politicas:  ", [str(d.relative_to(root)) for d in pol_dirs] or "NO ENCONTRADA")

    if ann_dirs:
        csvs = sorted(ann_dirs[0].glob("*.csv"))
        if csvs:
            inspect_csv(csvs[0])
        find_categories(ann_dirs[0])
    if pol_dirs:
        inspect_policy_text(pol_dirs[0])


if __name__ == "__main__":
    main()