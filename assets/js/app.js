        // =============================================
        // DECLARAÇÃO DE VARIÁVEIS - SELEÇÃO DE ELEMENTOS
        // =============================================

        // Seleciona o botão que abre o menu mobile pelo seu ID
        const btnMenu = document.getElementById('btnMenu');

        // Seleciona o container do menu mobile pelo seu ID
        const menuMobile = document.getElementById('menuMobile');

        // Seleciona o botão que fecha o menu mobile pelo seu ID
        const btnFechar = document.getElementById('btnFechar');

        // Seleciona o cabeçalho principal usando seletor CSS (classe)
        const header = document.querySelector('.cabecalho-principal');

        // =============================================
        // EVENTO PARA ABRIR O MENU MOBILE
        // =============================================

        // Adiciona um listener de evento de clique no botão de abrir menu
        btnMenu.addEventListener('click', function() {
            // Quando clicado, adiciona a classe 'aberto' ao menu mobile
            // Isso provavelmente torna o menu visível (via CSS)
            menuMobile.classList.add('aberto');
            
            // Adiciona a classe 'menu-aberto' ao cabeçalho
            // Isso pode alterar a aparência do cabeçalho quando o menu está aberto
            header.classList.add('menu-aberto');
        }); 

        // =============================================
        // EVENTO PARA FECHAR O MENU MOBILE
        // =============================================

        // Adiciona um listener de evento de clique no botão de fechar menu
        btnFechar.addEventListener('click', function() {
            // Quando clicado, remove a classe 'aberto' do menu mobile
            // Isso provavelmente esconde o menu (via CSS)
            menuMobile.classList.remove('aberto');
            
            // Remove a classe 'menu-aberto' do cabeçalho
            // Isso restaura a aparência original do cabeçalho
            header.classList.remove('menu-aberto');
        });

        // =============================================
        // EVENTO PARA FECHAR MENU AO CLICAR EM LINKS
        // =============================================

        // Seleciona TODOS os links (<a>) dentro do menu mobile
        document.querySelectorAll('#menuMobile a').forEach(link => {
            // Para cada link encontrado, adiciona um listener de clique
            link.addEventListener('click', function() {
                // Quando um link é clicado, remove a classe 'aberto' do menu
                // Isso fecha o menu automaticamente após a navegação
                menuMobile.classList.remove('aberto');
                
                // Remove a classe 'menu-aberto' do cabeçalho
                // Restaura a aparência original do cabeçalho
                header.classList.remove('menu-aberto');
            });
        });