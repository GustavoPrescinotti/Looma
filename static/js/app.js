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

const symbols = ['(', ')', ' ', '-'];

function formatPhone(v) {
  if (v.length === 0) return '';
  if (v.length <= 2) return '(' + v;
  if (v.length <= 6) return v.replace(/(\d{2})(\d{0,4})/, '($1) $2');
  return v.replace(/(\d{2})(\d{5})(\d{0,4})/, '($1) $2-$3');
}

function handleTelefoneInput(event) {
  const input = event.target;
  let digits = input.value.replace(/\D/g, '');

  if (digits.length > 11) digits = digits.slice(0, 11);

  input.value = formatPhone(digits);
}

function handleTelefoneKeydown(event) {
  const input = event.target;
  const cursorPos = input.selectionStart;
  const value = input.value;

  if (event.key === 'Backspace' && cursorPos > 0) {
    // Se o caractere antes do cursor for símbolo, ajusta o cursor para antes do símbolo
    if (symbols.includes(value[cursorPos - 1])) {
      event.preventDefault();

      // Move o cursor para a posição antes do símbolo
      let newCursor = cursorPos - 1;

      // Remove o dígito anterior ao símbolo
      // Primeiro, pega os dígitos do valor atual
      let digits = value.replace(/\D/g, '');

      // Calcula quantos dígitos há antes do cursor original (ignorando símbolos)
      let digitCountBeforeCursor = 0;
      for (let i = 0, count = 0; i < cursorPos; i++) {
        if (/\d/.test(value[i])) count++;
        digitCountBeforeCursor = count;
      }

      // Remove o dígito anterior ao símbolo (se houver)
      if (digitCountBeforeCursor > 0) {
        digits = digits.slice(0, digitCountBeforeCursor - 1) + digits.slice(digitCountBeforeCursor);
      }

      // Reaplica a máscara
      input.value = formatPhone(digits);

      // Agora calcula a nova posição do cursor
      // Percorre a string formatada para encontrar a posição depois de digitCountBeforeCursor-1 dígitos
      let digitsFound = 0;
      let newPos = 0;
      for (let i = 0; i < input.value.length; i++) {
        if (/\d/.test(input.value[i])) digitsFound++;
        if (digitsFound >= digitCountBeforeCursor - 1) {
          newPos = i + 1;
          break;
        }
      }
      if (digitsFound < digitCountBeforeCursor - 1) {
        newPos = input.value.length;
      }

      input.setSelectionRange(newPos, newPos);
    }
  }

  // Também dá para implementar algo parecido para 'Delete', se quiser
}

const cpfSymbols = ['.', '-'];

function formatCPF(value) {
  const digits = value.replace(/\D/g, '').slice(0, 11); // máximo 11 dígitos
  let formatted = '';

  if (digits.length <= 3) {
    formatted = digits;
  } else if (digits.length <= 6) {
    formatted = digits.slice(0,3) + '.' + digits.slice(3);
  } else if (digits.length <= 9) {
    formatted = digits.slice(0,3) + '.' + digits.slice(3,6) + '.' + digits.slice(6);
  } else {
    formatted = digits.slice(0,3) + '.' + digits.slice(3,6) + '.' + digits.slice(6,9) + '-' + digits.slice(9);
  }
  return formatted;
}

function handleCPFInput(event) {
  const input = event.target;
  const oldValue = input.value;
  const oldCursor = input.selectionStart;

  // Digitos puros
  let digits = oldValue.replace(/\D/g, '').slice(0, 11);

  // Aplica máscara
  let newValue = formatCPF(digits);
  input.value = newValue;

  // Conta quantos símbolos antes do cursor antigo
  let symbolsBeforeCursor = 0;
  for(let i = 0, count = 0; i < oldCursor; i++) {
    if (cpfSymbols.includes(oldValue[i])) count++;
    symbolsBeforeCursor = count;
  }

  // Posição do cursor em termos de dígitos
  const cursorDigitPos = oldCursor - symbolsBeforeCursor;

  // Calcula a nova posição do cursor após formatação
  let digitCount = 0;
  let newCursorPos = 0;
  for(let i = 0; i < newValue.length; i++) {
    if (/\d/.test(newValue[i])) digitCount++;
    if (digitCount >= cursorDigitPos + 1) {
      newCursorPos = i + 1;
      break;
    }
  }
  if (digitCount < cursorDigitPos + 1) {
    newCursorPos = newValue.length;
  }

  input.setSelectionRange(newCursorPos, newCursorPos);
}

function handleCPFKeydown(event) {
  const input = event.target;
  const cursorPos = input.selectionStart;
  const value = input.value;

  if (event.key === 'Backspace' && cursorPos > 0) {
    if (cpfSymbols.includes(value[cursorPos - 1])) {
      event.preventDefault();

      // Move cursor para antes do símbolo
      let newCursor = cursorPos - 1;

      let digits = value.replace(/\D/g, '');

      // Quantidade de dígitos antes do cursor
      let digitCountBeforeCursor = 0;
      for(let i = 0, count=0; i < cursorPos; i++) {
        if (/\d/.test(value[i])) count++;
        digitCountBeforeCursor = count;
      }

      // Remove o dígito antes do símbolo (se houver)
      if (digitCountBeforeCursor > 0) {
        digits = digits.slice(0, digitCountBeforeCursor -1) + digits.slice(digitCountBeforeCursor);
      }

      input.value = formatCPF(digits);

      // Ajusta o cursor
      let digitCount = 0;
      let newCursorPos = 0;
      for(let i = 0; i < input.value.length; i++) {
        if (/\d/.test(input.value[i])) digitCount++;
        if (digitCount >= digitCountBeforeCursor - 1) {
          newCursorPos = i + 1;
          break;
        }
      }
      if (digitCount < digitCountBeforeCursor -1) {
        newCursorPos = input.value.length;
      }

      input.setSelectionRange(newCursorPos, newCursorPos);
    }
  }
}
// Este evento garante que o script só rode depois que a página HTML inteira for carregada
    document.addEventListener('DOMContentLoaded', function() {

        // 1. Pega os elementos do HTML pelos seus IDs
        const termosCheckbox = document.getElementById('termos');
        const promoCheckbox = document.getElementById('promo');
        const loginButton = document.getElementById('btnLogin');

        // 2. Cria uma função para verificar o estado dos checkboxes
        function validarTermos() {
            // A condição é: o botão será desabilitado se a caixa 'termos' NÃO estiver marcada OU a caixa 'promo' NÃO estiver marcada.
            if (termosCheckbox.checked && promoCheckbox.checked) {
                loginButton.disabled = false; // Habilita o botão
            } else {
                loginButton.disabled = true; // Desabilita o botão
            }
        }

        // 3. Executa a função uma vez assim que a página carrega para deixar o botão desabilitado
        validarTermos();

        // 4. Adiciona "escutadores" que chamam a função toda vez que um dos checkboxes é clicado
        termosCheckbox.addEventListener('change', validarTermos);
        promoCheckbox.addEventListener('change', validarTermos);
    });