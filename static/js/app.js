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

const formEmprestimo = document.getElementById('formEmprestimo');

formEmprestimo.addEventListener('submit', function (e) {
    e.preventDefault();

    const valor = parseFloat(document.getElementById('valor').value);
    const ano = parseInt(document.getElementById('ano').value);
    const parcelas = parseInt(document.getElementById('prazo').value);
    const taxa = 0.05;

    if (isNaN(valor) || isNaN(parcelas) || isNaN(ano) || valor <= 0 || parcelas <= 0) {
        alert('Por favor, preencha os campos corretamente.');
        return;
    }

    const total = valor * Math.pow(1 + taxa, parcelas);
    const parcela = total / parcelas;

    const confirmMsg = `
    Valor: R$ ${valor.toFixed(2)}
    Ano: ${ano}
    Parcelas: ${parcelas}
    Valor da parcela: R$ ${parcela.toFixed(2)}
    Total: R$ ${total.toFixed(2)}

Deseja confirmar a simulação?`;

    if (confirm(confirmMsg)) {
        alert('Simulação confirmada!');
        // Aqui você pode submeter o formulário ou fazer outra ação
    }
});