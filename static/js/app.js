// Menu Mobile
const btnMenu = document.getElementById('btnMenu');
const menuMobile = document.getElementById('menuMobile');
const btnFechar = document.getElementById('btnFechar');
const header = document.querySelector('.cabecalho-principal');

if (btnMenu && menuMobile) {
    btnMenu.addEventListener('click', function () {
        menuMobile.classList.add('aberto');
        if (header) header.classList.add('menu-aberto');
    });
}

if (btnFechar && menuMobile) {
    btnFechar.addEventListener('click', function () {
        menuMobile.classList.remove('aberto');
        if (header) header.classList.remove('menu-aberto');
    });
}




if (menuMobile) {
    document.querySelectorAll('#menuMobile a').forEach(link => {
        link.addEventListener('click', function () {
            menuMobile.classList.remove('aberto');
            if (header) header.classList.remove('menu-aberto');
        });
    });
}

// Validação dos Termos
const termos = document.getElementById('termos');
if (termos) {
    termos.setCustomValidity('Por favor, aceite os termos para continuar.');

    termos.oninput = function () {
        if (termos.validity.valueMissing) {
            termos.setCustomValidity('Por favor, aceite os termos para continuar.');
        } else {
            termos.setCustomValidity('');
        }
    };
}

const promo = document.getElementById('promo');
if (promo) {
    promo.setCustomValidity('Por favor, aceite os termos para continuar.');
    promo.oninput = function () {
        if (promo.validity.valueMissing) {
            promo.setCustomValidity('Por favor, aceite os termos para continuar.');
        } else {
            promo.setCustomValidity('');
        }
    };
}

// Formulário de Empréstimo
const formEmprestimo = document.getElementById('formEmprestimo');
if (formEmprestimo) {
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
}


//Gráfico de Empréstimos
// Espera a página carregar
document.addEventListener('DOMContentLoaded', function() {

    // Função para buscar dados do servidor
    function carregarDados() {
        // Faz requisição para a API
        fetch('/app/admin/emprestimos-por-mes')
            .then(response => response.json()) // Converte resposta para JSON
            .then(dados => {
                // Se deu certo, atualiza o gráfico
                if (dados.success) {
                    atualizarGrafico(dados.emprestimosPorMes);
                }
            })
            .catch(error => {
                console.log('Erro ao carregar dados:', error);
            });
    }

    // Função para atualizar o gráfico
    function atualizarGrafico(dadosMensais) {
        // Nomes dos meses
        const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                      'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];

        // Encontra o maior valor para calcular proporções
        let maiorValor = 0;
        for (let i = 0; i < dadosMensais.length; i++) {
            if (dadosMensais[i] > maiorValor) {
                maiorValor = dadosMensais[i];
            }
        }

        // Altura máxima das barras
        const alturaMaxima = 120;

        // Para cada mês...
        for (let i = 0; i < 12; i++) {
            // Pega a quantidade de empréstimos do mês
            const quantidade = dadosMensais[i] || 0;

            // Calcula altura da barra (proporcional ao maior valor)
            let alturaBarra = 0;
            if (maiorValor > 0) {
                alturaBarra = (quantidade / maiorValor) * alturaMaxima;
            }

            // Encontra a barra no HTML
            const barraElemento = document.querySelector(`.chart-bar:nth-child(${i + 1}) .bar`);
            const valorElemento = document.querySelector(`.chart-bar:nth-child(${i + 1}) .bar-value`);

            // Atualiza a barra
            if (barraElemento) {
                barraElemento.style.height = alturaBarra + 'px';
                barraElemento.style.background = '#395ff9'; // Cor azul
            }

            // Atualiza o número acima da barra
            if (valorElemento) {
                valorElemento.textContent = quantidade;
            }
        }
    }

    // Carrega os dados quando a página abre
    carregarDados();
});



