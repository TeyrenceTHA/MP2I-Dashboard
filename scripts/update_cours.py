import os
import json
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://maths-cpge.fr"

COURSES_URL = f"{BASE_URL}/chapitres/"
LOGIN_URL = f"{BASE_URL}/wp-login.php"

OUTPUT_DIR = "programmes/cours"
OUTPUT_JSON = os.path.join(
    OUTPUT_DIR,
    "cours.json"
)


# ============================================================
# IDENTIFIANTS
# ============================================================

# Étape 1 :
CHAPTER_PASSWORD = os.environ.get(
    "MATHS_CPGE_PASSWORD"
)

PDF_USERNAME = os.environ.get(
    "MATHS_CPGE_ID"
)

PDF_PASSWORD = os.environ.get(
    "MATHS_CPGE_PASSWORD"
)


if not CHAPTER_PASSWORD:
    raise RuntimeError(
        "MATHS_CPGE_PASSWORD est manquant."
    )

if not PDF_USERNAME:
    raise RuntimeError(
        "MATHS_CPGE_ID est manquant."
    )

if not PDF_PASSWORD:
    raise RuntimeError(
        "MATHS_CPGE_PASSWORD_PDF est manquant."
    )


os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# USER-AGENT
# ============================================================

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/140.0 Safari/537.36"
)


# ============================================================
# ÉTAPE 1
# ACCÈS À /CHAPITRES/
# ============================================================

print()
print("=" * 60)
print("ÉTAPE 1 : accès aux chapitres")
print("=" * 60)

chapter_session = requests.Session()

chapter_session.headers.update({
    "User-Agent": USER_AGENT
})


print(
    "Accès à la page des chapitres..."
)

response = chapter_session.get(
    COURSES_URL,
    timeout=30
)

response.raise_for_status()

print(
    "HTTP :",
    response.status_code
)

print(
    "URL :",
    response.url
)


# ============================================================
# VÉRIFIER LE FORMULAIRE DE MOT DE PASSE
# ============================================================

soup = BeautifulSoup(
    response.text,
    "html.parser"
)

password_input = soup.find(
    "input",
    {
        "name": "post_password"
    }
)


if password_input:

    print(
        "Page protégée par mot de passe."
    )

    form = password_input.find_parent(
        "form"
    )

    if not form:
        raise RuntimeError(
            "Formulaire de mot de passe introuvable."
        )

    action = form.get("action")

    if not action:
        action = COURSES_URL

    password_url = urljoin(
        COURSES_URL,
        action
    )

    password_data = {}

    # Récupérer les champs éventuels
    for input_tag in form.find_all(
        "input"
    ):

        name = input_tag.get("name")

        if not name:
            continue

        input_type = (
            input_tag.get("type")
            or "text"
        ).lower()

        if input_type in (
            "submit",
            "button"
        ):
            continue

        password_data[name] = (
            input_tag.get("value")
            or ""
        )

    password_data[
        "post_password"
    ] = CHAPTER_PASSWORD

    print(
        "Envoi du mot de passe..."
    )

    password_response = chapter_session.post(
        password_url,
        data=password_data,
        timeout=30,
        allow_redirects=True
    )

    password_response.raise_for_status()

    print(
        "Réponse :",
        password_response.status_code
    )

    print(
        "URL après mot de passe :",
        password_response.url
    )

else:

    print(
        "Aucun formulaire de mot de passe."
    )

    print(
        "Accès déjà autorisé."
    )


# ============================================================
# VÉRIFICATION DE L'ACCÈS
# ============================================================

print(
    "Vérification de l'accès..."
)

chapters_response = chapter_session.get(
    COURSES_URL,
    timeout=30
)

chapters_response.raise_for_status()

chapters_soup = BeautifulSoup(
    chapters_response.text,
    "html.parser"
)

still_protected = chapters_soup.find(
    "input",
    {
        "name": "post_password"
    }
)

if still_protected:

    raise RuntimeError(
        "Le mot de passe des chapitres "
        "n'a pas été accepté."
    )


