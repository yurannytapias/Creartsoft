document.addEventListener("DOMContentLoaded", function() {

    const filas = document.querySelectorAll("table tbody tr");

    filas.forEach(fila => {

        fila.addEventListener("mouseenter", () => {

            fila.style.background = "#f5f5f5";

        });

        fila.addEventListener("mouseleave", () => {

            fila.style.background = "white";

        });

    });

});