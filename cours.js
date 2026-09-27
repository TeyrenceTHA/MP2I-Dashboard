const container =
    document.getElementById("cours-container");


if (!container) {

    console.error(
        "cours-container introuvable"
    );

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
                    "HTTP " +
                    response.status
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


            /*
             * Structure :
             *
             * ch01
             *   cours
             *   td
             *   correction
             *
             * ch02
             *   cours
             *   td
             *   correction
             */

            const chapitres = {};


            data.programmes.forEach(item => {

                const chapitre =
                    item.chapitre;


                if (!chapitres[chapitre]) {

                    chapitres[chapitre] = {};

                }


                const type =
                    String(item.type)
                        .toLowerCase()
                        .trim();


                /*
                 * CORRECTION TD
                 *
                 * Accepte :
                 *
                 * correction
                 * td-correction
                 * td_correction
                 * correction-td
                 * correction_td
                 * ch04-td-correction
                 */

                if (
                    type === "correction" ||
                    type === "td-correction" ||
                    type === "td_correction" ||
                    type === "correction-td" ||
                    type === "correction_td" ||
                    type.endsWith("-td-correction")
                ) {

                    chapitres[chapitre].correction =
                        item.url;

                    return;

                }


                /*
                 * COURS
                 */

                if (
                    type === "cours" ||
                    type.endsWith("-cours")
                ) {

                    chapitres[chapitre].cours =
                        item.url;

                    return;

                }


                /*
                 * TD
                 */

                if (
                    type === "td" ||
                    type.endsWith("-td")
                ) {

                    chapitres[chapitre].td =
                        item.url;

                    return;

                }

            });


            /*
             * Tri des chapitres
             */

            const liste =
                Object.keys(chapitres)
                    .sort((a, b) => {

                        const numA =
                            parseInt(
                                a.replace(/\D/g, "")
                            );

                        const numB =
                            parseInt(
                                b.replace(/\D/g, "")
                            );

                        return numA - numB;

                    });


            /*
             * Création des cartes
             */

            liste.forEach(chapitre => {

                const numero =
                    parseInt(
                        chapitre.replace(/\D/g, "")
                    );


                const card =
                    document.createElement(
                        "div"
                    );


                card.className =
                    "dashboard-card glass";


                const cours =
                    chapitres[chapitre].cours;


                const td =
                    chapitres[chapitre].td;


                const correction =
                    chapitres[chapitre].correction;


                card.innerHTML = `

                    <div class="card-icon">
                        ${String(numero).padStart(2, "0")}
                    </div>

                    <div>

                        <h3>
                            Chapitre ${numero}
                        </h3>

                        <p>
                            Cours, TD et correction disponibles.
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


                            ${
                                correction
                                    ? `
                                        <a
                                            class="mini-button"
                                            href="programmes/cours/${correction}"
                                            target="_blank"
                                            rel="noopener"
                                        >
                                            Correction TD →
                                        </a>
                                    `
                                    : ""
                            }

                        </div>

                    </div>

                `;


                container.appendChild(
                    card
                );

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