const CACHE_NAME = "mp2i-v4";

const FILES_TO_CACHE = [
    "./",
    "./index.html",
    "./kholle.html",
    "./revisions.html",
    "./revoir.html",
    "./maths.html",
    "./physique.html",
    "./info.html",
    "./cours.html",
    "./ds.html",

    "./style.css",
    "./script.js",
    "./activity.js",
    "./cours.js",
    "./manifest.json"
];


self.addEventListener("install", event => {

    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache =>
                cache.addAll(FILES_TO_CACHE)
            )
    );

    self.skipWaiting();

});


self.addEventListener("activate", event => {

    event.waitUntil(

        caches.keys()
            .then(keys =>

                Promise.all(
                    keys
                        .filter(
                            key =>
                                key !== CACHE_NAME
                        )
                        .map(
                            key =>
                                caches.delete(key)
                        )
                )

            )

    );

    self.clients.claim();

});


self.addEventListener("fetch", event => {

    const request =
        event.request;


    /*
     * Les fichiers JS / CSS / JSON
     * doivent toujours essayer le réseau.
     */
    if (
        request.destination === "script" ||
        request.destination === "style" ||
        request.url.includes(".json")
    ) {

        event.respondWith(

            fetch(request)
                .then(response => {

                    const copy =
                        response.clone();

                    caches.open(CACHE_NAME)
                        .then(cache =>
                            cache.put(
                                request,
                                copy
                            )
                        );

                    return response;

                })
                .catch(() =>
                    caches.match(request)
                )

        );

        return;
    }


    /*
     * Pages HTML :
     * réseau en priorité.
     */
    if (
        request.mode === "navigate"
    ) {

        event.respondWith(

            fetch(request)
                .then(response => {

                    const copy =
                        response.clone();

                    caches.open(CACHE_NAME)
                        .then(cache =>
                            cache.put(
                                request,
                                copy
                            )
                        );

                    return response;

                })
                .catch(() =>
                    caches.match(request)
                )

        );

        return;
    }


    event.respondWith(
        caches.match(request)
            .then(cached =>
                cached ||
                fetch(request)
            )
    );

});