from pathlib import Path
import json
import html

DOSSIER_CONTENT = Path("content")

DOSSIERS_PUBLICS = [
    "cours",
    "exercices",
    "devoirs",
    "activites"
]

FICHIER_SORTIE = Path("activites.html")


def informations_notebook(fichier):
    with open(fichier, encoding="utf-8") as f:
        notebook = json.load(f)

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
                description = reste.split("\n\n")[0].strip()

            break

    return titre, description


def nom_affiche(nom):
    return nom.replace("_", " ").replace("-", " ").title()


cartes = []

for categorie in DOSSIERS_PUBLICS:

    dossier_categorie = DOSSIER_CONTENT / categorie

    if not dossier_categorie.exists():
        continue

    for fichier in sorted(dossier_categorie.rglob("*.ipynb")):

        titre, description = informations_notebook(fichier)

        chemin_relatif = fichier.relative_to(DOSSIER_CONTENT)
        parties = chemin_relatif.parts

        categorie_affichee = nom_affiche(parties[0])

        if len(parties) >= 3:
            niveau = nom_affiche(parties[1])
        else:
            niveau = ""

        chemin_jupyter = "/".join(parties)

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

        chemin_js = html.escape(
            chemin_jupyter,
            quote=True
        )

        titre_js = html.escape(
            titre,
            quote=True
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

                <button
                    type="button"
                    onclick="ouvrirActivite('{chemin_js}', '{titre_js}')"
                >
                    Ouvrir
                </button>

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


    <div
        id="modal"
        class="modal"
        onclick="fermerSiFond(event)"
    >

        <div class="modal-contenu">

            <button
                type="button"
                class="fermer"
                onclick="fermerActivite()"
                title="Fermer"
            >
                ×
            </button>

            <iframe
                id="iframe-jupyter"
                title="Activité Jupyter"
                width="100%"
                height="850"
                style="border: 1px solid #ddd;"
                allow="cross-origin-isolated">
            </iframe>

        </div>

    </div>


    <script>

        function ouvrirActivite(path, titre) {{

            const iframe =
                document.getElementById("iframe-jupyter");

            iframe.src =
                "https://pierremaujonnet.github.io/jupyterlite_pmauj/notebooks/index.html?path="
                + encodeURIComponent(path);

            iframe.title = titre;

            document
                .getElementById("modal")
                .style.display = "flex";

            document.body.style.overflow = "hidden";
        }}


        function fermerActivite() {{

            document
                .getElementById("modal")
                .style.display = "none";

            document
                .getElementById("iframe-jupyter")
                .src = "";

            document.body.style.overflow = "";
        }}


        function fermerSiFond(event) {{

            if (event.target.id === "modal") {{
                fermerActivite();
            }}
        }}


        document.addEventListener(
            "keydown",
            function(event) {{

                if (event.key === "Escape") {{
                    fermerActivite();
                }}
            }}
        );

    </script>

</body>

</html>
"""


FICHIER_SORTIE.write_text(
    page,
    encoding="utf-8"
)

print(
    f"{len(cartes)} notebook(s) publié(s) dans "
    f"{FICHIER_SORTIE}"
)