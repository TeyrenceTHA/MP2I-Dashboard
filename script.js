// ================================
// PARAMÈTRES / THÈMES
// ================================

const settingsButton =
    document.getElementById("settingsButton");

const themePanel =
    document.getElementById("themePanel");


if (settingsButton && themePanel) {

    settingsButton.addEventListener(
        "click",
        function(event) {

            event.preventDefault();

            themePanel.classList.toggle("show");

        }
    );

}


function setTheme(theme) {

    document.body.classList.remove(
        "theme-purple",
        "theme-red",
        "theme-green"
    );

    document.body.classList.add(
        "theme-" + theme
    );

    localStorage.setItem(
        "theme",
        theme
    );

}


const savedTheme =
    localStorage.getItem("theme") ||
    "purple";

setTheme(savedTheme);


// ================================
// RECHERCHE GLOBALE
// ================================

const searchInput =
    document.getElementById("globalSearch");

const searchResults =
    document.getElementById("searchResults");


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
// AJOUTER UN ÉLÉMENT À LA RECHERCHE
// ================================

function addSearchItem(
    title,
    description,
    type,
    url
) {

    searchData.push({

        title: title,

        description:
            description || "",

        type:
            type || "",

        url: url

    });

}


// ================================
// CHARGER LES KHÔLLES
// ================================

fetch("programmes/maths/maths.json")

    .then(response => {

        if (!response.ok) {

            throw new Error(
                "maths.json introuvable"
            );

        }

        return response.json();

    })

    .then(data => {

        if (!data.programmes) return;


        data.programmes.forEach(
            programme => {

                addSearchItem(

                    programme.semaine,

                    programme.titre,

                    "Khôlle",

                    "programmes/maths/" +
                    programme.fichier

                );

            }
        );

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

            throw new Error(
                "cours.json introuvable"
            );

        }

        return response.json();

    })

    .then(data => {

        if (!data.programmes) return;


        data.programmes.forEach(
            document => {

                const numero =
                    document.chapitre
                        .replace("ch", "");


                const type =
                    document.type
                        ? document.type.toUpperCase()
                        : "DOCUMENT";


                addSearchItem(

                    "Chapitre " +
                    numero +
                    " — " +
                    type,

                    "Cours de mathématiques",

                    "Cours",

                    "programmes/cours/" +
                    document.url

                );

            }
        );

    })

    .catch(error => {

        console.error(
            "Erreur chargement cours :",
            error
        );

    });


// ================================
// CHARGER LES DS / DM
// ================================

fetch("programmes/ds/ds.json")

    .then(response => {

        if (!response.ok) {

            throw new Error(
                "ds.json introuvable"
            );

        }

        return response.json();

    })

    .then(data => {

        if (!data.devoirs) return;


        data.devoirs.forEach(
            devoir => {

                const partie =
                    devoir.partie === "sujet"
                        ? "Sujet"
                        : "Corrigé";


                addSearchItem(

                    devoir.titre +
                    " — " +
                    partie,

                    "Devoir de " +
                    devoir.type,

                    "DS / DM",

                    "programmes/ds/" +
                    devoir.fichier

                );

            }
        );

    })

    .catch(error => {

        console.error(
            "Erreur chargement DS :",
            error
        );

    });


// ================================
// CHARGER LES NOTEBOOKS
// ================================

function loadNotebooks() {

    const subjects = [

        {
            key: "mp2i-maths-notebooks",
            name: "Mathématiques"
        },

        {
            key: "mp2i-physique-notebooks",
            name: "Physique"
        },

        {
            key: "mp2i-info-notebooks",
            name: "Informatique"
        }

    ];


    subjects.forEach(subject => {

        const saved =
            localStorage.getItem(
                subject.key
            );


        if (!saved) return;


        try {

            const notebooks =
                JSON.parse(saved);


            if (!Array.isArray(notebooks)) {
                return;
            }


            notebooks.forEach(
                notebook => {

                    if (
                        !notebook.name ||
                        !notebook.url
                    ) {
                        return;
                    }


                    addSearchItem(

                        notebook.name,

                        "Notebook de révision",

                        "Notebook · " +
                        subject.name,

                        notebook.url

                    );

                }
            );

        }

        catch (error) {

            console.error(
                "Erreur chargement notebooks :",
                subject.name,
                error
            );

        }

    });

}


// Charger les notebooks
loadNotebooks();


// ================================
// AFFICHER LES RÉSULTATS
// ================================

function displayResults(query) {

    searchResults.innerHTML = "";


    if (!query) {

        searchResults.classList.remove(
            "show"
        );

        return;

    }


    const normalizedQuery =
        normalizeText(query);


    const results =
        searchData.filter(item => {

            const title =
                normalizeText(
                    item.title
                );


            const description =
                normalizeText(
                    item.description
                );


            const type =
                normalizeText(
                    item.type
                );


            return (

                title.includes(
                    normalizedQuery
                )

                ||

                description.includes(
                    normalizedQuery
                )

                ||

                type.includes(
                    normalizedQuery
                )

            );

        });


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


        searchResults.classList.add(
            "show"
        );

        return;

    }


    results.forEach(item => {

        const result =
            document.createElement("a");


        result.className =
            "search-result";


        result.href =
            item.url;


        result.target =
            "_blank";


        result.rel =
            "noopener noreferrer";


        result.innerHTML = `

            <div>

                <div class="search-result-title">
                    ${item.title}
                </div>

                <div class="search-result-type">
                    ${item.type}
                    ${
                        item.description
                            ? " · " +
                              item.description
                            : ""
                    }
                </div>

            </div>

        `;


        searchResults.appendChild(
            result
        );

    });


    searchResults.classList.add(
        "show"
    );

}


// ================================
// ÉVÉNEMENT DE RECHERCHE
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
if ("serviceWorker" in navigator) {

    window.addEventListener("load", () => {

        navigator.serviceWorker.register("./sw.js")
            .then(() => {
                console.log("PWA activée");
            })
            .catch(error => {
                console.error(
                    "Erreur PWA :",
                    error
                );
            });

    });

}