import os
import json
import requests
from bs4 import BeautifulSoup
from requests.auth import HTTPDigestAuth
from urllib.parse import urljoin

BASE_URL = "https://maths-cpge.fr"
CHAPITRES_URL = f"{BASE_URL}/chapitres/"

PASSWORD = os.environ.get("MATHS_CPGE_PASSWORD")
PDF_ID = os.environ.get("MATHS_CPGE_ID")

OUTPUT_DIR = "programmes/cours"
JSON_FILE = os.path.join(OUTPUT_DIR, "cours.json")

if not PASSWORD:
    raise RuntimeError("Secret MATHS_CPGE_PASSWORD manquant.")

if not PDF_ID:
    raise RuntimeError("Secret MATHS_CPGE_ID manquant.")

session = requests.Session()

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/154.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}

print("1. Ouverture de /chapitres/...")

page = session.get(
    CHAPITRES_URL,
    headers=headers,
    timeout=30
)

print("HTTP :", page.status_code)

page.raise_for_status()

soup = BeautifulSoup(
    page.text,
    "html.parser"
)

password_input = soup.find(
    "input",
    attrs={"name": "post_password"}
)

if password_input:
    print("2. Page protégée : envoi du mot de passe...")

    form = password_input.find_parent("form")

    if not form:
        raise RuntimeError(
            "Formulaire post_password introuvable."
        )

    action = urljoin(
        CHAPITRES_URL,
        form.get("action") or CHAPITRES_URL
    )

    data = {
        "post_password": PASSWORD
    }

    redirect = form.find(
        "input",
        attrs={"name": "redirect_to"}
    )

    if redirect and redirect.get("value"):
        data["redirect_to"] = redirect["value"]

    unlocked = session.post(
        action,
        data=data,
        headers={
            **headers,
            "Referer": CHAPITRES_URL
        },
        timeout=30,
        allow_redirects=True
    )

    print(
        "Réponse mot de passe :",
        unlocked.status_code
    )

    unlocked.raise_for_status()

    page = session.get(
        CHAPITRES_URL,
        headers=headers,
        timeout=30
    )

    page.raise_for_status()

    soup = BeautifulSoup(
        page.text,
        "html.parser"
    )

    if soup.find(
        "input",
        attrs={"name": "post_password"}
    ):
        raise RuntimeError(
            "Le mot de passe de /chapitres/ est refusé."
        )

else:
    print(
        "2. La page n'est pas protégée par post_password."
    )

print("3. Recherche des PDF...")

pdf_links = []

for link in soup.find_all("a", href=True):
    href = link["href"].strip()

    if not href.lower().endswith(".pdf"):
        continue

    url = urljoin(
        BASE_URL,
        href
    )

    if url not in pdf_links:
        pdf_links.append(url)

print(
    "PDF trouvés :",
    len(pdf_links)
)

if not pdf_links:
    raise RuntimeError(
        "Aucun PDF trouvé sur /chapitres/."
    )

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

programmes = []

for url in pdf_links:
    filename = url.rstrip("/").split("/")[-1]
    name = filename.lower()

    if not name.startswith("ch"):
        continue

    number = ""

    for char in name[2:]:
        if char.isdigit():
            number += char
        else:
            break

    if not number:
        continue

    chapter = f"ch{number}"

    if "td-correction" in name:
        document_type = "correction"

    elif "-td" in name:
        document_type = "td"

    elif "-cours" in name:
        document_type = "cours"

    else:
        print(
            "Type inconnu :",
            filename
        )
        continue

    destination = os.path.join(
        OUTPUT_DIR,
        filename
    )

    print()
    print("----------------------------------------")
    print("PDF :", filename)
    print("Type :", document_type)
    print("URL :", url)

    try:
        pdf = session.get(
            url,
            headers={
                **headers,
                "Accept": "application/pdf,*/*",
                "Referer": CHAPITRES_URL
            },
            auth=HTTPDigestAuth(
                PDF_ID,
                PASSWORD
            ),
            timeout=30,
            allow_redirects=True
        )

        print(
            "HTTP :",
            pdf.status_code
        )

        if pdf.status_code == 401:
            print(
                "ERREUR 401 : authentification Digest refusée."
            )
            continue

        pdf.raise_for_status()

        if not pdf.content.startswith(b"%PDF"):
            print(
                "ERREUR : la réponse n'est pas un PDF."
            )
            continue

        with open(
            destination,
            "wb"
        ) as file:
            file.write(pdf.content)

        print(
            "OK :",
            destination
        )

        programmes.append({
            "chapitre": chapter,
            "type": document_type,
            "url": filename
        })

    except requests.RequestException as error:
        print(
            "ERREUR :",
            error
        )

programmes.sort(
    key=lambda item: (
        int(item["chapitre"][2:]),
        {
            "cours": 0,
            "td": 1,
            "correction": 2
        }.get(
            item["type"],
            9
        )
    )
)

with open(
    JSON_FILE,
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        {
            "programmes": programmes
        },
        file,
        ensure_ascii=False,
        indent=2
    )

print()
print("========================================")
print("TERMINÉ")
print("========================================")
print(
    "PDF téléchargés :",
    len(programmes)
)
print(
    "JSON généré :",
    JSON_FILE
)
