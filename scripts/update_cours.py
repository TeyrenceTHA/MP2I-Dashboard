import os
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://maths-cpge.fr"
COURSES_URL = f"{BASE_URL}/chapitres/"

USERNAME = os.environ.get("MATHS_CPGE_ID")
PASSWORD = os.environ.get("MATHS_CPGE_PASSWORD")

if not USERNAME or not PASSWORD:
    raise RuntimeError("Secrets manquants.")

session = requests.Session()

print("Connexion au site...")

login_data = {
    "log": USERNAME,
    "pwd": PASSWORD,
    "wp-submit": "Log In",
    "redirect_to": COURSES_URL,
    "testcookie": "1"
}

login = session.post(
    f"{BASE_URL}/wp-login.php",
    data=login_data,
    timeout=30,
    allow_redirects=True
)

print("Login HTTP :", login.status_code)
print("URL après connexion :", login.url)

print()
print("Récupération des chapitres...")

page = session.get(
    COURSES_URL,
    timeout=30
)

print("Page HTTP :", page.status_code)
print("URL finale :", page.url)
print("Taille HTML :", len(page.text))

print()

soup = BeautifulSoup(
    page.text,
    "html.parser"
)

links = soup.find_all("a")

print("Nombre de liens trouvés :", len(links))
print()

for link in links[:50]:

    text = link.get_text(" ", strip=True)
    href = link.get("href")

    print(
        "TEXT:",
        repr(text),
        "| HREF:",
        repr(href)
    )

print()
print("Recherche des PDF...")

pdfs = []

for link in links:

    href = link.get("href") or ""

    if ".pdf" in href.lower():
        pdfs.append(href)


print("PDF trouvés :", len(pdfs))

for pdf in pdfs:
    print(pdf)