const container =
    document.getElementById("cours-container");


if (!container) {
    console.error("cours-container introuvable");
} else {

    fetch(
        "programmes/cours/cours.json?v=" +
        Date.now()
    )

    .then(response => {

        console.log(
            "cours.json :",
            response.status
        );

        if (!response.ok) {
            throw new Error(
                "HTTP " + response.status
            );
        }

        return response.json();

    })

    .then(data => {

        console.log(
            "Données des cours :",
            data
        );


        container.innerHTML = "";


        if (
            !data.programmes ||
            data.programmes.length === 0
        ) {

            container.innerHTML = `

                <div class="glass loading-card">

                    Aucun cours disponible.

                </div>

            `;

            return;
        }


        const chapitres = {};


        data.programmes.forEach(item => {

            const chapitre =
                item.chapitre;

            if (!chapitres[chapitre]) {

                chapitres[chapitre] = {};

            }

            chapitres[chapitre][
                item.type.toLowerCase()
            ] = item.url;

        });


        const liste =
            Object.keys(chapitres)
            .sort((a, b) => {

                const numA =
                    parseInt(
                        a.replace("ch", "")
                    );

                const numB =
                    parseInt(
                        b.replace("ch", "")
                    );

                return numA - numB;

            });


        liste.forEach(chapitre => {

            const numero =
                parseInt(
                    chapitre.replace("ch", "")
                );


            const card =
                document.createElement("div");

            card.className =
                "dashboard-card glass";


            const cours =
                chapitres[chapitre].cours;

            const td =
                chapitres[chapitre].td;


            card.innerHTML = `

                <div class="card-icon">

                    ${String(numero).padStart(2, "0")}

                </div>


                <div>

                    <h3>
                        Chapitre ${numero}
                    </h3>

                    <p>
                        Cours et exercices disponibles.
                    </p>


                    <div class="course-buttons">

                        ${
                            cours
                            ? `
                                <a
                                    class="mini-button"
                                    href="programmes/cours/${cours}"
                                    target="_blank"
                                    rel="noopener"
                                >
                                    Cours →
                                </a>
                            `
                            : ""
                        }


                        ${
                            td
                            ? `
                                <a
                                    class="mini-button"
                                    href="programmes/cours/${td}"
                                    target="_blank"
                                    rel="noopener"
                                >
                                    TD →
                                </a>
                            `
                            : ""
                        }

                    </div>

                </div>

            `;


            container.appendChild(card);

        });


        console.log(
            liste.length +
            " chapitre(s) affiché(s)"
        );

    })

    .catch(error => {

        console.error(
            "Erreur chargement cours :",
            error
        );


        container.innerHTML = `

            <div class="glass loading-card">

                Impossible de charger les cours.

                <br>

                <small>
                    ${error.message}
                </small>

            </div>

        `;

    });

}