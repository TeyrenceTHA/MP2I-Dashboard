// ========================================
// ACTIVITÉ MP2I
// ========================================

const ACTIVITY_KEY = "mp2i-activity";


// ========================================
// CHARGEMENT
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
                documents:
                    Array.isArray(data.documents)
                        ? data.documents
                        : [],
                totalSeconds:
                    Number(data.totalSeconds) || 0,
                lastActive:
                    Number(data.lastActive) || Date.now()
            };

        }

    } catch (error) {

        console.error(error);

    }


    return {
        days: {},
        documents: [],
        totalSeconds: 0,
        lastActive: Date.now()
    };

}


let activity =
    loadActivity();


// ========================================
// SAUVEGARDE
// ========================================

function save() {

    localStorage.setItem(
        ACTIVITY_KEY,
        JSON.stringify(activity)
    );

}


// ========================================
// DATE
// ========================================

function dateKey(date = new Date()) {

    return (
        date.getFullYear() +
        "-" +
        String(
            date.getMonth() + 1
        ).padStart(2, "0") +
        "-" +
        String(
            date.getDate()
        ).padStart(2, "0")
    );

}


// ========================================
// JOUR
// ========================================

function today() {

    const key =
        dateKey();


    if (!activity.days[key]) {

        activity.days[key] = {
            minutes: 0,
            documents: 0
        };

    }


    return activity.days[key];

}


// ========================================
// TIMER
// ========================================

let lastTick =
    Date.now();


let running = true;


/*
 * Au chargement d'une nouvelle page,
 * on repart du timestamp sauvegardé.
 */
activity.lastActive =
    Date.now();


function tick() {

    if (!running) return;


    const now =
        Date.now();


    const elapsed =
        (now - lastTick) / 1000;


    if (
        elapsed > 0 &&
        elapsed < 10
    ) {

        activity.totalSeconds +=
            elapsed;


        today().minutes +=
            elapsed / 60;

    }


    lastTick =
        now;

}


// ========================================
// TIMER LIVE
// ========================================

setInterval(() => {

    tick();

    activity.lastActive =
        Date.now();

    save();

    updateDashboard();

}, 1000);


// ========================================
// CHANGEMENT D'ONGLET
// ========================================

document.addEventListener(
    "visibilitychange",
    () => {

        if (
            document.visibilityState ===
            "visible"
        ) {

            running = true;

            lastTick =
                Date.now();

        } else {

            tick();

            running = false;

            activity.lastActive =
                Date.now();

            save();

        }

    }
);


// ========================================
// DOCUMENTS
// ========================================

function registerDocument(url) {

    if (!url) return;


    if (
        activity.documents.includes(url)
    ) {

        return;

    }


    activity.documents.push(url);


    today().documents++;


    save();

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
            href.toLowerCase()
                .includes(".pdf") ||
            href.includes(
                "notebook.google.com"
            )
        ) {

            registerDocument(href);

        }

    }
);


// ========================================
// STREAK
// ========================================

function streak() {

    let count = 0;

    const date =
        new Date();


    while (true) {

        const day =
            activity.days[
                dateKey(date)
            ];


        if (
            !day ||
            (
                day.minutes <= 0 &&
                day.documents <= 0
            )
        ) {

            break;

        }


        count++;


        date.setDate(
            date.getDate() - 1
        );

    }


    return count;

}


// ========================================
// JOURS ACTIFS
// ========================================

function activeDays() {

    return Object.values(
        activity.days
    ).filter(day =>
        day.minutes > 0 ||
        day.documents > 0
    ).length;

}


// ========================================
// FORMAT TEMPS
// ========================================

function formatTime(seconds) {

    seconds =
        Math.floor(seconds);


    const h =
        Math.floor(
            seconds / 3600
        );


    const m =
        Math.floor(
            (seconds % 3600) / 60
        );


    const s =
        seconds % 60;


    if (h > 0) {

        return (
            h +
            "h " +
            String(m).padStart(2, "0") +
            " min"
        );

    }


    if (m > 0) {

        return (
            m +
            " min " +
            String(s).padStart(2, "0") +
            " s"
        );

    }


    return s + " s";

}


// ========================================
// HEATMAP
// ========================================

function intensity(day) {

    if (!day) return 0;


    const score =
        (day.minutes || 0) +
        (day.documents || 0) * 5;


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


    const now =
        new Date();


    for (
        let i = 364;
        i >= 0;
        i--
    ) {

        const date =
            new Date(now);


        date.setDate(
            now.getDate() - i
        );


        const key =
            dateKey(date);


        const day =
            activity.days[key];


        const cell =
            document.createElement("div");


        cell.className =
            "activity-cell activity-" +
            intensity(day);


        cell.title =
            key +
            " · " +
            Math.floor(
                day?.minutes || 0
            ) +
            " min · " +
            (day?.documents || 0) +
            " document(s)";


        heatmap.appendChild(cell);

    }

}


// ========================================
// DASHBOARD
// ========================================

function updateDashboard() {

    const streakEl =
        document.getElementById(
            "activityStreak"
        );


    const documentsEl =
        document.getElementById(
            "activityDocuments"
        );


    const timeEl =
        document.getElementById(
            "activityTime"
        );


    const daysEl =
        document.getElementById(
            "activityDays"
        );


    if (streakEl) {

        streakEl.textContent =
            streak() + " jours";

    }


    if (documentsEl) {

        documentsEl.textContent =
            activity.documents.length;

    }


    if (timeEl) {

        timeEl.textContent =
            formatTime(
                activity.totalSeconds
            );

    }


    if (daysEl) {

        daysEl.textContent =
            activeDays();

    }


    generateHeatmap();

}


// ========================================
// INITIALISATION
// ========================================

today();

updateDashboard();

save();


// ========================================
// AVANT DE QUITTER
// ========================================

window.addEventListener(
    "pagehide",
    () => {

        tick();

        activity.lastActive =
            Date.now();

        save();

    }
);