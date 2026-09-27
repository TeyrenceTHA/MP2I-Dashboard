import os
import json
import re
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.auth import HTTPDigestAuth


BASE_URL = "https://maths-cpge.fr"
PAGE_URL = BASE_URL + "/devoirs/"

PDF_ID = os.environ["MATHS_CPGE_ID"]
PASSWORD = os.environ["MATHS_CPGE_PASSWORD"]

OUTPUT_DIR = Path("programmes/ds")
PDF_DIR = OUTPUT_DIR / "pdf"
JSON_FILE = OUTPUT_DIR / "ds.json"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PDF_DIR.mkdir(parents=True, exist_ok=True)


session = requests.Session()

response = session.get(
    PAGE_URL,
    timeout=30
)

print("Page HTTP :", response.status_code)

response.raise_for_status()

print("Taille de la page :", len(response.text))

soup = BeautifulSoup(
    response.text,
    "html.parser"
)
print("=== RECHERCHE PDF DANS LE HTML ===")

pdf_matches = re.findall(
    r'[^"\']+\.pdf',
    response.text,
    re.IGNORECASE
)

for match in pdf_matches:
    print("PDF TROUVÉ :", match)

print("Nombre de PDF :", len(pdf_matches))
print("Nombre de liens :", len(soup.find_all("a")))

for link in soup.find_all("a", href=True):
    href = link["href"].strip()

    if "devoir" in href.lower() or ".pdf" in href.lower():
        print("LIEN TROUVÉ :", href)


documents = []


for link in soup.find_all("a", href=True):

    href = link["href"].strip()

    # On cherche directement les fichiers DM/DS
    match = re.search(
        r"(dm|ds)(\d+)[^/]*\.pdf",
        href,
        re.IGNORECASE
    )

    if not match:
        continue


    type_devoir = match.group(1).upper()
    numero = int(match.group(2))

    filename = Path(href).name


    if filename in [
        document["fichier"]
        for document in documents
    ]:
        continue


    url = urljoin(
        BASE_URL,
        href
    )


    titre = f"{type_devoir}{numero}"


    local_path = PDF_DIR / filename


    print()
    print("Trouvé :", filename)
    print("URL :", url)


    pdf = session.get(
        url,
        auth=HTTPDigestAuth(
            PDF_ID,
            PASSWORD
        ),
        timeout=30
    )


    print(
        "Réponse PDF :",
        pdf.status_code
    )


    pdf.raise_for_status()


    local_path.write_bytes(
        pdf.content
    )


    print(
        "Enregistré :",
        local_path
    )


    documents.append({
        "titre": titre,
        "type": type_devoir,
        "fichier": f"pdf/{filename}",
        "source": url
    })


data = {
    "source": PAGE_URL,
    "devoirs": documents
}


JSON_FILE.write_text(
    json.dumps(
        data,
        indent=4,
        ensure_ascii=False
    ),
    encoding="utf-8"
)


print()
print("DS trouvés :", len(documents))
print("JSON mis à jour :", JSON_FILE)