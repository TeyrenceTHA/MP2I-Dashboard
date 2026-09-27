// ========================================
// ACTIVITÉ MP2I — VERSION OPTIMISÉE
// ========================================

const ACTIVITY_KEY = "mp2i-activity";


// ========================================
// DONNÉES
// ========================================

function createEmptyData() {
    return {
        days: {},
        documents: [],
        totalSeconds: 0
    };
}

function loadActivity() {

    try {

        const saved =
            localStorage.getItem(ACTIVITY_KEY);

        if (!saved) {
            return createEmptyData();
        }

        const data = JSON.parse(saved);

        return {
            days: data.days || {},
            documents: Array.isArray(data.documents)
                ? data.documents
                : [],
            totalSeconds:
                Number(data.totalSeconds) || 0
        };

    } catch (error) {

        console.error(
            "Erreur données activité :",
            error
        );

        return createEmptyData();
    }
}


let activityData = loadActivity();


// ========================================
// SAUVEGARDE
// ========================================

let saveTimeout = null;

function saveActivity() {

    clearTimeout(saveTimeout);

    saveTimeout = setTimeout(() => {

        localStorage.setItem(
            ACTIVITY_KEY,
            JSON.stringify(activityData)
        );

    }, 100);

}


// ========================================
// DATE
// ========================================

function getDateKey(date = new Date()) {

    return (
        date.getFullYear() +
        "-" +
        String(date.getMonth() + 1).padStart(2, "0") +
        "-" +
        String(date.getDate()).padStart(2, "0")
    );

}


function getTodayData() {

    const today = getDateKey();

    if (!activityData.days[today]) {

        activityData.days[today] = {
            minutes: 0,
            documents: 0
        };

    }

    return activityData.days[today];

}


// ========================================
// TIMER
// ========================================

let lastTimestamp = Date.now();

let timerRunning =
    document.visibilityState === "visible";


function updateTimer() {

    if (!timerRunning) {

        lastTimestamp = Date.now();

        return;
    }


    const now = Date.now();

    const elapsed =
        (now - lastTimestamp) / 1000;


    // Protection contre les gros sauts
    if (
        elapsed > 0 &&
        elapsed < 120
    ) {

        activityData.totalSeconds += elapsed;

        const today =
            getTodayData();

        today.minutes +=
            elapsed / 60;

        saveActivity();

    }


    lastTimestamp = now;

}


// Mise à jour toutes les secondes
setInterval(updateTimer, 1000);


// ========================================
// VISIBILITÉ DE L'ONGLET
// ========================================

document.addEventListener(
    "visibilitychange",
    () => {

        if (
            document.visibilityState ===
            "visible"
        ) {

            timerRunning = true;

            lastTimestamp = Date.now();

            getTodayData();

            saveActivity();

        } else {

            updateTimer();

            timerRunning = false;

            saveActivity();

        }

    }
);


// ========================================
// ACTIVITÉ INITIALE
// ========================================

getTodayData();

saveActivity();


// ========================================
// DOCUMENTS
// ========================================

function registerDocument(url) {

    if (!url) return;


    // Déjà enregistré
    if (
        activityData.documents.includes(url)
    ) {

        getTodayData();

        saveActivity();

        return;
    }


    activityData.documents.push(url);


    const today =
        getTodayData();


    today.documents++;


    saveActivity();

    updateActivityDashboard();

}


// Détecte les clics sur les documents
document.addEventListener(
    "click",
    event => {

        const link =
            event.target.closest("a");


        if (!link) return;


        const href =
            link.href || "";


        const isDocument =
            href.toLowerCase().includes(".pdf") ||
            href.includes("notebook.google.com");


        if (isDocument) {

            registerDocument(href);

        }

    }
);


// ========================================
// STREAK
// ========================================

function calculateStreak() {

    let streak = 0;

    const date = new Date();


    while (true) {

        const key =
            getDateKey(date);


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
// FORMATAGE DU TEMPS
// ========================================

function formatTime(seconds) {

    seconds =
        Math.max(
            0,
            Math.floor(seconds)
        );


    const hours =
        Math.floor(
            seconds / 3600
        );


    const minutes =
        Math.floor(
            (seconds % 3600) / 60
        );


    const secs =
        seconds % 60;


    if (hours > 0) {

        return (
            hours +
            "h " +
            String(minutes).padStart(2, "0") +
            " min"
        );

    }


    if (minutes > 0) {

        return (
            minutes +
            " min " +
            String(secs).padStart(2, "0") +
            " s"
        );

    }


    return secs + " s";

}


// ========================================
// INTENSITÉ HEATMAP
// ========================================

function getIntensity(day) {

    if (!day) return 0;


    const minutes =
        Number(day.minutes) || 0;


    const documents =
        Number(day.documents) || 0;


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


    // 365 jours
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
            getDateKey(date);


        const day =
            activityData.days[key];


        const intensity =
            getIntensity(day);


        const cell =
            document.createElement("div");


        cell.className =
            "activity-cell activity-" +
            intensity;


        const minutes =
            Math.floor(
                day?.minutes || 0
            );


        const documents =
            day?.documents || 0;


        cell.title =
            key +
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


        heatmap.appendChild(cell);

    }

}


// ========================================
// DASHBOARD
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
                activityData.totalSeconds
            );

    }


    if (daysElement) {

        daysElement.textContent =
            calculateActiveDays();

    }


    generateHeatmap();

}


// ========================================
// MISE À JOUR LIVE
// ========================================

setInterval(() => {

    updateTimer();

    updateActivityDashboard();

}, 1000);


// Première initialisation
updateActivityDashboard();


// ========================================
// SAUVEGARDE AVANT FERMETURE
// ========================================

window.addEventListener(
    "beforeunload",
    () => {

        updateTimer();

        localStorage.setItem(
            ACTIVITY_KEY,
            JSON.stringify(activityData)
        );

    }
);