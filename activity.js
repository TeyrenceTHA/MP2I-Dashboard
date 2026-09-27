// ========================================
// ACTIVITÉ MP2I
// ========================================

const ACTIVITY_KEY = "mp2i-activity";


// ========================================
// DONNÉES
// ========================================

function getActivityData() {

    const saved =
        localStorage.getItem(ACTIVITY_KEY);

    if (saved) {

        try {
            return JSON.parse(saved);
        }

        catch (error) {
            console.error(
                "Erreur données activité :",
                error
            );
        }

    }


    return {
        days: {},
        documents: [],
        totalSeconds: 0
    };

}


let activityData =
    getActivityData();


function saveActivity() {

    localStorage.setItem(
        ACTIVITY_KEY,
        JSON.stringify(activityData)
    );

}


// ========================================
// DATE DU JOUR
// ========================================

function getToday() {

    const now = new Date();

    return (
        now.getFullYear() +
        "-" +
        String(now.getMonth() + 1).padStart(2, "0") +
        "-" +
        String(now.getDate()).padStart(2, "0")
    );

}


// ========================================
// ENREGISTRER UNE ACTIVITÉ
// ========================================

function registerActivity() {

    const today =
        getToday();


    if (!activityData.days[today]) {

        activityData.days[today] = {
            minutes: 0,
            documents: 0
        };

    }


    saveActivity();

}


// ========================================
// DOCUMENT CONSULTÉ
// ========================================

function registerDocument(url) {

    if (!url) return;


    if (
        activityData.documents.includes(url)
    ) {

        registerActivity();

        return;

    }


    activityData.documents.push(url);


    const today =
        getToday();


    if (!activityData.days[today]) {

        activityData.days[today] = {
            minutes: 0,
            documents: 0
        };

    }


    activityData.days[today].documents++;


    saveActivity();

}


// ========================================
// TEMPS DE TRAVAIL
// ========================================

let lastActivityTime =
    Date.now();


function updateWorkTime() {

    if (
        document.visibilityState !==
        "visible"
    ) {
        return;
    }


    const now =
        Date.now();


    const elapsed =
        Math.floor(
            (now - lastActivityTime) / 1000
        );


    // Évite les énormes écarts
    // si l'ordinateur est mis en veille.
    if (
        elapsed > 0 &&
        elapsed <= 90
    ) {

        activityData.totalSeconds +=
            elapsed;


        const today =
            getToday();


        if (!activityData.days[today]) {

            activityData.days[today] = {
                minutes: 0,
                documents: 0
            };

        }


        activityData.days[today].minutes +=
            elapsed / 60;


        saveActivity();

    }


    lastActivityTime =
        now;

}


setInterval(
    updateWorkTime,
    60000
);


document.addEventListener(
    "visibilitychange",
    function() {

        if (
            document.visibilityState ===
            "visible"
        ) {

            lastActivityTime =
                Date.now();

            registerActivity();

        }

        else {

            updateWorkTime();

        }

    }
);


// ========================================
// ACTIVITÉ AU CHARGEMENT
// ========================================

registerActivity();


// ========================================
// DÉTECTER LES DOCUMENTS OUVERTS
// ========================================

document.addEventListener(
    "click",
    function(event) {

        const link =
            event.target.closest("a");

        if (!link) return;


        const href =
            link.href || "";


        const isDocument =
            href.includes(".pdf") ||
            href.includes(
                "notebook.google.com"
            );


        if (isDocument) {

            registerDocument(href);

        }

    }
);


// ========================================
// CALCUL DU STREAK
// ========================================

function calculateStreak() {

    let streak = 0;


    const date =
        new Date();


    while (true) {

        const key =
            date.getFullYear() +
            "-" +
            String(
                date.getMonth() + 1
            ).padStart(2, "0") +
            "-" +
            String(
                date.getDate()
            ).padStart(2, "0");


        const day =
            activityData.days[key];


        if (
            !day ||
            (
                day.minutes <= 0 &&
                day.documents <= 0
            )
        ) {
            break;
        }


        streak++;


        date.setDate(
            date.getDate() - 1
        );

    }


    return streak;

}


// ========================================
// JOURS ACTIFS
// ========================================

function calculateActiveDays() {

    return Object.values(
        activityData.days
    ).filter(day => {

        return (
            day.minutes > 0 ||
            day.documents > 0
        );

    }).length;

}


// ========================================
// TEMPS FORMATÉ
// ========================================

function formatTime(seconds) {

    const hours =
        Math.floor(
            seconds / 3600
        );


    const minutes =
        Math.floor(
            (seconds % 3600) / 60
        );


    if (hours > 0) {

        return (
            hours +
            "h " +
            String(minutes).padStart(2, "0")
        );

    }


    return minutes + " min";

}


// ========================================
// INTENSITÉ D'UNE JOURNÉE
// ========================================

function getIntensity(day) {

    if (!day) return 0;


    const minutes =
        day.minutes || 0;


    const documents =
        day.documents || 0;


    const score =
        minutes +
        documents * 5;


    if (score <= 0) return 0;

    if (score < 15) return 1;

    if (score < 30) return 2;

    if (score < 60) return 3;

    return 4;

}


// ========================================
// HEATMAP
// ========================================

function generateHeatmap() {

    const heatmap =
        document.getElementById(
            "activityHeatmap"
        );


    if (!heatmap) return;


    heatmap.innerHTML = "";


    const today =
        new Date();


    // 365 derniers jours
    const days = [];


    for (
        let i = 364;
        i >= 0;
        i--
    ) {

        const date =
            new Date(today);


        date.setDate(
            today.getDate() - i
        );


        const key =
            date.getFullYear() +
            "-" +
            String(
                date.getMonth() + 1
            ).padStart(2, "0") +
            "-" +
            String(
                date.getDate()
            ).padStart(2, "0");


        days.push({
            date,
            key
        });

    }


    days.forEach(item => {

        const cell =
            document.createElement(
                "div"
            );


        const day =
            activityData.days[
                item.key
            ];


        const intensity =
            getIntensity(day);


        cell.className =
            "activity-cell activity-" +
            intensity;


        const minutes =
            Math.round(
                day?.minutes || 0
            );


        const documents =
            day?.documents || 0;


        cell.title =
            item.key +
            " · " +
            minutes +
            " min · " +
            documents +
            " document" +
            (
                documents > 1
                    ? "s"
                    : ""
            );


        heatmap.appendChild(
            cell
        );

    });

}


// ========================================
// AFFICHAGE DU DASHBOARD
// ========================================

function updateActivityDashboard() {

    const streakElement =
        document.getElementById(
            "activityStreak"
        );


    const documentsElement =
        document.getElementById(
            "activityDocuments"
        );


    const timeElement =
        document.getElementById(
            "activityTime"
        );


    const daysElement =
        document.getElementById(
            "activityDays"
        );


    if (streakElement) {

        streakElement.textContent =
            calculateStreak() +
            " jours";

    }


    if (documentsElement) {

        documentsElement.textContent =
            activityData.documents.length;

    }


    if (timeElement) {

        timeElement.textContent =
            formatTime(
                Math.round(
                    activityData.totalSeconds
                )
            );

    }


    if (daysElement) {

        daysElement.textContent =
            calculateActiveDays();

    }


    generateHeatmap();

}


// ========================================
// MISE À JOUR
// ========================================

updateActivityDashboard();


setInterval(
    updateActivityDashboard,
    60000
);