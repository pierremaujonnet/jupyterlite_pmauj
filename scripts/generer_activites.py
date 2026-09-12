from pathlib import Path
import json
import html

# ============================================================
# À MODIFIER UNIQUEMENT ICI
# ============================================================

DOSSIERS_PUBLICS = [
    "cours",
    "exercices",
    "devoirs",
    "activites"
]

# ============================================================
# NE PLUS TOUCHER AU RESTE
# ============================================================

DOSSIER_CONTENT = Path("content")
FICHIER_SORTIE = Path("activites.html")

URL_JUPYTERLITE = (
    "https://pierremaujonnet.github.io/"
    "jupyterlite_pmauj/notebooks/index.html?path="
)


def nom_affiche(nom):
    """
    Transforme un nom de dossier en texte lisible.
    """
    return (
        nom
        .replace("_", " ")
        .replace("-", " ")
        .strip()
        .title()
    )


def informations_notebook(fichier):
    """
    Cherche le titre et la description dans la première
    cellule Markdown commençant par '# '.
    """

    with open(fichier, encoding="utf-8") as f:
        notebook = json.load(f)

    titre = nom_affiche(fichier.stem)
    description = ""

    for cellule in notebook.get("cells", []):

        if cellule.get("cell_type") != "markdown":
            continue

        texte = "".join(
            cellule.get("source", [])
        ).strip()

        if not texte:
            continue

        lignes = texte.splitlines()

        if lignes[0].startswith("# "):

            titre = lignes[0][2:].strip()

            reste = "\n".join(
                lignes[1:]
            ).strip()

            if reste:
                description = (
                    reste
                    .split("\n\n")[0]
                    .strip()
                )

            break

    return titre, description


def identifiant_dossier(dossier):
    """
    Fabrique un identifiant HTML unique à partir
    du chemin relatif à content/.
    """

    relatif = dossier.relative_to(DOSSIER_CONTENT)

    return (
        "dossier-"
        + "-".join(relatif.parts)
        .replace("_", "-")
        .replace(" ", "-")
    )


def creer_menu_dossier(dossier):
    """
    Génère récursivement le menu HTML correspondant
    à un dossier et à ses sous-dossiers.
    """

    sous_dossiers = sorted(
        [
            element
            for element in dossier.iterdir()
            if element.is_dir()
        ],
        key=lambda p: p.name.lower()
    )

    notebooks = list(
        dossier.glob("*.ipynb")
    )

    contenu = []

    # Si le dossier contient directement des notebooks,
    # son nom devient cliquable.
    if notebooks:

        id_dossier = identifiant_dossier(dossier)

        contenu.append(
            f"""
            <button
                class="bouton-dossier"
                type="button"
                onclick="afficherDossier('{id_dossier}')"
            >
                {html.escape(nom_affiche(dossier.name))}
            </button>
            """
        )

    else:

        contenu.append(
            f"""
            <span class="nom-dossier">
                {html.escape(nom_affiche(dossier.name))}
            </span>
            """
        )

    # Sous-dossiers
    if sous_dossiers:

        contenu.append('<ul class="sous-menu">')

        for sous_dossier in sous_dossiers:

            contenu.append("<li>")

            contenu.append(
                creer_menu_dossier(sous_dossier)
            )

            contenu.append("</li>")

        contenu.append("</ul>")

    return "".join(contenu)


def creer_cartes_dossier(dossier):
    """
    Génère les cartes correspondant aux notebooks
    contenus directement dans un dossier.
    """

    cartes = []

    for fichier in sorted(
        dossier.glob("*.ipynb"),
        key=lambda p: p.name.lower()
    ):

        titre, description = informations_notebook(
            fichier
        )

        chemin_jupyter = "/".join(
            fichier
            .relative_to(DOSSIER_CONTENT)
            .parts
        )

        description_html = ""

        if description:

            description_html = (
                f"<p>{html.escape(description)}</p>"
            )

        cartes.append(
            f"""
            <article class="carte">

                <h2>
                    {html.escape(titre)}
                </h2>

                {description_html}

                <button
                    type="button"
                    onclick="ouvrirActivite(
                        {html.escape(json.dumps(chemin_jupyter), quote=True)},
                        {html.escape(json.dumps(titre), quote=True)}
                    )"
                >
                    Ouvrir
                </button>

            </article>
            """
        )

    return "".join(cartes)


# ============================================================
# CONSTRUCTION DU MENU
# ============================================================

menu_html = []

sections_html = []

premier_dossier = None


