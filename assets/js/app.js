const btnMenu = document.getElementById('btnMenu');
const menuMobile = document.getElementById('menuMobile');
const btnFechar = document.getElementById('btnFechar');
const header = document.querySelector('.cabecalho-principal');

btnMenu.addEventListener('click', function() {
    menuMobile.classList.add('aberto');
    header.classList.add('menu-aberto');
}); 

btnFechar.addEventListener('click', function() {
    menuMobile.classList.remove('aberto');
    header.classList.remove('menu-aberto');
});


document.querySelectorAll('#menuMobile a').forEach(link => {
    link.addEventListener('click', function() {
        menuMobile.classList.remove('aberto');
        header.classList.remove('menu-aberto');
    });
});