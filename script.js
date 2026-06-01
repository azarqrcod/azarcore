function setLanguage(lang){

const heroText = document.getElementById("heroText");

if(lang === "en"){

heroText.innerHTML =
"Digital, AI & Creative Solutions for Businesses";

document.querySelector("#services h2").innerHTML = "Services";

document.querySelector("#portfolio h2").innerHTML = "Portfolio";

document.querySelector("#nfc h2").innerHTML = "NFC Solutions";

document.querySelector("#ai h2").innerHTML = "AI Solutions";

document.querySelector("#miniapps h2").innerHTML = "Mini Apps";

document.querySelector("#contact h2").innerHTML = "Contact";

}else{

heroText.innerHTML =
"Digitale, KI- und Kreativlösungen für Unternehmen";

document.querySelector("#services h2").innerHTML = "Dienstleistungen";

document.querySelector("#portfolio h2").innerHTML = "Portfolio";

document.querySelector("#nfc h2").innerHTML = "NFC Lösungen";

document.querySelector("#ai h2").innerHTML = "KI Lösungen";

document.querySelector("#miniapps h2").innerHTML = "Mini Apps";

document.querySelector("#contact h2").innerHTML = "Kontakt";

}

}

window.addEventListener("scroll", () => {

const cards = document.querySelectorAll(".card");

cards.forEach(card => {

const position = card.getBoundingClientRect().top;

const screenPosition = window.innerHeight / 1.2;

if(position < screenPosition){

card.style.opacity = "1";
card.style.transform = "translateY(0px)";

}

});

});
