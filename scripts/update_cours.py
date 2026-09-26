import json
import os
import re
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


SOURCE_URL = "https://maths-cpge.fr/chapitres/"

OUTPUT_DIR = Path("programmes/cours")
JSON_FILE = OUTPUT_DIR / "cours.json"

PASSWORD = os.environ.get("MATHS_CPGE_PASSWORD")


def main():

    if not PASSWORD:
        raise RuntimeError(
            "Le secret MATHS_CPGE_PASSWORD est introuvable."
        )

    session = requests.Session()

    headers = {
        "User-Agent": "MP2I-Dashboard/1.0"
    }

    print("Connexion à :", SOURCE_URL)

    response = session.get(
        SOURCE_URL,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    form = soup.find("form")

    if not form:
        raise RuntimeError(
            "Formulaire de mot de passe introuvable."
        )

    action = form.get("action") or SOURCE_URL

    action = urljoin(
        SOURCE_URL,
        action
    )

    data = {}

    for input_tag in form.find_all("input"):

        name = input_tag.get("name")

        if not name:
            continue

        if input_tag.get("type", "text") == "hidden":
            data[name] = input_tag.get("value", "")

    password_input = form.find(
        "input",
        {"type": "password"}
    )

    if not password_input:
        raise RuntimeError(
            "Champ de mot de passe introuvable."
        )

    password_name = password_input.get("name")

    if not password_name:
        raise RuntimeError(
            "Nom du champ mot de passe introuvable."
        )

    data[password_name] = PASSWORD

    print("Envoi du mot de passe...")

    unlocked = session.post(
        action,
        data=data,
        headers=headers,
        timeout=30
    )

    unlocked.raise_for_status()

    if "Ce contenu est protégé par un mot de passe" in unlocked.text:
        raise RuntimeError(
            "Le mot de passe n'a pas permis de déverrouiller la page."
        )

    print("Page déverrouillée.")

    soup = BeautifulSoup(
        unlocked.text,
        "html.parser"
    )

    programmes = []

    for link in soup.find_all("a", href=True):

        href = link["href"]

        match = re.search(
            r"/docs/chapitres/(ch\d+)-(cours|td)\.pdf",
            href,
            re.IGNORECASE
        )

        if not match:
            continue

        chapitre = match.group(1).lower()
        type_document = match.group(2).lower()

        url = urljoin(
            SOURCE_URL,
            href
        )

        programmes.append({
            "chapitre": chapitre,
            "type": type_document,
            "url": url
        })

        print(
            "Trouvé :",
            chapitre,
            type_document,
            url
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    JSON_FILE.write_text(
        json.dumps(
            {
                "source": SOURCE_URL,
                "programmes": programmes
            },
            ensure_ascii=False,
            indent=4
        ),
        encoding="utf-8"
    )

    print()
    print(
        "Nombre de documents trouvés :",
        len(programmes)
    )

    print(
        "JSON créé :",
        JSON_FILE
    )


if __name__ == "__main__":
    main()