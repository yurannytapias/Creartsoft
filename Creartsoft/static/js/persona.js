let precio = 0;
let tiempo = 0;
let pisos = 0;

function actualizar(){

document.getElementById("precio").innerText = precio;
document.getElementById("tiempo").innerText = tiempo;

}

function agregarPiso(){

if(pisos >= 3) return;

pisos++;

let piso = document.createElement("div");
piso.classList.add("piso");

document.getElementById("pastel").appendChild(piso);

precio += 30000;
tiempo += 12;

actualizar();

}

function quitarPiso(){

let pastel = document.getElementById("pastel");

if(pastel.lastChild){

pastel.removeChild(pastel.lastChild);

pisos--;

precio -= 30000;
tiempo -= 12;

actualizar();

}

}

function decorar(tipo){

let pisosPastel = document.querySelectorAll(".piso");

pisosPastel.forEach(p => {

p.classList.remove("flores");
p.classList.remove("chocolate");

p.classList.add(tipo);

});

precio += 8000;
tiempo += 4;

actualizar();

}