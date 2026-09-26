import json
import os
import re
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


SOURCE_URL = "https://maths-cpge.fr/chapitres/"

OUTPUT_DIR = Path("programmes/cours")
PDF_DIR = OUTPUT_DIR / "pdf"
JSON_FILE = OUTPUT_DIR / "cours.json"

PASSWORD = os.environ.get("MATHS_CPGE_PASSWORD")
PDF_ID = os.environ.get("MATHS_CPGE_ID")


def main():

    if not PASSWORD:
        raise RuntimeError(
            "Le secret MATHS_CPGE_PASSWORD est introuvable."
        )

    if not PDF_ID:
        raise RuntimeError(
            "Le secret MATHS_CPGE_ID est introuvable."
        )

    session = requests.Session()

    headers = {
        "User-Agent": "MP2I-Dashboard/1.0"
    }

    print("Connexion à :", SOURCE_URL)

    # --------------------------------------------------
    # 1. Déverrouiller la page des chapitres
    # --------------------------------------------------

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

    # --------------------------------------------------
    # 2. Préparer les dossiers
    # --------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    PDF_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    programmes = []

    # --------------------------------------------------
    # 3. Trouver les PDF
    # --------------------------------------------------

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

        filename = Path(href).name

        local_path = PDF_DIR / filename

        print()
        print("Téléchargement :", filename)

        # --------------------------------------------------
        # 4. Télécharger avec ID + mot de passe
        # --------------------------------------------------

        try:

            pdf = session.get(
                url,
                headers=headers,
                auth=(
                    PDF_ID,
                    PASSWORD
                ),
                timeout=30
            )

            print(
                "Réponse HTTP :",
                pdf.status_code
            )

            pdf.raise_for_status()

            if not pdf.content.startswith(b"%PDF"):
                print(
                    "Erreur : le fichier reçu n'est pas un PDF."
                )
                continue

            local_path.write_bytes(
                pdf.content
            )

            print(
                "Enregistré :",
                local_path
            )

            programmes.append({
                "chapitre": chapitre,
                "type": type_document,
                "url": f"pdf/{filename}"
            })

        except Exception as error:

            print(
                "Erreur pour",
                filename,
                ":",
                error
            )

    # --------------------------------------------------
    # 5. Créer cours.json
    # --------------------------------------------------

    programmes.sort(
        key=lambda x: (
            int(
                re.search(
                    r"\d+",
                    x["chapitre"]
                ).group()
            ),
            x["type"]
        )
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
        "Nombre de documents téléchargés :",
        len(programmes)
    )

    print(
        "JSON créé :",
        JSON_FILE
    )


if __name__ == "__main__":
    main()