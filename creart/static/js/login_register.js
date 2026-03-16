document.getElementById("btn__iniciar").addEventListener("click", login);

document.getElementById("btn__register").addEventListener("click", register);

//declarando variables 
var contenedor_form = document.querySelector(".contenedor__form");
var formulario_login = document.querySelector(".login");
var formulario_register = document.querySelector(".register");
var caja_trasera_login = document.querySelector(".caja_trasera-login");
var caja_trasera_register = document.querySelector(".caja_trasera-register");

function login(){
	formulario_register.style.display = "none";
	contenedor_form.style.left = "-450px";
	formulario_login.style.display ="block";
	caja_trasera_register.style.opacity = "1";
	caja_trasera_login.style.opacity = "0";
}
	
function register(){
	formulario_register.style.display = "block";
	contenedor_form.style.left = "410px";
	formulario_login.style.display ="none";
	caja_trasera_register.style.opacity = "0";
	caja_trasera_login.style.opacity = "1";
}