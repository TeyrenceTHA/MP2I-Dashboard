const settingsButton = document.getElementById("settingsButton");
const themePanel = document.getElementById("themePanel");

settingsButton.addEventListener("click", function(event) {
    event.preventDefault();
    themePanel.classList.toggle("show");
});


function setTheme(theme) {

    document.body.classList.remove(
        "theme-purple",
        "theme-red",
        "theme-green"
    );

    document.body.classList.add("theme-" + theme);

    localStorage.setItem("theme", theme);
}


const savedTheme = localStorage.getItem("theme");

if (savedTheme) {
    setTheme(savedTheme);
} else {
    setTheme("purple");
}