#!/usr/bin/env python3
"""Ajoute un style CSS aux cellules Markdown contenant une solution.

Le script parcourt récursivement tous les fichiers ``.ipynb`` situés dans le
dossier où il est placé et dans ses sous-dossiers. Une cellule est considérée
comme une cellule de solution lorsqu'elle contient une balise ``<summary>``
dont le texte comporte le mot « solution ».

Exemple :
    python inserer_style_solutions.py

Un autre dossier peut néanmoins être indiqué explicitement :
    python inserer_style_solutions.py chemin/vers/exercices
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path


STYLE = """<style>
    summary {
        color: purple;
        cursor: pointer;
        font-weight: bold;
    }
</style>"""

SOLUTION_RE = re.compile(
    r"<summary\b[^>]*>.*?solution.*?</summary>",
    flags=re.IGNORECASE | re.DOTALL,
)

# Reconnaît un bloc <style> qui ne contient que la mise en forme de summary.
SUMMARY_STYLE_RE = re.compile(
    r"<style>\s*summary\s*\{(?=[^}]*\bcolor\s*:\s*purple\s*;)"
    r"(?=[^}]*\bcursor\s*:\s*pointer\s*;)"
    r"(?=[^}]*\bfont-weight\s*:\s*bold\s*;)[^}]*\}\s*</style>\s*",
    flags=re.IGNORECASE | re.DOTALL,
)


def lire_source(cellule: dict) -> str:
    """Renvoie le contenu d'une cellule, quel que soit son format JSON."""
    source = cellule.get("source", "")
    return "".join(source) if isinstance(source, list) else source


def ecrire_source(cellule: dict, texte: str) -> None:
    """Conserve le format initial de la propriété source."""
    if isinstance(cellule.get("source"), list):
        cellule["source"] = texte.splitlines(keepends=True)
    else:
        cellule["source"] = texte


def traiter_notebook(chemin: Path, sauvegarde: bool) -> int:
    """Modifie un notebook et renvoie le nombre de cellules changées."""
    try:
        notebook = json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as erreur:
        print(f"ERREUR  {chemin} : {erreur}")
        return 0

    modifications = 0

    for cellule in notebook.get("cells", []):
        if cellule.get("cell_type") != "markdown":
            continue

        source = lire_source(cellule)
        if not SOLUTION_RE.search(source):
            continue

        # Supprime les éventuelles copies de ce même style avant d'en ajouter
        # exactement une. Le script peut ainsi être relancé sans créer de doublon.
        contenu = SUMMARY_STYLE_RE.sub("", source).lstrip("\r\n")
        nouveau_source = f"{STYLE}\n\n{contenu}"

        if nouveau_source != source:
            ecrire_source(cellule, nouveau_source)
            modifications += 1

    if modifications:
        if sauvegarde:
            copie = chemin.with_suffix(chemin.suffix + ".bak")
            if not copie.exists():
                shutil.copy2(chemin, copie)

        temporaire = chemin.with_suffix(chemin.suffix + ".tmp")
        temporaire.write_text(
            json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8",
        )
        temporaire.replace(chemin)

    return modifications


def main() -> int:
    # Évite un arrêt sous Windows lorsqu'un chemin contient un caractère Unicode
    # que l'encodage historique de la console ne sait pas afficher.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    analyseur = argparse.ArgumentParser(
        description=(
            "Insère le style CSS de <summary> dans chaque cellule Markdown "
            "contenant une solution déroulante."
        )
    )
    analyseur.add_argument(
        "dossier",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parent,
        help=(
            "dossier racine contenant les notebooks à modifier ; "
            "par défaut, dossier où se trouve ce programme"
        ),
    )
    analyseur.add_argument(
        "--backup",
        action="store_true",
        help="crée une copie .ipynb.bak avant chaque modification",
    )
    arguments = analyseur.parse_args()

    dossier = arguments.dossier.expanduser().resolve()
    if not dossier.is_dir():
        analyseur.error(f"le dossier n'existe pas : {dossier}")

    notebooks = sorted(dossier.rglob("*.ipynb"))
    total_cellules = 0
    total_fichiers = 0

    for notebook in notebooks:
        nombre = traiter_notebook(notebook, arguments.backup)
        if nombre:
            total_fichiers += 1
            total_cellules += nombre
            print(f"MODIFIÉ {notebook} ({nombre} cellule(s))")
        else:
            print(f"INCHANGÉ {notebook}")

    print(
        f"\nTerminé : {total_cellules} cellule(s) modifiée(s) "
        f"dans {total_fichiers} fichier(s), sur {len(notebooks)} notebook(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
