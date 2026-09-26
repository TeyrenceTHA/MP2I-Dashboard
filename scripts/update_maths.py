import json
import re
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


SOURCE_URL = "https://maths-cpge.fr/colles/"

OUTPUT_DIR = Path("programmes/maths")
PDF_DIR = OUTPUT_DIR / "pdf"
JSON_FILE = OUTPUT_DIR / "maths.json"

HEADERS = {
    "User-Agent": "MP2I-Dashboard/1.0"
}


def clean_filename(text):
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", "-", text.strip())
    return text.lower()


def main():
    print("Connexion à :", SOURCE_URL)

    response = requests.get(
        SOURCE_URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    programmes = []

    for link in soup.find_all("a", href=True):

        text = link.get_text(" ", strip=True)

        if "programme détaillé" not in text.lower():
            continue

        url = urljoin(SOURCE_URL, link["href"])

        print("Programme trouvé :", text)
        print("URL :", url)

        parent_text = link.parent.get_text(" ", strip=True)

        week_match = re.search(
            r"\bS\d+\b",
            parent_text,
            re.IGNORECASE
        )

        week = (
            week_match.group(0).upper()
            if week_match
            else "Programme"
        )

        # Utilise le vrai nom du PDF fourni par le site
        filename = Path(url).name

        pdf_path = PDF_DIR / filename

        try:
            pdf_response = requests.get(
                url,
                headers=HEADERS,
                timeout=30
            )

            pdf_response.raise_for_status()

            if not pdf_response.content.startswith(b"%PDF"):
                print("Attention : ce fichier ne semble pas être un PDF.")
                continue

            pdf_path.write_bytes(pdf_response.content)

            programmes.append({
                "semaine": week,
                "titre": text,
                "fichier": f"pdf/{filename}",
                "source": url
            })

            print("Téléchargé :", pdf_path)

        except Exception as error:
            print("Erreur :", error)

    programmes.sort(
        key=lambda x: int(
            re.search(r"\d+", x["semaine"]).group()
        ) if re.search(r"\d+", x["semaine"]) else 0,
        reverse=True
    )

    data = {
        "source": SOURCE_URL,
        "programmes": programmes
    }

    JSON_FILE.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=4
        ),
        encoding="utf-8"
    )

    print()
    print("Nombre de programmes :", len(programmes))
    print("JSON créé :", JSON_FILE)


if __name__ == "__main__":
    main()