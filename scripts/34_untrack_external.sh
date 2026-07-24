#!/usr/bin/env bash
# EJECUTAR SOLO TRAS ACUERDO EN LA DAILY — el MAPP entró sin decisión de spec; al
# mergear esto, desaparece de la carpeta de quien haga pull
#
# Deja de rastrear (git rm --cached) data/dataset_extension/external_datasets/
# (MAPP_Corpus + JURIX extraidos: MAPP incluye aleman, fuera de alcance por
# 2_spec.md §11, y ninguno de los dos pasa por la norma de datos generados del
# §12) y la basura de macOS versionada por error (.DS_Store, __MACOSX/, ._*).
# Los archivos siguen en disco de quien lo ejecute: solo salen del indice de
# git, ya cubiertos por las reglas anadidas a .gitignore.

set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

git rm -r --cached --ignore-unmatch -- data/dataset_extension/external_datasets/
git rm -r --cached --ignore-unmatch -- '**/.DS_Store'
git rm -r --cached --ignore-unmatch -- '**/__MACOSX'
git rm -r --cached --ignore-unmatch -- '**/._*'

echo "Listo. Revisa 'git status' y comitea: chore: untrack MAPP_Corpus y basura de macOS (#33)"
