import os
import re
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


SOURCE_URL = "https://maths-cpge.fr/chapitres/"

OUTPUT_DIR = Path("programmes/cours")
HTML_FILE = OUTPUT_DIR / "cours.html"

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

    # Première requête : récupérer le formulaire
    response = session.get(
        SOURCE_URL,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

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

    # Récupérer les champs cachés du formulaire
    data = {}

    for input_tag in form.find_all("input"):

        name = input_tag.get("name")

        if not name:
            continue

        input_type = input_tag.get(
            "type",
            "text"
        )

        if input_type in ["hidden"]:
            data[name] = input_tag.get(
                "value",
                ""
            )

    # Chercher le champ mot de passe
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

    # Vérifier que la page est réellement déverrouillée
    if "Ce contenu est protégé par un mot de passe" in unlocked.text:
        raise RuntimeError(
            "Le mot de passe n'a pas permis de déverrouiller la page."
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

    # Sauvegarder la page déverrouillée
    HTML_FILE.write_text(
        soup.prettify(),
        encoding="utf-8"
    )

    print("Page enregistrée :", HTML_FILE)


if __name__ == "__main__":
    main()