for nom_dossier_principal in DOSSIERS_PUBLICS:

    dossier_principal = (
        DOSSIER_CONTENT
        / nom_dossier_principal
    )

    if not dossier_principal.exists():
        continue

    menu_html.append(
        f"""
        <div class="menu-principal">

            <div class="titre-menu-principal">
                {html.escape(nom_affiche(nom_dossier_principal))}

                <ul>
        """
    )

    sous_dossiers = sorted(
        [
            element
            for element in dossier_principal.iterdir()
            if element.is_dir()
        ],
        key=lambda p: p.name.lower()
    )

    # Notebooks directement dans le dossier principal
    if list(dossier_principal.glob("*.ipynb")):

        id_dossier = identifiant_dossier(
            dossier_principal
        )

        menu_html.append(
            f"""
            <li>
                <button
                    class="bouton-dossier"
                    type="button"
                    onclick="afficherDossier('{id_dossier}')"
                >
                    {html.escape(nom_affiche(nom_dossier_principal))}
                </button>
            </li>
            """
        )

        if premier_dossier is None:
            premier_dossier = id_dossier

    for sous_dossier in sous_dossiers:

        menu_html.append("<li>")

        menu_html.append(
            creer_menu_dossier(sous_dossier)
        )

        menu_html.append("</li>")

    menu_html.append(
        """
                </ul>
            </div>
        </div>
        """
    )


# ============================================================
# CONSTRUCTION DE TOUTES LES SECTIONS DE CARTES
# ============================================================

for nom_dossier_principal in DOSSIERS_PUBLICS:

    dossier_principal = (
        DOSSIER_CONTENT
        / nom_dossier_principal
    )

    if not dossier_principal.exists():
        continue

    dossiers = [
        dossier_principal,
        *sorted(
            [
                d
                for d in dossier_principal.rglob("*")
                if d.is_dir()
            ],
            key=lambda p: str(p).lower()
        )
    ]

    for dossier in dossiers:

        notebooks = list(
            dossier.glob("*.ipynb")
        )

        if not notebooks:
            continue

        id_dossier = identifiant_dossier(
            dossier
        )

        if premier_dossier is None:
            premier_dossier = id_dossier

        chemin_affiche = " / ".join(
            nom_affiche(partie)
            for partie in
            dossier.relative_to(
                DOSSIER_CONTENT
            ).parts
        )

        sections_html.append(
            f"""
            <section
                id="{id_dossier}"
                class="section-cartes"
            >

                <h2 class="titre-section">
                    {html.escape(chemin_affiche)}
                </h2>

                <div class="grille">
                    {creer_cartes_dossier(dossier)}
                </div>

            </section>
            """
        )


# ============================================================
# PAGE HTML
# ============================================================

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

    <h1>
        Activités numériques
    </h1>


    <nav class="menu">

        {''.join(menu_html)}

    </nav>


    <main>

        {''.join(sections_html)}


        <div
            id="zone-jupyter"
            class="zone-jupyter"
        >

            <iframe
                id="iframe-jupyter"
                src=""
                title="Activité Jupyter"
                width="100%"
                height="850"
                style="border: 1px solid #ddd;"
                allow="cross-origin-isolated">
            </iframe>

        </div>

    </main>


    <script>

        const URL_JUPYTERLITE =
            "{URL_JUPYTERLITE}";


        let activiteCourante = "";


        function afficherDossier(id) {{

            document
                .querySelectorAll(".section-cartes")
                .forEach(section => {{
                    section.style.display = "none";
                }});

            const section =
                document.getElementById(id);

            if (section) {{

                section.style.display = "block";

            }}
        }}


        function ouvrirActivite(path, titre) {{

            const iframe =
                document.getElementById(
                    "iframe-jupyter"
                );

            const zone =
                document.getElementById(
                    "zone-jupyter"
                );

            if (path === activiteCourante) {{

                zone.scrollIntoView({{
                    behavior: "smooth",
                    block: "start"
                }});

                return;
            }}

            activiteCourante = path;

            iframe.src =
                URL_JUPYTERLITE
                + encodeURI(path);

            iframe.title = titre;

            zone.style.display = "block";

            zone.scrollIntoView({{
                behavior: "smooth",
                block: "start"
            }});
        }}


        function fermerActivite() {{

            const zone =
                document.getElementById(
                    "zone-jupyter"
                );

            const iframe =
                document.getElementById(
                    "iframe-jupyter"
                );

            zone.style.display = "none";

            iframe.src = "";
        }}


        document.addEventListener(
            "DOMContentLoaded",
            function() {{

                document
                    .querySelectorAll(
                        ".section-cartes"
                    )
                    .forEach(section => {{
                        section.style.display =
                            "none";
                    }});

                const premier =
                    "{premier_dossier or ''}";

                if (premier) {{
                    afficherDossier(
                        premier
                    );
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
    f"Page créée : {FICHIER_SORTIE}"
)
