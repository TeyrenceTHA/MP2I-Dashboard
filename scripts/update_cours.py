import os
import json
import re
import base64
import html
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = "https://maths-cpge.fr"
LOGIN_URL = f"{BASE_URL}/wp-login.php"
COURSES_URL = f"{BASE_URL}/chapitres/"

OUTPUT_DIR = "programmes/cours"
OUTPUT_JSON = os.path.join(OUTPUT_DIR, "cours.json")


USERNAME = os.environ.get("MATHS_CPGE_ID")
PASSWORD = os.environ.get("MATHS_CPGE_PASSWORD")


if not USERNAME or not PASSWORD:
    raise RuntimeError(
        "MATHS_CPGE_ID ou MATHS_CPGE_PASSWORD est manquant."
    )


os.makedirs(OUTPUT_DIR, exist_ok=True)


session = requests.Session()

session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0 Safari/537.36"
    )
})


# ============================================================
# 1. RÉCUPÉRER LA PAGE DE CONNEXION
# ============================================================

print("Récupération de la page de connexion...")

login_page = session.get(
    LOGIN_URL,
    timeout=30
)

login_page.raise_for_status()


soup = BeautifulSoup(
    login_page.text,
    "html.parser"
)


# ============================================================
# 2. RÉCUPÉRER LES CHAMPS DU FORMULAIRE
# ============================================================

form = soup.find(
    "form",
    id="loginform"
)


if not form:
    raise RuntimeError(
        "Formulaire WordPress #loginform introuvable."
    )


login_data = {}


for input_tag in form.find_all("input"):

    name = input_tag.get("name")

    if not name:
        continue

    input_type = (
        input_tag.get("type") or "text"
    ).lower()

    # Les champs utilisateur/mot de passe seront ajoutés
    # explicitement plus bas.
    if name in ("log", "pwd"):
        continue

    # Bouton submit
    if input_type == "submit":

        if name == "wp-submit":

            login_data[name] = (
                input_tag.get("value")
                or "Se connecter"
            )

        continue

    login_data[name] = (
        input_tag.get("value") or ""
    )


# Valeurs principales
login_data["log"] = USERNAME
login_data["pwd"] = PASSWORD


# ============================================================
# 3. RÉCUPÉRER LE CHAMP WP ARMOUR / HONEYPOT
# ============================================================

print("Recherche du champ anti-spam WP Armour...")


wpa_field_name = None
wpa_field_value = None


# On cherche :
#
# wpa_field_info = JSON.parse(atob("...."));
#

pattern = re.compile(
    r'wpa_field_info\s*=\s*JSON\.parse'
    r'\(\s*atob\(["\']([^"\']+)["\']\)',
    re.IGNORECASE
)


match = pattern.search(
    login_page.text
)


if match:

    encoded = match.group(1)

    try:

        decoded = base64.b64decode(
            encoded
        ).decode("utf-8")

        wpa_data = json.loads(
            decoded
        )

        wpa_field_name = (
            wpa_data.get("wpa_field_name")
        )

        wpa_field_value = (
            wpa_data.get("wpa_field_value")
        )

        print(
            "Champ WP Armour détecté :",
            wpa_field_name
        )

    except Exception as error:

        raise RuntimeError(
            "Impossible de décoder les données WP Armour : "
            + str(error)
        )

else:

    print(
        "Aucun champ WP Armour détecté."
    )


if wpa_field_name:

    login_data[wpa_field_name] = str(
        wpa_field_value
    )


# ============================================================
# 4. PARAMÈTRES WORDPRESS
# ============================================================

login_data.setdefault(
    "rememberme",
    ""
)

login_data.setdefault(
    "redirect_to",
    COURSES_URL
)

login_data.setdefault(
    "testcookie",
    "1"
)

login_data.setdefault(
    "wpa_initiator",
    ""
)


print("Connexion au site...")


# Le cookie testcookie de WordPress
# est parfois nécessaire.
session.cookies.set(
    "wordpress_test_cookie",
    "WP%20Cookie%20check",
    domain="maths-cpge.fr"
)


# ============================================================
# 5. CONNEXION
# ============================================================

login_response = session.post(
    LOGIN_URL,
    data=login_data,
    timeout=30,
    allow_redirects=True
)


print(
    "Login HTTP :",
    login_response.status_code
)

print(
    "URL après connexion :",
    login_response.url
)


# ============================================================
# 6. VÉRIFICATION DE LA CONNEXION
# ============================================================

if "/wp-login.php" in login_response.url:

    login_soup = BeautifulSoup(
        login_response.text,
        "html.parser"
    )

    error_messages = []

    for selector in (
        ".message",
        "#login_error",
        ".notice-error"
    ):

        for element in login_soup.select(
            selector
        ):

            text = element.get_text(
                " ",
                strip=True
            )

            if text:
                error_messages.append(text)


    if error_messages:

        print()
        print(
            "Erreur de connexion :"
        )

        for message in error_messages:

            print(
                " -",
                message
            )

    raise RuntimeError(
        "Authentification WordPress échouée."
    )


print("Connexion réussie.")


# ============================================================
# 7. RÉCUPÉRER LA PAGE DES CHAPITRES
# ============================================================

print()
print("Récupération des chapitres...")


chapters_response = session.get(
    COURSES_URL,
    timeout=30
)

chapters_response.raise_for_status()


print(
    "Page HTTP :",
    chapters_response.status_code
)

print(
    "URL finale :",
    chapters_response.url
)

print(
    "Taille HTML :",
    len(chapters_response.text)
)


soup = BeautifulSoup(
    chapters_response.text,
    "html.parser"
)


# ============================================================
# 8. DÉTECTION DES DOCUMENTS
# ============================================================

def detect_chapter(text):

    match = re.search(
        r"\bch[-_]?(\d+)\b",
        text.lower()
    )

    if not match:
        return None

    return (
        "ch" +
        str(
            int(match.group(1))
        ).zfill(2)
    )


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


programmes = []


# ============================================================
# 9. CHERCHER LES LIENS PDF
# ============================================================

for link in soup.find_all("a"):

    href = link.get("href")

    if not href:
        continue


    text = link.get_text(
        " ",
        strip=True
    )


    combined = (
        text +
        " " +
        href
    ).lower()


    if ".pdf" not in combined:
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
        BASE_URL,
        href
    )


    filename = os.path.basename(
        pdf_url.split("?")[0]
    )


    output_path = os.path.join(
        OUTPUT_DIR,
        filename
    )


    print(
        f"[{chapter}] "
        f"{document_type} -> "
        f"{filename}"
    )


    try:

        pdf_response = session.get(
            pdf_url,
            timeout=60
        )

        pdf_response.raise_for_status()


        # Vérification basique :
        # un vrai PDF commence normalement par %PDF
        if not pdf_response.content.startswith(
            b"%PDF"
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
# 10. SUPPRIMER LES DOUBLONS
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
# 11. TRI
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
# 12. ÉCRIRE cours.json
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


print()
print(
    f"{len(programmes)} documents "
    f"enregistrés dans "
    f"{OUTPUT_JSON}"
)


# ============================================================
# 13. RÉCAPITULATIF
# ============================================================

chapters = sorted(
    set(
        item["chapitre"]
        for item in programmes
    ),
    key=lambda chapter: int(
        re.search(
            r"\d+",
            chapter
        ).group()
    )
)


print(
    f"{len(chapters)} chapitre(s) détecté(s)."
)

for chapter in chapters:

    documents = [
        item["type"]
        for item in programmes
        if item["chapitre"] == chapter
    ]

    print(
        chapter + " : " +
        ", ".join(documents)
    )