print(
    "Accès aux chapitres confirmé."
)

print(
    "Taille HTML :",
    len(chapters_response.text)
)


# ============================================================
# ÉTAPE 2
# AUTHENTIFICATION POUR LES PDF
# ============================================================

print()
print("=" * 60)
print("ÉTAPE 2 : authentification PDF")
print("=" * 60)


pdf_session = requests.Session()

pdf_session.headers.update({
    "User-Agent": USER_AGENT
})


print(
    "Accès à la page de connexion..."
)

pdf_login_page = pdf_session.get(
    LOGIN_URL,
    timeout=30
)

pdf_login_page.raise_for_status()


# ============================================================
# RÉCUPÉRER LE FORMULAIRE WORDPRESS
# ============================================================

pdf_login_soup = BeautifulSoup(
    pdf_login_page.text,
    "html.parser"
)

login_form = pdf_login_soup.find(
    "form",
    id="loginform"
)


if not login_form:

    raise RuntimeError(
        "Formulaire WordPress "
        "#loginform introuvable."
    )


pdf_login_data = {}


for input_tag in login_form.find_all(
    "input"
):

    name = input_tag.get("name")

    if not name:
        continue

    input_type = (
        input_tag.get("type")
        or "text"
    ).lower()

    if input_type == "submit":

        if name == "wp-submit":

            pdf_login_data[name] = (
                input_tag.get("value")
                or "Se connecter"
            )

        continue

    if name == "log":
        continue

    if name == "pwd":
        continue

    pdf_login_data[name] = (
        input_tag.get("value")
        or ""
    )


# ============================================================
# IDENTIFIANTS
# ============================================================

pdf_login_data["log"] = PDF_USERNAME
pdf_login_data["pwd"] = PDF_PASSWORD

pdf_login_data.setdefault(
    "rememberme",
    ""
)

pdf_login_data.setdefault(
    "redirect_to",
    COURSES_URL
)

pdf_login_data.setdefault(
    "testcookie",
    "1"
)


# ============================================================
# COOKIE WORDPRESS
# ============================================================

pdf_session.cookies.set(
    "wordpress_test_cookie",
    "WP%20Cookie%20check",
    domain="maths-cpge.fr"
)


# ============================================================
# CONNEXION
# ============================================================

print(
    "Connexion avec ID + mot de passe..."
)

pdf_login_response = pdf_session.post(
    LOGIN_URL,
    data=pdf_login_data,
    timeout=30,
    allow_redirects=True
)


print(
    "HTTP :",
    pdf_login_response.status_code
)

print(
    "URL après connexion :",
    pdf_login_response.url
)


# ============================================================
# VÉRIFICATION
# ============================================================

if "/wp-login.php" in pdf_login_response.url:

    error_soup = BeautifulSoup(
        pdf_login_response.text,
        "html.parser"
    )

    errors = []

    for selector in (
        "#login_error",
        ".message",
        ".notice-error"
    ):

        for element in error_soup.select(
            selector
        ):

            message = element.get_text(
                " ",
                strip=True
            )

            if message:
                errors.append(message)

    if errors:

        print()
        print(
            "Erreur(s) de connexion :"
        )

        for error in errors:
            print(
                " -",
                error
            )

    raise RuntimeError(
        "Authentification PDF échouée."
    )


print(
    "Authentification PDF réussie."
)


# ============================================================
# DÉTECTION DU CHAPITRE
# ============================================================

def detect_chapter(text):

    match = re.search(
        r"\bch[-_]?(\d+)\b",
        text.lower()
    )

    if not match:
        return None

    number = int(
        match.group(1)
    )

    return (
        "ch"
        + str(number).zfill(2)
    )


# ============================================================
# DÉTECTION DU TYPE
# ============================================================

def detect_type(text):

    text = text.lower()

    # Correction TD
    if (
        "td-correction" in text
        or "td_correction" in text
        or "correction-td" in text
        or "correction_td" in text
    ):
        return "correction"

    # TD
    if re.search(
        r"(^|[-_])td($|[-_.])",
        text
    ):
        return "td"

    # Cours
    if "cours" in text:
        return "cours"

    return None


