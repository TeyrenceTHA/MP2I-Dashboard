import os
import json
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = "https://maths-cpge.fr"
COURSES_URL = "https://maths-cpge.fr/chapitres/"

OUTPUT_DIR = "programmes/cours"
OUTPUT_JSON = os.path.join(OUTPUT_DIR, "cours.json")


USERNAME = os.environ.get("MATHS_CPGE_ID")
PASSWORD = os.environ.get("MATHS_CPGE_PASSWORD")


if not USERNAME or not PASSWORD:
    raise RuntimeError(
        "MATHS_CPGE_ID ou MATHS_CPGE_PASSWORD manquant."
    )


os.makedirs(OUTPUT_DIR, exist_ok=True)


session = requests.Session()


print("Connexion au site...")


login_data = {
    "log": USERNAME,
    "pwd": PASSWORD,
    "wp-submit": "Log In",
    "redirect_to": COURSES_URL,
    "testcookie": "1"
}


response = session.post(
    f"{BASE_URL}/wp-login.php",
    data=login_data,
    timeout=30
)


if response.status_code != 200:
    raise RuntimeError(
        f"Erreur de connexion : HTTP {response.status_code}"
    )


print("Récupération des chapitres...")


response = session.get(
    COURSES_URL,
    timeout=30
)

response.raise_for_status()


soup = BeautifulSoup(
    response.text,
    "html.parser"
)


programmes = []


def detect_document_type(text):
    """
    Détecte le type à partir de noms comme :

    ch04-cours
    ch04-td
    ch04-td-correction
    """

    text = text.lower().strip()

    if "td-correction" in text:
        return "correction"

    if "td_correction" in text:
        return "correction"

    if "correction-td" in text:
        return "correction"

    if "correction_td" in text:
        return "correction"

    if re.search(r"\btd\b", text):
        return "td"

    if "cours" in text:
        return "cours"

    return None


def detect_chapter(text):
    """
    Extrait ch04, ch12, etc.
    """

    match = re.search(
        r"(ch\d+)",
        text.lower()
    )

    if match:
        return match.group(1)

    return None


links = soup.find_all("a")


for link in links:

    href = link.get("href")

    if not href:
        continue


    text = link.get_text(
        " ",
        strip=True
    )


    full_text = f"{text} {href}".lower()


    if ".pdf" not in full_text:
        continue


    chapter = detect_chapter(full_text)

    if not chapter:
        continue


    document_type = detect_document_type(
        full_text
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
        f"{document_type} : "
        f"{filename}"
    )


    try:

        pdf_response = session.get(
            pdf_url,
            timeout=60
        )

        pdf_response.raise_for_status()


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


        print("  -> téléchargé")


    except Exception as error:

        print(
            f"  -> erreur : {error}"
        )


# Supprime les doublons
unique_programmes = []


seen = set()


for item in programmes:

    key = (
        item["chapitre"],
        item["type"]
    )

    if key in seen:
        continue

    seen.add(key)

    unique_programmes.append(item)


# Tri par chapitre
def chapter_number(item):

    match = re.search(
        r"\d+",
        item["chapitre"]
    )

    if match:
        return int(match.group())

    return 9999


unique_programmes.sort(
    key=lambda item: (
        chapter_number(item),
        item["type"]
    )
)


data = {
    "programmes": unique_programmes
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
    f"{len(unique_programmes)} documents "
    f"enregistrés dans {OUTPUT_JSON}"
)