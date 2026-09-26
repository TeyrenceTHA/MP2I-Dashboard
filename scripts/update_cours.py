import os
import re
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


SOURCE_URL = "https://maths-cpge.fr/chapitres/"

OUTPUT_DIR = Path("programmes/cours")

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

    # Récupérer la page protégée
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
    print()
    print("=== LIENS PDF TROUVÉS ===")

    for link in soup.find_all("a", href=True):
        href = link["href"]

        if ".pdf" in href.lower():
            print(href)

    print("=== FIN ===")
    print()

    # Trouver le formulaire de mot de passe
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

    # Récupérer les champs cachés
    data = {}

    for input_tag in form.find_all("input"):

        name = input_tag.get("name")

        if not name:
            continue

        if input_tag.get("type", "text") == "hidden":
            data[name] = input_tag.get("value", "")

    # Champ mot de passe
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

    # Vérification
    if "Ce contenu est protégé par un mot de passe" in unlocked.text:
        raise RuntimeError(
            "Mot de passe incorrect ou page toujours protégée."
        )

    print("Page déverrouillée.")

    soup = BeautifulSoup(
        unlocked.text,
        "html.parser"
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Chercher tous les PDF de chapitres
    pdf_links = soup.find_all(
        "a",
        href=True
    )

    downloaded = 0

    for link in pdf_links:

        href = link["href"]

        # On ne garde que les PDF de chapitres
        if not re.search(
            r"/docs/chapitres/.*\.pdf$",
            href,
            re.IGNORECASE
        ):
            continue

        url = urljoin(
            SOURCE_URL,
            href
        )

        filename = Path(href).name

        output_path = OUTPUT_DIR / filename

        print("Téléchargement :", filename)

        try:

            pdf = session.get(
                url,
                headers=headers,
                timeout=30
            )

            pdf.raise_for_status()

            if not pdf.content.startswith(b"%PDF"):
                print(
                    "Attention : fichier non reconnu comme PDF."
                )
                continue

            output_path.write_bytes(
                pdf.content
            )

            downloaded += 1

        except Exception as error:

            print(
                "Erreur pour",
                filename,
                ":",
                error
            )

    print()
    print(
        "Nombre de PDF téléchargés :",
        downloaded
    )


if __name__ == "__main__":
    main()