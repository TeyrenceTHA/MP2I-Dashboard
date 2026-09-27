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

OUTPUT_DIR = "programmes/cours"
OUTPUT_JSON = os.path.join(
    OUTPUT_DIR,
    "cours.json"
)

PASSWORD = os.environ.get(
    "MATHS_CPGE_PASSWORD"
)


if not PASSWORD:
    raise RuntimeError(
        "MATHS_CPGE_PASSWORD est manquant."
    )


os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# SESSION
# ============================================================

session = requests.Session()

session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0 Safari/537.36"
    )
})


# ============================================================
# 1. ACCÉDER À LA PAGE
# ============================================================

print("Accès à la page des chapitres...")

response = session.get(
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
# 2. VÉRIFIER SI LA PAGE EST PROTÉGÉE
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


# ============================================================
# 3. ENVOYER LE MOT DE PASSE
# ============================================================

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

    password_data = {
        "post_password": PASSWORD
    }

    # Récupérer les autres champs éventuels
    for input_tag in form.find_all("input"):

        name = input_tag.get("name")

        if not name:
            continue

        if name == "post_password":
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
    ] = PASSWORD

    print(
        "Envoi du mot de passe..."
    )

    password_response = session.post(
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
# 4. VÉRIFIER QUE L'ACCÈS EST BIEN DÉVERROUILLÉ
# ============================================================

print(
    "Vérification de l'accès..."
)

chapters_response = session.get(
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
        "Le mot de passe n'a pas été accepté."
    )


print(
    "Accès aux chapitres confirmé."
)

print(
    "Taille HTML :",
    len(chapters_response.text)
)


# ============================================================
# 5. DÉTECTION DU CHAPITRE
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
# 6. DÉTECTION DU TYPE
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
# 7. RÉCUPÉRATION DES PDF
# ============================================================

programmes = []

print()
print("Recherche des PDF...")


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

    chapter = detect_chapter(
        combined
    )

    if not chapter:
        continue

    document_type = detect_type(
        combined
    )

    if not document_type:
        continue

    pdf_url = urljoin(
        COURSES_URL,
        href
    )

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
        f"[{chapter}] "
        f"{document_type}"
    )

    print(
        "URL :",
        pdf_url
    )

    print(
        "Fichier :",
        filename
    )

    try:

        pdf_response = session.get(
            pdf_url,
            timeout=60
        )

        pdf_response.raise_for_status()

        content_type = (
            pdf_response.headers
            .get(
                "Content-Type",
                ""
            )
            .lower()
        )

        # Vérification PDF
        if not (
            pdf_response.content
            .startswith(b"%PDF")
        ):

            print(
                "  -> réponse non-PDF, ignorée"
            )

            continue

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
# 8. SUPPRIMER LES DOUBLONS
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
# 9. TRI DES CHAPITRES
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
# 10. CRÉER cours.json
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
# 11. RÉSUMÉ
# ============================================================

print()
print("=" * 50)

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

print("=" * 50)