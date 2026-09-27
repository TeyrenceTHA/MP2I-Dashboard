// ========================================
// ACTIVITÉ MP2I
// ========================================

const ACTIVITY_KEY = "mp2i-activity";


// ========================================
// DONNÉES
// ========================================

function loadActivity() {

    try {

        const saved =
            localStorage.getItem(ACTIVITY_KEY);

        if (saved) {

            const data =
                JSON.parse(saved);

            return {
                days: data.days || {},
                documents: Array.isArray(data.documents)
                    ? data.documents
                    : [],
                totalSeconds:
                    Number(data.totalSeconds) || 0
            };

        }

    } catch (error) {

        console.error(
            "Erreur activité :",
            error
        );

    }


    return {
        days: {},
        documents: [],
        totalSeconds: 0
    };

}


let activityData =
    loadActivity();


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


// ========================================
// JOUR
// ========================================

function getTodayData() {

    const today =
        getDateKey();


    if (!activityData.days[today]) {

        activityData.days[today] = {
            minutes: 0,
            documents: 0
        };

    }


    return activityData.days[today];

}


// ========================================
// SAUVEGARDE
// ========================================

function saveActivity() {

    localStorage.setItem(
        ACTIVITY_KEY,
        JSON.stringify(activityData)
    );

}


// ========================================
// TIMER
// ========================================

let lastTimestamp =
    Date.now();


let timerRunning =
    document.visibilityState === "visible";


function tickTimer() {

    if (!timerRunning) {

        lastTimestamp =
            Date.now();

        return;

    }


    const now =
        Date.now();


    const elapsed =
        (now - lastTimestamp) / 1000;


    /*
     * Protection :
     * on ignore un changement
     * de page extrêmement long.
     */
    if (
        elapsed > 0 &&
        elapsed < 120
    ) {

        activityData.totalSeconds +=
            elapsed;


        const today =
            getTodayData();


        today.minutes +=
            elapsed / 60;

    }


    lastTimestamp =
        now;

}


// ========================================
// VISIBILITÉ
// ========================================

document.addEventListener(
    "visibilitychange",
    () => {

        if (
            document.visibilityState ===
            "visible"
        ) {

            timerRunning = true;

            lastTimestamp =
                Date.now();

        } else {

            tickTimer();

            timerRunning = false;

            saveActivity();

        }

    }
);


// ========================================
// DOCUMENTS
// ========================================

function registerDocument(url) {

    if (!url) return;


    if (
        activityData.documents.includes(url)
    ) {

        return;

    }


    activityData.documents.push(url);


    const today =
        getTodayData();


    today.documents++;


    saveActivity();


    updateDashboard();

}


document.addEventListener(
    "click",
    event => {

        const link =
            event.target.closest("a");


        if (!link) return;


        const href =
            link.href || "";


        if (
            href.toLowerCase().includes(".pdf") ||
            href.includes("notebook.google.com")
        ) {

            registerDocument(href);

        }

    }
);


// ========================================
// STREAK
// ========================================

function calculateStreak() {

    let streak = 0;


    const date =
        new Date();


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
// FORMAT TEMPS
// ========================================

function formatTime(seconds) {

    seconds =
        Math.floor(seconds);


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
// HEATMAP
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


function generateHeatmap() {

    const heatmap =
        document.getElementById(
            "activityHeatmap"
        );


    if (!heatmap) return;


    heatmap.innerHTML = "";


    const today =
        new Date();


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


        const cell =
            document.createElement("div");


        cell.className =
            "activity-cell activity-" +
            getIntensity(day);


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

function updateDashboard() {

    const streak =
        document.getElementById(
            "activityStreak"
        );


    const documents =
        document.getElementById(
            "activityDocuments"
        );


    const time =
        document.getElementById(
            "activityTime"
        );


    const days =
        document.getElementById(
            "activityDays"
        );


    if (streak) {

        streak.textContent =
            calculateStreak() +
            " jours";

    }


    if (documents) {

        documents.textContent =
            activityData.documents.length;

    }


    if (time) {

        time.textContent =
            formatTime(
                activityData.totalSeconds
            );

    }


    if (days) {

        days.textContent =
            calculateActiveDays();

    }


    generateHeatmap();

}


// Alias utilisé après ajout d'un document
function updateActivityDashboard() {

    updateDashboard();

}


// ========================================
// INITIALISATION
// ========================================

getTodayData();

updateDashboard();


// ========================================
// TIMER LIVE
// ========================================

setInterval(() => {

    tickTimer();

    updateDashboard();

}, 1000);


// ========================================
// SAUVEGARDE
// ========================================

setInterval(() => {

    saveActivity();

}, 10000);


window.addEventListener(
    "beforeunload",
    () => {

        tickTimer();

        saveActivity();

    }
);