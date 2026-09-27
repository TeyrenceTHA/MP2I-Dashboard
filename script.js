// ================================
// PARAMÈTRES / THÈMES
// ================================

const settingsButton = document.getElementById("settingsButton");
const themePanel = document.getElementById("themePanel");

if (settingsButton && themePanel) {
    settingsButton.addEventListener("click", function(event) {
        event.preventDefault();
        themePanel.classList.toggle("show");
    });
}


function setTheme(theme) {

    document.body.classList.remove(
        "theme-purple",
        "theme-red",
        "theme-green"
    );

    document.body.classList.add("theme-" + theme);

    localStorage.setItem("theme", theme);
}


const savedTheme = localStorage.getItem("theme") || "purple";

setTheme(savedTheme);


// ================================
// RECHERCHE GLOBALE
// ================================

const searchInput = document.getElementById("globalSearch");
const searchResults = document.getElementById("searchResults");

let searchData = [];


// ================================
// NORMALISER LE TEXTE
// ================================

function normalizeText(text) {

    return text
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "");
}


// ================================
// CHARGER LES KHÔLLES
// ================================

fetch("programmes/maths/maths.json")

    .then(response => {

        if (!response.ok) {
            throw new Error("maths.json introuvable");
        }

        return response.json();
    })

    .then(data => {

        if (!data.programmes) return;

        data.programmes.forEach(programme => {

            searchData.push({

                title: programme.semaine,

                description: programme.titre,

                type: "Khôlle",

                url:
                    "programmes/maths/" +
                    programme.fichier

            });

        });

    })

    .catch(error => {

        console.error(
            "Erreur chargement khôlles :",
            error
        );

    });


// ================================
// CHARGER LES COURS
// ================================

fetch("programmes/cours/cours.json")

    .then(response => {

        if (!response.ok) {
            throw new Error("cours.json introuvable");
        }

        return response.json();
    })

    .then(data => {

        if (!data.programmes) return;

        data.programmes.forEach(document => {

            const numero = document.chapitre
                .replace("ch", "");

            const type =
                document.type
                    ? document.type.toUpperCase()
                    : "DOCUMENT";

            searchData.push({

                title:
                    "Chapitre " +
                    numero +
                    " — " +
                    type,

                description:
                    "Cours de mathématiques",

                type: "Cours",

                url:
                    "programmes/cours/" +
                    document.url

            });

        });

    })

    .catch(error => {

        console.error(
            "Erreur chargement cours :",
            error
        );

    });


// ================================
// AFFICHER LES RÉSULTATS
// ================================

function displayResults(query) {

    searchResults.innerHTML = "";

    if (!query) {

        searchResults.classList.remove("show");

        return;
    }


    const normalizedQuery =
        normalizeText(query);


    const results = searchData.filter(item => {

        const title =
            normalizeText(item.title);

        const description =
            normalizeText(
                item.description || ""
            );

        const type =
            normalizeText(item.type || "");

        return (
            title.includes(normalizedQuery) ||
            description.includes(normalizedQuery) ||
            type.includes(normalizedQuery)
        );

    });


    // Aucun résultat

    if (results.length === 0) {

        searchResults.innerHTML = `

            <div class="search-result">

                <div>

                    <div class="search-result-title">
                        Aucun résultat
                    </div>

                    <div class="search-result-type">
                        Aucun document correspondant
                    </div>

                </div>

            </div>

        `;

        searchResults.classList.add("show");

        return;
    }


    // Résultats

    results.forEach(item => {

        const result =
            document.createElement("a");

        result.className =
            "search-result";

        result.href =
            item.url;

        result.target =
            "_blank";


        result.innerHTML = `

            <div>

                <div class="search-result-title">
                    ${item.title}
                </div>

                <div class="search-result-type">
                    ${item.type}
                    ${item.description
                        ? " · " + item.description
                        : ""
                    }
                </div>

            </div>

        `;


        searchResults.appendChild(result);

    });


    searchResults.classList.add("show");
}


// ================================
// ÉCOUTER LA RECHERCHE
// ================================

if (searchInput) {

    searchInput.addEventListener(
        "input",
        function() {

            displayResults(
                searchInput.value.trim()
            );

        }
    );

}


// ================================
// FERMER LA RECHERCHE
// ================================

document.addEventListener(
    "click",
    function(event) {

        if (
            !event.target.closest(
                ".global-search"
            )
        ) {

            searchResults.classList.remove(
                "show"
            );

        }

    }
);