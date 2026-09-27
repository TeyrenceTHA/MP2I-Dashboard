```python
import os
import json
import requests

from bs4 import BeautifulSoup
from requests.auth import HTTPDigestAuth
from urllib.parse import urljoin


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://maths-cpge.fr"
CHAPITRES_URL = f"{BASE_URL}/chapitres/"

PAGE_PASSWORD = os.environ.get("MATHS_CPGE_PASSWORD")
PDF_ID = os.environ.get("MATHS_CPGE_ID")
PDF_PASSWORD = os.environ.get("MATHS_CPGE_PASSWORD")

OUTPUT_DIR = "programmes/cours"
JSON_FILE = os.path.join(OUTPUT_DIR, "cours.json")


if not PAGE_PASSWORD:
    raise RuntimeError("MATHS_CPGE_PASSWORD est absent.")

if not PDF_ID:
    raise RuntimeError("MATHS_CPGE_ID est absent.")


# ============================================================
# SESSION
# ============================================================

session = requests.Session()

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/154.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}


# ============================================================
# 1. ACCÈS À LA PAGE /CHAPITRES/
# ============================================================

print("Accès à la page des chapitres...")

response = session.get(
    CHAPITRES_URL,
    headers=headers,
    timeout=30
)

print("HTTP :", response.status_code)
print("URL :", response.url)

response.raise_for_status()


# ============================================================
# 2. DÉTECTION DU MOT DE PASSE DE PAGE
# ============================================================

soup = BeautifulSoup(response.text, "html.parser")

password_field = soup.find(
    "input",
    attrs={"name": "post_password"}
)

if password_field:
    print("Page protégée par mot de passe.")
    print("Envoi du mot de passe...")

    password_form = password_field.find_parent("form")

    if not password_form:
        raise RuntimeError(
            "Champ post_password trouvé mais formulaire introuvable."
        )

    action = password_form.get("action") or CHAPITRES_URL
    action = urljoin(CHAPITRES_URL, action)

    password_data = {
        "post_password": PAGE_PASSWORD
    }

    # Certains formulaires WordPress utilisent également redirect_to.
    redirect_field = password_form.find(
        "input",
        attrs={"name": "redirect_to"}
    )

    if redirect_field and redirect_field.get("value"):
        password_data["redirect_to"] = redirect_field["value"]

    password_response = session.post(
        action,
        data=password_data,
        headers={
            **headers,
            "Referer": CHAPITRES_URL
        },
        timeout=30,
        allow_redirects=True
    )

    print("Réponse :", password_response.status_code)
    print("URL après mot de passe :", password_response.url)

    password_response.raise_for_status()

    # Vérification
    verify = session.get(
        CHAPITRES_URL,
        headers=headers,
        timeout=30
    )

    print("Vérification de l'accès...")
    verify.raise_for_status()

    soup = BeautifulSoup(verify.text, "html.parser")

    if soup.find(
        "input",
        attrs={"name": "post_password"}
    ):
        raise RuntimeError(
            "Le mot de passe de la page semble incorrect."
        )

    html = verify.text

else:
    print("La page n'est pas protégée par post_password.")
    html = response.text


print("Accès aux chapitres confirmé.")
print("Taille HTML :", len(html))


# ============================================================
# 3. RECHERCHE DES PDF
# ============================================================

soup = BeautifulSoup(html, "html.parser")

pdf_links = []

for link in soup.find_all("a", href=True):

    href = link["href"].strip()

    if not href.lower().endswith(".pdf"):
        continue

    pdf_url = urljoin(BASE_URL, href)

    if pdf_url not in pdf_links:
        pdf_links.append(pdf_url)


print("PDF trouvés :", len(pdf_links))


if not pdf_links:
    raise RuntimeError(
        "Aucun PDF trouvé sur la page des chapitres."
    )


# ============================================================
# 4. PRÉPARATION DU DOSSIER
# ============================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)

programmes = []


# ============================================================
# 5. TÉLÉCHARGEMENT DES PDF
# ============================================================

for url in pdf_links:

    filename = url.split("/")[-1]

    print()
    print("=" * 60)
    print("PDF :", filename)
    print("URL :", url)

    # --------------------------------------------------------
    # Détection du chapitre
    # --------------------------------------------------------

    filename_lower = filename.lower()

    chapter = None

    if filename_lower.startswith("ch"):

        number = ""

        for char in filename_lower[2:]:
            if char.isdigit():
                number += char
            else:
                break

        if number:
            chapter = f"ch{number}"

    if not chapter:
        print("  -> chapitre impossible à déterminer")
        continue


    # --------------------------------------------------------
    # Détection du type
    # --------------------------------------------------------

    if "td-correction" in filename_lower:
        document_type = "correction"

    elif "-td" in filename_lower:
        document_type = "td"

    elif "-cours" in filename_lower:
        document_type = "cours"

    else:
        print("  -> type inconnu, ignoré")
        continue


    # --------------------------------------------------------
    # Nom local
    # --------------------------------------------------------

    local_filename = filename

    local_path = os.path.join(
        OUTPUT_DIR,
        local_filename
    )


    # --------------------------------------------------------
    # Téléchargement avec HTTP Digest
    # --------------------------------------------------------

    print(
        f"  -> téléchargement ({document_type})..."
    )

    try:

        pdf = session.get(
            url,
            headers=headers,
            auth=HTTPDigestAuth(
                PDF_ID,
                PDF_PASSWORD
            ),
            timeout=30
        )

        print(
            "  -> HTTP :",
            pdf.status_code
        )

        pdf.raise_for_status()

        content_type = pdf.headers.get(
            "Content-Type",
            ""
        ).lower()

        if "application/pdf" not in content_type:

            print(
                "  -> avertissement : Content-Type =",
                content_type
            )

        with open(
            local_path,
            "wb"
        ) as file:

            file.write(pdf.content)

        print(
            "  -> enregistré :",
            local_path
        )

    except Exception as error:

        print(
            "  -> erreur :",
            error
        )

        continue


    # --------------
```
