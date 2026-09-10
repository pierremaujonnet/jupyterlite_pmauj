from pathlib import Path
import json
import html

# Dossier contenant les notebooks
DOSSIER_CONTENT = Path("content")

# Seuls ces sous-dossiers seront affichés sur la page des activités
DOSSIERS_PUBLICS = [
    "cours"
]



# Fichier HTML généré
FICHIER_SORTIE = Path("pages/activites.html")


def informations_notebook(fichier):
    """
    Récupère le titre et la description du notebook.

    Le titre est recherché dans la première cellule Markdown
    commençant par '# '.

    Le premier paragraphe situé après le titre est utilisé
    comme description.
    """

    with open(fichier, encoding="utf-8") as f:
        notebook = json.load(f)

    # Valeurs par défaut
    titre = fichier.stem.replace("_", " ").replace("-", " ").title()
    description = ""

    for cellule in notebook.get("cells", []):
        if cellule.get("cell_type") != "markdown":
            continue

        texte = "".join(cellule.get("source", [])).strip()

        if not texte:
            continue

        lignes = texte.splitlines()

        if lignes[0].startswith("# "):
            titre = lignes[0][2:].strip()

            reste = "\n".join(lignes[1:]).strip()

            if reste:
                # On ne conserve que le premier paragraphe
                description = reste.split("\n\n")[0].strip()

            break

    return titre, description


def nom_affiche(nom):
    """
    Transforme un nom de dossier en texte plus lisible.
    """
    return nom.replace("_", " ").replace("-", " ").title()


cartes = []


for categorie in DOSSIERS_PUBLICS:

    dossier_categorie = DOSSIER_CONTENT / categorie

    # Si le dossier n'existe pas, on passe simplement au suivant
    if not dossier_categorie.exists():
        continue

    for fichier in sorted(dossier_categorie.rglob("*.ipynb")):

        titre, description = informations_notebook(fichier)

        # Chemin du notebook relativement à content/
        chemin_relatif = fichier.relative_to(DOSSIER_CONTENT)

        parties = chemin_relatif.parts

        # Exemple :
        # content/exercices/premiere/suites.ipynb
        #
        # parties vaut :
        # ("exercices", "premiere", "suites.ipynb")

        categorie_affichee = nom_affiche(parties[0])

        if len(parties) >= 3:
            niveau = nom_affiche(parties[1])
        else:
            niveau = ""

        # Chemin utilisé par JupyterLite
        chemin_jupyter = "/".join(parties)

        lien = "../lab/index.html?path=" + chemin_jupyter

        niveau_html = ""

        if niveau:
            niveau_html = (
                f'<div class="niveau">{html.escape(niveau)}</div>'
            )

        description_html = ""

        if description:
            description_html = (
                f"<p>{html.escape(description)}</p>"
            )

        cartes.append(
            f"""
            <article class="carte">

                <div class="categorie">
                    {html.escape(categorie_affichee)}
                </div>

                {niveau_html}

                <h2>{html.escape(titre)}</h2>

                {description_html}

                <a href="{html.escape(lien)}" target="_blank">
                    Ouvrir
                </a>

            </article>
            """
        )


page = f"""<!DOCTYPE html>
<html lang="fr">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1"
    >

    <title>Activités numériques</title>

    <link
        rel="stylesheet"
        href="activites.css"
    >

</head>

<body>

    <h1>Activités numériques</h1>

    <div class="grille">

        {''.join(cartes)}

    </div>

</body>

</html>
"""


# Création du dossier pages/ s'il n'existe pas
FICHIER_SORTIE.parent.mkdir(
    parents=True,
    exist_ok=True
)

# Écriture du fichier HTML
FICHIER_SORTIE.write_text(
    page,
    encoding="utf-8"
)

print(
    f"{len(cartes)} notebook(s) publié(s) dans "
    f"{FICHIER_SORTIE}"
)