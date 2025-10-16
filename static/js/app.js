// =============================================
// DECLARAÇÃO DE VARIÁVEIS - SELEÇÃO DE ELEMENTOS
// =============================================

// Seleciona o botão que abre o menu mobile pelo seu ID ('btnMenu').
const btnMenu = document.getElementById('btnMenu');

// Seleciona o container do menu mobile pelo seu ID ('menuMobile').
const menuMobile = document.getElementById('menuMobile');

// Seleciona o botão que fecha o menu mobile pelo seu ID ('btnFechar').
const btnFechar = document.getElementById('btnFechar');

// Seleciona o cabeçalho principal usando seletor CSS pela classe '.cabecalho-principal'.
const header = document.querySelector('.cabecalho-principal');

// =============================================
// EVENTO PARA ABRIR O MENU MOBILE
// =============================================

// Adiciona um listener de evento de clique no botão de abrir menu (btnMenu).
btnMenu.addEventListener('click', function() {
    // Quando clicado, adiciona a classe 'aberto' ao menu mobile.
    // Esta classe (definida via CSS) torna o menu visível, geralmente deslizando-o para a tela.
    menuMobile.classList.add('aberto');
    
    // Adiciona a classe 'menu-aberto' ao cabeçalho.
    // Esta classe pode ser usada no CSS para, por exemplo, mudar a cor do cabeçalho ou ocultar outros elementos.
    header.classList.add('menu-aberto');
}); 

// =============================================
// EVENTO PARA FECHAR O MENU MOBILE
// =============================================

// Adiciona um listener de evento de clique no botão de fechar menu (btnFechar).
btnFechar.addEventListener('click', function() {
    // Quando clicado, remove a classe 'aberto' do menu mobile.
    // Isso o esconde, restaurando a visualização padrão.
    menuMobile.classList.remove('aberto');
    
    // Remove a classe 'menu-aberto' do cabeçalho, restaurando sua aparência original.
    header.classList.remove('menu-aberto');
});

// =============================================
// EVENTO PARA FECHAR MENU AO CLICAR EM LINKS
// =============================================

// Seleciona TODOS os links (<a>) que estão DENTRO do menu mobile (#menuMobile).
document.querySelectorAll('#menuMobile a').forEach(link => {
    // Para cada link encontrado, adiciona um listener de clique.
    link.addEventListener('click', function() {
        // Ao clicar em um link, remove a classe 'aberto' do menu.
        // Isso fecha o menu automaticamente após o usuário selecionar uma página/seção.
        menuMobile.classList.remove('aberto');
        
        // Remove a classe 'menu-aberto' do cabeçalho.
        header.classList.remove('menu-aberto');
    });
});

