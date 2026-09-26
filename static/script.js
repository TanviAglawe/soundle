document.addEventListener("DOMContentLoaded", function () {

    const input = document.getElementById("artistInput");
    const suggestions = document.getElementById("suggestions");

    if (!input || !suggestions) {
        return;
    }


    let artists = [];


    // Get artists from Flask
    fetch("/artists")
        .then(function (response) {

            if (!response.ok) {
                throw new Error("Artist API failed");
            }

            return response.json();

        })
        .then(function (data) {

            artists = data;

            console.log("Artists loaded:", artists);

        })
        .catch(function (error) {

            console.error(
                "Could not load artists:",
                error
            );

        });


    input.addEventListener("input", function () {

        const text =
            input.value.trim().toLowerCase();


        suggestions.innerHTML = "";


        if (text.length === 0) {

            suggestions.style.display = "none";

            return;

        }


        const matches = artists
            .filter(function (artist) {

                return artist
                    .toLowerCase()
                    .includes(text);

            })
            .slice(0, 6);


        if (matches.length === 0) {

            suggestions.style.display = "none";

            return;

        }


        matches.forEach(function (artist) {

            const option =
                document.createElement("div");


            option.className =
                "suggestion-item";


            option.textContent =
                artist;


            option.addEventListener(
                "click",
                function () {

                    input.value = artist;

                    suggestions.innerHTML = "";

                    suggestions.style.display =
                        "none";

                }
            );


            suggestions.appendChild(option);

        });


        suggestions.style.display = "block";

    });


    // Close dropdown when clicking elsewhere
    document.addEventListener(
        "click",
        function (event) {

            if (
                event.target !== input &&
                !suggestions.contains(event.target)
            ) {

                suggestions.innerHTML = "";

                suggestions.style.display =
                    "none";

            }

        }
    );

});