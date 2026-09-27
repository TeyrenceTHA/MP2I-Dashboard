import os
import json
import re
from pathlib import Path

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


# ================================
# RÉCUPÉRER LA PAGE
# ================================

response = session.get(PAGE_URL, timeout=30)

response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")


# ================================
# TROUVER LES PDF
# ================================

documents = []


for link in soup.find_all("a", href=True):

    href = link["href"]

    if "/docs/devoirs/" not in href:
        continue

    if not href.lower().endswith(".pdf"):
        continue

    url = (
        href
        if href.startswith("http")
        else BASE_URL + href
    )

    filename = Path(url).name

    # Évite les doublons
    if any(doc["fichier"] == filename for doc in documents):
        continue

    # Exemple : dm02-sujet.pdf
    match = re.search(
        r"(dm|ds)(\d+)",
        filename,
        re.IGNORECASE
    )

    if match:

        type_devoir = match.group(1).upper()
        numero = int(match.group(2))

        titre = f"{type_devoir}{numero}"

    else:

        titre = filename.replace(".pdf", "")


    local_path = PDF_DIR / filename


    # ================================
    # TÉLÉCHARGEMENT
    # ================================

    print("Téléchargement :", filename)

    pdf = session.get(
        url,
        auth=HTTPDigestAuth(
            PDF_ID,
            PASSWORD
        ),
        timeout=30
    )

    print("Réponse HTTP :", pdf.status_code)

    pdf.raise_for_status()

    local_path.write_bytes(pdf.content)

    print("Enregistré :", local_path)


    documents.append({

        "titre": titre,

        "fichier": f"pdf/{filename}",

        "source": url

    })


# ================================
# JSON
# ================================

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