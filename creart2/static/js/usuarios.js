function buscarUsuario() {

    let input = document.getElementById("buscar");
    let filtro = input.value.toLowerCase();
    let filas = document.querySelectorAll("table tbody tr");

    filas.forEach(fila => {

        let nombre = fila.children[1].textContent.toLowerCase();

        if (nombre.includes(filtro)) {
            fila.style.display = "";
        } else {
            fila.style.display = "none";
        }

    });

}