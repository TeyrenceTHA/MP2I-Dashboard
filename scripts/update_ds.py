import os
import json
from pathlib import Path

import requests
from requests.auth import HTTPDigestAuth


BASE_URL = "https://maths-cpge.fr"
PDF_ID = os.environ["MATHS_CPGE_ID"]
PASSWORD = os.environ["MATHS_CPGE_PASSWORD"]

OUTPUT_DIR = Path("programmes/ds")
PDF_DIR = OUTPUT_DIR / "pdf"
JSON_FILE = OUTPUT_DIR / "ds.json"

PDF_DIR.mkdir(parents=True, exist_ok=True)

session = requests.Session()

auth = HTTPDigestAuth(PDF_ID, PASSWORD)

documents = []

for type_devoir in ["dm", "ds"]:

    for numero in range(1, 51):

        for partie in ["sujet", "corrige"]:

            filename = (
                f"{type_devoir}{numero:02d}-{partie}.pdf"
            )

            url = f"{BASE_URL}/docs/devoirs/{filename}"

            try:
                response = session.get(
                    url,
                    auth=auth,
                    timeout=20
                )

                if response.status_code == 404:
                    continue

                response.raise_for_status()

                # Vérifier que la réponse est bien un PDF
                if not response.content.startswith(b"%PDF"):
                    print("Fichier ignoré :", filename)
                    continue

                local_path = PDF_DIR / filename
                local_path.write_bytes(response.content)

                titre = f"{type_devoir.upper()}{numero}"

                documents.append({
                    "titre": titre,
                    "type": type_devoir.upper(),
                    "partie": partie,
                    "fichier": f"pdf/{filename}",
                    "source": url
                })

                print("Téléchargé :", filename)

            except requests.RequestException as error:
                print("Erreur :", filename, error)


data = {
    "source": BASE_URL + "/devoirs/",
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
print("Documents trouvés :", len(documents))
print("JSON mis à jour :", JSON_FILE)