//Contador de Total de Simulações Confirmadas
document.addEventListener('DOMContentLoaded', function() {

    // Função para atualizar o contador de simulações
    function atualizarContadorSimulacoes() {
        // Busca o elemento onde mostra o total de simulações
        const contadorElemento = document.getElementById('total-simulacoes');

        if (contadorElemento) {
            // Pega o valor SALVO no localStorage ou começa com 0
            let valorAtual = parseInt(localStorage.getItem('totalSimulacoes')) || 0;

            // Aumenta o contador em 1
            valorAtual += 1;

            // Atualiza o HTML
            contadorElemento.textContent = valorAtual;

            // Salva o NOVO valor no localStorage
            localStorage.setItem('totalSimulacoes', valorAtual.toString());
        }
    }

    // Função para carregar o contador salvo quando a página abre
    function carregarContadorSimulacoes() {
        const contadorElemento = document.getElementById('total-simulacoes');
        if (contadorElemento) {
            // Pega o valor salvo no localStorage ou usa 0
            const valorSalvo = parseInt(localStorage.getItem('totalSimulacoes')) || 0;
            contadorElemento.textContent = valorSalvo;
        }
    }

    // Encontra o botão de simular na página de simulação
    const botaoSimular = document.querySelector('button[type="submit"]');

    // Se encontrou o botão na página de simulação
    if (botaoSimular && botaoSimular.textContent.includes('Simular')) {
        // Adiciona o evento de clique no botão
        botaoSimular.addEventListener('click', function() {
            // Salva no localStorage que uma simulação foi feita
            localStorage.setItem('simulacaoFeita', 'true');
        });
    }

    // Se está na página do dashboard admin
    const graficoEmprestimos = document.getElementById('graficoEmprestimos');
    if (graficoEmprestimos) {
        // CARREGA o contador salvo quando a página abre
        carregarContadorSimulacoes();

        // Verifica se há simulação salva no localStorage
        if (localStorage.getItem('simulacaoFeita') === 'true') {
            // Atualiza o contador
            atualizarContadorSimulacoes();
            // Remove o marcador do localStorage
            localStorage.removeItem('simulacaoFeita');
        }
    }
});


//Contador de Empréstimos Confirmados
document.addEventListener('DOMContentLoaded', function() {

    // Função para buscar dados do servidor e atualizar contadores
    function carregarDados() {
        // Faz requisição para a API
        fetch('/app/admin/emprestimos-por-mes')
            .then(response => response.json())
            .then(dados => {
                if (dados.success) {
                    atualizarContadores(dados.emprestimosPorMes);
                }
            })
            .catch(error => {
                console.log('Erro ao carregar dados:', error);
            });
    }

    // Função para atualizar os contadores
    function atualizarContadores(dadosMensais) {
        // Calcula o total de empréstimos (soma de todos os meses)
        let totalEmprestimos = 0;
        for (let i = 0; i < dadosMensais.length; i++) {
            totalEmprestimos += dadosMensais[i] || 0;
        }

        // Atualiza o contador de empréstimos no HTML
        const contadorEmprestimos = document.getElementById('total-emprestimos');
        if (contadorEmprestimos) {
            contadorEmprestimos.textContent = totalEmprestimos;
        }

        // Se quiser também calcular total de simulações (opcional)
        const contadorSimulacoes = document.getElementById('total-simulacoes');
        if (contadorSimulacoes) {
            // Aqui você pode colocar a lógica para simulações se tiver os dados
            // Por enquanto vamos deixar 0 ou manter como está
        }
    }

    // Carrega os dados quando a página abre
    carregarDados();
});



    const hoje = new Date().toISOString().split('T')[0];
    const trintaDiasAtras = new Date();
    trintaDiasAtras.setDate(trintaDiasAtras.getDate() - 30);
    const dataInicio = trintaDiasAtras.toISOString().split('T')[0];

    document.getElementById('data_fim').value = hoje;
    document.getElementById('data_inicio').value = dataInicio;