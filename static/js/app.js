const btnMenu = document.getElementById('btnMenu');
const menuMobile = document.getElementById('menuMobile');
const btnFechar = document.getElementById('btnFechar');
const header = document.querySelector('.cabecalho-principal');
btnMenu.addEventListener('click', function () {

  menuMobile.classList.add('aberto');


  header.classList.add('menu-aberto');
});

btnFechar.addEventListener('click', function () {

  menuMobile.classList.remove('aberto');


  header.classList.remove('menu-aberto');
});

document.querySelectorAll('#menuMobile a').forEach(link => {

  link.addEventListener('click', function () {

    menuMobile.classList.remove('aberto');


    header.classList.remove('menu-aberto');
  });
});



//JAVA SCRIPT DOS TERMOS

const termos = document.getElementById('termos');
termos.setCustomValidity('Por favor, aceitas os termos para continuar.');

termos.oninput = function () {
  if (termos.validity.valueMissing) {
    termos.setCustomValidity('Por favor, aceitas os termos para continuar.');
  } else {
    termos.setCustomValidity('');
  }
};


const promo = document.getElementById('promo');
promo.setCustomValidity('Por favor, aceitas os termos para continuar.');
promo.oninput = function () {
  if (promo.validity.valueMissing) {
    promo.setCustomValidity('Por favor, aceitas os termos para continuar.');
  }
  else {
    promo.setCustomValidity('');
  }
}
