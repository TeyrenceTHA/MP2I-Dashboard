const CACHE_NAME = "mp2i-v2";

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
    "./manifest.json",

    "./programmes/cours/cours.json"
];


self.addEventListener(
    "install",
    event => {

        event.waitUntil(

            caches.open(CACHE_NAME)
                .then(cache => {

                    return cache.addAll(
                        FILES_TO_CACHE
                    );

                })

        );

        self.skipWaiting();

    }
);


self.addEventListener(
    "activate",
    event => {

        event.waitUntil(

            caches.keys()
                .then(keys => {

                    return Promise.all(

                        keys
                            .filter(
                                key =>
                                    key !== CACHE_NAME
                            )
                            .map(
                                key =>
                                    caches.delete(key)
                            )

                    );

                })

        );

        self.clients.claim();

    }
);


self.addEventListener(
    "fetch",
    event => {

        const request =
            event.request;


        /*
         * Pour les pages HTML :
         * toujours essayer le réseau.
         */

        if (
            request.mode === "navigate"
        ) {

            event.respondWith(

                fetch(request)
                    .then(response => {

                        const copy =
                            response.clone();


                        caches.open(
                            CACHE_NAME
                        ).then(cache => {

                            cache.put(
                                request,
                                copy
                            );

                        });


                        return response;

                    })
                    .catch(() => {

                        return caches.match(
                            request
                        );

                    })

            );

            return;

        }


        /*
         * Pour les autres fichiers :
         * cache puis réseau.
         */

        event.respondWith(

            caches.match(request)
                .then(cached => {

                    if (cached) {
                        return cached;
                    }


                    return fetch(request);

                })

        );

    }
);