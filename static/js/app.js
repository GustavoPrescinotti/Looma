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

// =============================================
// LÓGICA DE VALIDAÇÃO E REDIRECIONAMENTO DE LOGIN
// =============================================

// Garante que o código de login só será executado após o HTML ser completamente carregado e a DOM estar pronta.
// document.addEventListener('DOMContentLoaded', function() {
//     // Seleciona o primeiro formulário encontrado na página.
//     const loginForm = document.querySelector('form');
    
//     // Verifica se um formulário (presumivelmente de login) existe na página atual.
//     if (loginForm) {
//         // Adiciona um listener para interceptar o evento de submissão do formulário.
//         loginForm.addEventListener('submit', function(event) {
//             // Previne o comportamento padrão do navegador (que é recarregar a página ou navegar para 'action').
//             event.preventDefault();
            
//             // Seleciona os campos de input de e-mail e senha pelo ID.
//             const emailInput = document.getElementById('email');
//             const passwordInput = document.getElementById('password');
            
//             // Obtém o valor do e-mail, removendo espaços em branco no início/fim.
//             const email = emailInput.value.trim();
//             // Obtém o valor da senha.
//             const password = passwordInput.value;
            
//             // Validações básicas: verifica se o campo de e-mail está vazio.
//             if (!email) {
//                 alert('Por favor, insira seu email.');
//                 emailInput.focus(); // Coloca o foco de volta no campo de e-mail.
//                 return; // Interrompe a submissão do formulário.
//             }
            
//             // Validações básicas: verifica se o campo de senha está vazio.
//             if (!password) {
//                 alert('Por favor, insira sua senha.');
//                 passwordInput.focus(); // Coloca o foco de volta no campo de senha.
//                 return; // Interrompe a submissão do formulário.
//             }
            
//             // Verifica o tipo de usuário baseado no e-mail.
//             // A lógica é baseada na presença da substring '.admin@' no campo de e-mail.
//             if (email.includes('.admin@')) {
//                 console.log('Acesso de administrador detectado');
//                 // Redireciona o usuário para o dashboard do administrador.
//                 window.location.href = 'dashboard_admin.html';
//             } else {
//                 console.log('Acesso de empresário detectado');
//                 // Para qualquer outro e-mail, redireciona para o dashboard do empresário (usuário padrão).
//                 // Nota: O arquivo original aponta para 'dashboard_empresario.html', mas no repositório temos 'dashboard_usuario.html'
//                 // Mantendo o destino original baseado na lógica fornecida.
//                 window.location.href = 'dashboard_empresario.html'; 
//             }
//         });
//     }
// });