# ============================================================
# RÉCUPÉRATION DES PDF
# ============================================================

programmes = []

print()
print("=" * 60)
print("RECHERCHE DES PDF")
print("=" * 60)


for link in chapters_soup.find_all("a"):

    href = link.get("href")

    if not href:
        continue

    text = link.get_text(
        " ",
        strip=True
    )

    combined = (
        text
        + " "
        + href
    )


    # Seulement les PDF
    if ".pdf" not in combined.lower():
        continue


    # Chapitre
    chapter = detect_chapter(
        combined
    )

    if not chapter:
        continue


    # Type
    document_type = detect_type(
        combined
    )

    if not document_type:
        continue


    # URL complète
    pdf_url = urljoin(
        COURSES_URL,
        href
    )


    # Nom du fichier
    parsed_url = urlparse(
        pdf_url
    )

    filename = os.path.basename(
        parsed_url.path
    )

    if not filename:
        continue


    output_path = os.path.join(
        OUTPUT_DIR,
        filename
    )


    print()
    print(
        f"[{chapter}] {document_type}"
    )

    print(
        "URL :",
        pdf_url
    )

    print(
        "Fichier :",
        filename
    )


    # ========================================================
    # TÉLÉCHARGEMENT
    # ========================================================

    try:

        pdf_response = pdf_session.get(
            pdf_url,
            timeout=60,
            allow_redirects=True
        )


        print(
            "HTTP PDF :",
            pdf_response.status_code
        )


        pdf_response.raise_for_status()


        # Vérifier que c'est bien un PDF
        if not pdf_response.content.startswith(
            b"%PDF"
        ):

            print(
                "  -> réponse non-PDF, ignorée"
            )

            content_type = (
                pdf_response.headers
                .get(
                    "Content-Type",
                    ""
                )
            )

            print(
                "  -> Content-Type :",
                content_type
            )

            continue


        # Écrire le fichier
        with open(
            output_path,
            "wb"
        ) as file:

            file.write(
                pdf_response.content
            )


        programmes.append({
            "chapitre": chapter,
            "type": document_type,
            "url": filename
        })


        print(
            "  -> téléchargé"
        )


    except Exception as error:

        print(
            "  -> erreur :",
            error
        )


# ============================================================
# SUPPRIMER LES DOUBLONS
# ============================================================

unique = {}

for item in programmes:

    key = (
        item["chapitre"],
        item["type"]
    )

    unique[key] = item


programmes = list(
    unique.values()
)


# ============================================================
# TRI
# ============================================================

def chapter_number(item):

    match = re.search(
        r"\d+",
        item["chapitre"]
    )

    if match:
        return int(
            match.group()
        )

    return 9999


type_order = {
    "cours": 0,
    "td": 1,
    "correction": 2
}


programmes.sort(
    key=lambda item: (
        chapter_number(item),
        type_order.get(
            item["type"],
            99
        )
    )
)


# ============================================================
# CRÉER cours.json
# ============================================================

data = {
    "programmes": programmes
}


with open(
    OUTPUT_JSON,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        data,
        file,
        ensure_ascii=False,
        indent=2
    )


# ============================================================
# RÉSUMÉ
# ============================================================

print()
print("=" * 60)

print(
    f"{len(programmes)} document(s) "
    f"enregistré(s)"
)

print(
    f"Fichier : {OUTPUT_JSON}"
)


chapters = sorted(
    set(
        item["chapitre"]
        for item in programmes
    ),
    key=lambda chapter:
        int(
            re.search(
                r"\d+",
                chapter
            ).group()
        )
)


print(
    f"{len(chapters)} chapitre(s) détecté(s)"
)

print()


for chapter in chapters:

    documents = [
        item["type"]
        for item in programmes
        if item["chapitre"] == chapter
    ]

    print(
        chapter
        + " : "
        + ", ".join(documents)
    )


print("=" * 60)