# Importa classes e funções do Flask para criar a app, renderizar templates, redirecionar, usar sessões, etc.
from flask import Flask, render_template, redirect, session, url_for, request, flash
# Importa funções do Flask-Bcrypt para gerar e verificar hashes de senhas.
from flask_bcrypt import generate_password_hash, check_password_hash
# Importa a classe date do módulo datetime para trabalhar com datas.
from datetime import datetime, date
# Importa a biblioteca fdb para conectar com o banco de dados Firebird.
import fdb

# Cria uma instância da aplicação Flask, usando o nome do módulo atual.
app = Flask(__name__)

# Define uma chave secreta para a aplicação, usada para assinar cookies de sessão.
# IMPORTANTE: Em produção, use uma chave mais complexa e armazenada em variável de ambiente
app.secret_key = 'IgorELaisMeDeemNota'

# Define o endereço do servidor do banco de dados.
host = 'localhost'
# Define o caminho para o arquivo do banco de dados Firebird.
database = r'C:\Users\Aluno\Desktop\Looma-31-10-2025\Looma.FDB'
# Define o nome de usuário para a conexão com o banco de dados.
user = 'sysdba'
# Define a senha para a conexão com o banco de dados.
password = 'sysdba'

# Conecta-se ao banco de dados Firebird usando as configurações definidas.
con = fdb.connect(host=host, database=database, user=user, password=password)

# Define uma função chamada verificar_senha_forte que recebe uma senha como argumento.

# Função para criar o usuário admin fixo (execute uma vez)
def criar_admin_fixo():
    cursor = con.cursor()
    try:
        # Verifica se o admin já existe
        cursor.execute("SELECT id_usuario FROM usuario WHERE email = ?", ('adm.looma@gmail.com',))
        admin_existente = cursor.fetchone()

        if not admin_existente:
            # Cria o hash da senha
            hash_senha = generate_password_hash('M8#$%oA123456789ert').decode('utf-8')

            # Insere o usuário admin
            cursor.execute(
                "INSERT INTO usuario (email, nome, senha, cpf, telefone, tipo, tentativas, ativo) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                ('adm.looma@gmail.com', 'Administrador Looma', hash_senha, '000.000.000-00', '(00) 00000-0000', 'admin',
                 0, True)
            )
            con.commit()
            print("Admin criado com sucesso!")
        else:
            print("Admin já existe!")
    except Exception as e:
        print(f"Erro ao criar admin: {e}")
    finally:
        cursor.close()

# Chame esta função uma vez para criar o admin
# criar_admin_fixo()
def verificar_senha_forte(senha):
    # Verifica se o comprimento da senha é menor que 8 caracteres.
    if len(senha) < 8:
        # Se for menor que 8, retorna False, indicando que a senha não é forte.
        return False

    # Inicializa a variável para verificar se há letra maiúscula como False.
    tem_maiuscula = False
    # Inicializa a variável para verificar se há letra minúscula como False.
    tem_minuscula = False
    # Inicializa a variável para verificar se há número como False.
    tem_numero = False
    # Inicializa a variável para verificar se há caractere especial como False.
    tem_especial = False
    # Define uma string com os caracteres especiais permitidos.
    caracteres_especiais = "!@#$%^&*()_-+=<>?/.,;:"

    # Inicia um loop para percorrer cada caractere na string da senha.
    for char in senha:
        # Verifica se o caractere atual é uma letra maiúscula.
        if char.isupper():
            # Se for maiúscula, define a variável tem_maiuscula como True.
            tem_maiuscula = True
        # Se não for maiúscula, verifica se é uma letra minúscula.
        elif char.islower():
            # Se for minúscula, define a variável tem_minuscula como True.
            tem_minuscula = True
        # Se não for letra, verifica se é um dígito numérico.
        elif char.isdigit():
            # Se for um número, define a variável tem_numero como True.
            tem_numero = True
        # Se não for nenhum dos anteriores, verifica se está na lista de caracteres especiais.
        elif char in caracteres_especiais:
            # Se for um caractere especial, define a variável tem_especial como True.
            tem_especial = True

    # Verifica se todas as quatro condições (maiúscula, minúscula, número, especial) são verdadeiras.
    if tem_maiuscula and tem_minuscula and tem_numero and tem_especial:
        # Se todas forem verdadeiras, retorna True, indicando que a senha é forte.
        return True
    # Se alguma das condições não for atendida, retorna False.
    return False

# Define um decorador que associa a URL raiz ('/') à função 'index'.
@app.route('/')
# Define a função 'index' que será executada quando a URL raiz for acessada.
def index():
    # Retorna o conteúdo do arquivo 'index.html' renderizado para o navegador.
    return render_template('index.html')


# Define um decorador para a URL '/auth/login', aceitando os métodos GET e POST.
@app.route('/auth/login', methods=['GET', 'POST'])
# Define a função 'login' que lida com a autenticação do usuário.
def login():
    # Verifica se a chave 'usuario' existe na sessão atual.
    if 'usuario' in session:
        # Se o usuário já estiver logado, redireciona para a página do dashboard.
        return redirect(url_for('dashboard'))

    # Verifica se o método da requisição HTTP é GET.
    if request.method == 'GET':
        # Se for GET, renderiza e exibe a página de login.
        return render_template('login.html')

    # Cria um objeto cursor para interagir com o banco de dados.
    cursor = con.cursor()

    # Inicia um bloco try para tratamento de exceções durante o processo de login.
    try:
        # Pega o valor do campo 'email' enviado pelo formulário.
        email = request.form['email']
        # Pega o valor do campo 'password' enviado pelo formulário.
        senha = request.form['password']

        # Executa uma consulta SQL para selecionar um usuário pelo email.
        cursor.execute(
            # A consulta SQL a ser executada.
            "SELECT id_usuario, nome, email, senha, tipo, tentativas, cpf, ativo, telefone FROM usuario WHERE email = ?",
            # Passa o email como um parâmetro para a consulta, evitando injeção de SQL.
            (email,))
        # Busca a primeira linha do resultado da consulta.
        usuario = cursor.fetchone()

        # Verifica se a consulta não retornou nenhum usuário.
        if not usuario:
            # Exibe uma mensagem de erro para o usuário.
            flash("Email ou senha incorretos. Por favor, tente novamente.", "error")
            # Redireciona de volta para a página de login.
            return redirect(url_for('login'))

        # Extrai o tipo de usuário (ex: 'admin', 'user') do resultado da consulta.
        tipo = usuario[4]
        # Extrai o número de tentativas de login do resultado da consulta.
        tentativas = usuario[5]
        # Extrai o status da conta (ativo/inativo) do resultado da consulta.
        ativo = usuario[7]

        # Verifica se a conta do usuário não está ativa.
        if not ativo:
            # Exibe uma mensagem informando que a conta está bloqueada.
            flash("Sua conta foi bloqueada devido a múltiplas tentativas de login. Entre em contato com o suporte.",
                  # Define a categoria da mensagem como 'error'.
                  "error")
            # Redireciona de volta para a página de login.
            return redirect(url_for('login'))

        # Compara a senha fornecida com o hash armazenado no banco de dados.
        if check_password_hash(usuario[3], senha):
            # check_password_hash :
            # Senha correta: cria a sessão do usuário

            # Inicia um bloco try para a atualização das tentativas.
            try:
                # Atualiza o número de tentativas para 0 no banco de dados.
                cursor.execute("UPDATE USUARIO SET TENTATIVAS = ? WHERE id_usuario = ?", (0, usuario[0]))
                # Confirma a transação, salvando a alteração no banco.
                con.commit()
            # Captura qualquer exceção que ocorra durante a atualização.
            except Exception as e:
                # Exibe uma mensagem de erro caso a atualização falhe.
                flash("Não foi possível atualizar o usuário.", "error")

            # Armazena os dados do usuário na sessão, efetivando o login.
            session['usuario'] = usuario
            # Exibe uma mensagem de sucesso para o usuário.
            flash("Login realizado com sucesso! Bem-vindo(a)!", "success")
            # Redireciona o usuário para a página do dashboard.
            return redirect(url_for('dashboard'))
        # Se a senha estiver incorreta.
        else:
            # Senha incorreta: incrementa o contador de tentativas
            # Exibe uma mensagem de erro de credenciais inválidas.
            flash("Email ou senha incorretos. Por favor, tente novamente.", "error")

            # Apenas usuários comuns têm limite de tentativas
            # Verifica se o tipo do usuário é 'user'.
            if tipo == 'user':
                # Incrementa o contador de tentativas de login.
                tentativas = tentativas + 1

                # Se atingiu 3 tentativas, bloqueia a conta
                # Inicia um bloco try para atualizar as tentativas e o status da conta.
                try:
                    # Executa um comando SQL para atualizar as tentativas e o status.
                    cursor.execute("UPDATE USUARIO SET TENTATIVAS = ?, ATIVO = ? WHERE ID_USUARIO = ?",
                                   # Passa os novos valores para a consulta (ativa a conta se tentativas < 3).
                                   (tentativas, (True if tentativas < 3 else False), usuario[0]))
                    # Confirma a transação no banco de dados.
                    con.commit()

                    # Se a conta foi bloqueada, informa o usuário
                    # Verifica se o número de tentativas atingiu ou ultrapassou 3.
                    if tentativas >= 3:
                        # Exibe uma mensagem informando o bloqueio da conta.
                        flash("Sua conta foi bloqueada devido a múltiplas tentativas de login incorretas.", "error")
                # Captura qualquer exceção durante a atualização.
                except Exception as e:
                    # Exibe uma mensagem de erro genérica.
                    flash("Erro ao processar tentativa de login.", "error")
                # Bloco que é executado independentemente de ter ocorrido erro ou não.
                finally:
                    # Fecha o cursor para liberar recursos.
                    cursor.close()
    # Captura qualquer exceção que possa ocorrer no bloco try principal.
    except Exception as e:
        # Captura qualquer erro durante o processo de login
        # Exibe uma mensagem de erro genérica para o usuário.
        flash("Houve um erro ao fazer login. Por favor, tente novamente.", "error")
    # Bloco que é executado sempre, com ou sem erro.
    finally:
        # Garante que o cursor seja fechado para liberar recursos do banco de dados.
        cursor.close()

    # Redireciona o usuário de volta para a página de login em caso de falha.
    return redirect(url_for('login'))
# Define a rota '/auth/cadastro' que aceita métodos GET e POST.
@app.route('/auth/cadastro', methods=['GET', 'POST'])
# Define a função 'cadastro' para registrar novos usuários.
def cadastro():
    # Verifica se já existe um usuário na sessão.
    if 'usuario' in session:
        # Se sim, redireciona para o dashboard.
        return redirect(url_for('dashboard'))

    # Verifica se o método da requisição é GET.
    if request.method == 'GET':
        # Se for GET, exibe a página de cadastro.
        return render_template('cadastro.html')

    # Cria um novo cursor para interagir com o banco de dados.
    cursor = con.cursor()

    # Inicia um bloco try para tratamento de erros durante o cadastro.
    try:
        # Obtém o email do formulário de cadastro.
        email = request.form['email']
        # Obtém o nome do formulário de cadastro.
        nome = request.form['name']
        # Obtém a senha do formulário de cadastro.
        senha = request.form['password']
        # Obtém o CPF do formulário de cadastro.
        cpf = request.form['cpf']
        # Obtém o telefone do formulário de cadastro.
        telefone = request.form['phone']
        # Obtém a confirmação da senha do formulário.
        confirmar_senha = request.form['confirm_password']

        # Chama a função para verificar se a senha atende aos critérios de segurança.
        if not verificar_senha_forte(senha):
            # Exibe uma mensagem de erro se a senha for fraca.
            flash(
                # Texto da mensagem de erro.
                "A senha deve ter pelo menos 8 caracteres, uma letra maiúscula, uma letra minúscula, um número e um caractere especial.",
                # Categoria da mensagem.
                "error")
            # Redireciona de volta para a página de cadastro.
            return redirect(url_for('cadastro'))

        # Verifica se a senha e a confirmação de senha são diferentes.
        if senha != confirmar_senha:
            # Exibe uma mensagem de erro se as senhas não coincidirem.
            flash("As senhas não coincidem. Por favor, tente novamente.", "error")
            # Redireciona de volta para a página de cadastro.
            return redirect(url_for('cadastro'))

        # Executa uma consulta para verificar se o email já existe.
        cursor.execute("SELECT id_usuario FROM usuario WHERE email = ?", (email,))
        # Busca o resultado da consulta.
        usuario = cursor.fetchone()
        # fetchone: usar fetchone() porque só deve existir um usuário com aquele e-mail.
        # fetchall : Ele vai buscar todos os usuarios
        # Se a consulta retornou um usuário (ou seja, o email já existe).
        if usuario:
            # Exibe uma mensagem de erro.
            flash("Este email já está cadastrado. Por favor, use outro email ou faça login.", "error")
            # Fecha o cursor.
            cursor.close()
            # Redireciona de volta para a página de cadastro.
            return redirect(url_for('cadastro'))

        # Gera um hash seguro da senha e o decodifica para string UTF-8.
        hash_senha = generate_password_hash(senha).decode('utf-8')

        # Executa um comando SQL para inserir o novo usuário na tabela.
        cursor.execute(
            # A instrução SQL de inserção.
            "INSERT INTO usuario(email, nome, senha, cpf, telefone, tipo, tentativas, ativo) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            # Passa os dados do novo usuário como parâmetros para a inserção.
            (email, nome, hash_senha, cpf, telefone, 'user', 0, True))
        # Confirma a transação, salvando o novo usuário no banco de dados.
        con.commit()

        # Exibe uma mensagem de sucesso para o usuário.
        flash("Cadastro realizado com sucesso! Faça login para continuar.", "success")
    # Captura qualquer exceção que ocorra durante o processo.
    except Exception as e:
        # Captura qualquer erro durante o cadastro
        # Exibe uma mensagem de erro genérica.
        flash("Não foi possível criar sua conta. Por favor, tente novamente.", "error")
        # Redireciona de volta para a página de cadastro.
        return redirect(url_for('cadastro'))
    # Bloco que sempre será executado.
    finally:
        # Garante que o cursor seja fechado.
        cursor.close()

    # Redireciona para a página de login após o cadastro bem-sucedido.
    return redirect(url_for('login'))


# Define a rota para '/app'.
# Define a rota para '/app'.
@app.route('/app')
def dashboard():
    if 'usuario' not in session:
        flash("Você precisa fazer login para acessar esta página.", "error")
        return redirect(url_for('login'))

    cursor = con.cursor()
    try:
        if session['usuario'][4] == 'admin':
            cursor.execute("SELECT COUNT(*) FROM usuario WHERE ativo = ?", (1,))
            usuariosAtivos = cursor.fetchone()
            total_usuarios_ativos = usuariosAtivos[0] if usuariosAtivos else 0
            return render_template('dashboard_admin.html', total_usuarios=total_usuarios_ativos)
        else:
            id_usuario = session['usuario'][0]

            # Buscar transações (SEM incluir parcelas de empréstimos duplicadas)
            cursor.execute("""
                SELECT TIPO, VALOR, DESCRICAO
                FROM TRANSACOES
                WHERE ID_USUARIO = ?
                ORDER BY DATA_TRANSACAO DESC
            """, (id_usuario,))
            transacoes = cursor.fetchall()

            total_receitas = 0.0
            total_despesas = 0.0

            for transacao in transacoes:
                tipo = transacao[0]
                valor = float(transacao[1])
                # Não somar parcelas de empréstimo aqui, vamos calcular separadamente
                if 'parcela de empréstimo' not in transacao[2].lower():
                    if tipo.lower() == 'receita':
                        total_receitas += valor
                    elif tipo.lower() == 'despesa':
                        total_despesas += valor

            # Buscar TODOS os empréstimos ativos do usuário
            cursor.execute("""
                SELECT ID_EMPRESTIMO, VALOR_EMPRESTIMO, PARCELAS_RESTANTES, 
                       PROXIMO_VENCIMENTO, PARCELA_MENSAL, DATA_CONTRATACAO
                FROM EMPRESTIMOS 
                WHERE ID_USUARIO = ? AND STATUS = 'ativo'
                ORDER BY DATA_CONTRATACAO DESC
            """, (id_usuario,))
            emprestimos_data = cursor.fetchall()

            # Calcular totais dos empréstimos
            valor_total_emprestimos = 0.0
            soma_parcelas_mensais = 0.0
            total_a_pagar = 0.0
            emprestimos_lista = []

            for emprestimo in emprestimos_data:
                id_emprestimo = emprestimo[0]
                valor_emprestimo = float(emprestimo[1])
                parcelas_restantes = int(emprestimo[2])
                parcela_mensal = float(emprestimo[4])
                data_contratacao = emprestimo[5]

                valor_total_emprestimos += valor_emprestimo
                soma_parcelas_mensais += parcela_mensal
                total_a_pagar += parcela_mensal * parcelas_restantes

                # CORREÇÃO: Tratar data_contratacao quando for None
                if data_contratacao:
                    if isinstance(data_contratacao, str):
                        data_contratacao_obj = datetime.strptime(data_contratacao.split()[0], '%Y-%m-%d')
                    else:
                        data_contratacao_obj = data_contratacao
                    data_contratacao_formatada = data_contratacao_obj.strftime('%d/%m/%Y')
                else:
                    data_contratacao_formatada = "Não informada"

                # Formatar próximo vencimento
                proximo_vencimento = emprestimo[3]
                if proximo_vencimento:
                    if isinstance(proximo_vencimento, str):
                        vencimento_obj = datetime.strptime(proximo_vencimento.split()[0], '%Y-%m-%d')
                    else:
                        vencimento_obj = proximo_vencimento
                    proximo_vencimento_formatado = vencimento_obj.strftime('%d/%m/%Y')
                else:
                    proximo_vencimento_formatado = "Não definido"

                # Adicionar à lista de empréstimos individuais
                emprestimos_lista.append({
                    'id': id_emprestimo,
                    'valor_emprestimo': valor_emprestimo,
                    'parcelas_restantes': parcelas_restantes,
                    'proximo_vencimento': proximo_vencimento_formatado,
                    'parcela_mensal': parcela_mensal,
                    'total_a_pagar': parcela_mensal * parcelas_restantes,
                    'data_contratacao': data_contratacao_formatada
                })

            # AGORA adicionar APENAS as parcelas mensais às despesas
            total_despesas_com_parcelas = total_despesas + soma_parcelas_mensais

            # Calcular renda líquida COM as parcelas
            renda_liquida = total_receitas - total_despesas_com_parcelas

            # O limite é 30% da renda líquida SEM as parcelas de empréstimo
            limite_emprestimo = (total_receitas - total_despesas_com_parcelas) * 0.3
            if limite_emprestimo < 0:
                limite_emprestimo = 0

            emprestimos = {
                'valor_total': valor_total_emprestimos,
                'total_a_pagar': total_a_pagar,
                'parcelas_restantes': sum(e['parcelas_restantes'] for e in emprestimos_lista),
                'lista_emprestimos': emprestimos_lista
            }

            return render_template('dashboard_usuario.html',
                                   total_receitas=total_receitas,
                                   total_despesas=total_despesas_com_parcelas,
                                   renda_liquida=renda_liquida,
                                   limite_emprestimo=limite_emprestimo,
                                   emprestimos=emprestimos)
    except Exception as e:
        flash(f"Erro ao carregar dashboard: {e}", "error")
        emprestimos = {
            'valor_total': 0.0,
            'total_a_pagar': 0.0,
            'parcelas_restantes': 0,
            'lista_emprestimos': []
        }
        return render_template('dashboard_usuario.html',
                               total_receitas=0,
                               total_despesas=0,
                               renda_liquida=0,
                               limite_emprestimo=0,
                               emprestimos=emprestimos)
    finally:
        cursor.close()
# Define a rota para '/logout'.
@app.route('/logout')
# Define a função 'logout' para encerrar a sessão do usuário.
def logout():
    # Remove o usuário da sessão
    # Verifica se existe um usuário na sessão.
    if 'usuario' in session:
        # Remove a chave 'usuario' da sessão, efetivamente deslogando o usuário.
        session.pop("usuario", None)
        # Exibe uma mensagem de sucesso.
        flash("Logout realizado com sucesso!", "success")

    # Redireciona o usuário para a página de login.
    return redirect(url_for('login'))


# ROTAS ADMINISTRATIVAS - Apenas para usuários com perfil 'admin'


# Define a rota para criar taxas, aceitando métodos GET e POST.
@app.route('/app/taxas/criar', methods=['GET', 'POST'])
def nova_taxa():
    if 'usuario' not in session:
        flash("Você precisa fazer login para acessar esta página.", "error")
        return redirect(url_for('login'))

    if session['usuario'][4] != 'admin':
        flash("Acesso negado. Apenas administradores podem acessar esta página.", "error")
        return redirect(url_for('dashboard'))

    if request.method == 'GET':
        ano_atual = datetime.now().year
        return render_template('nova_taxa.html', ano_atual=ano_atual)

    cursor = con.cursor()

    try:
        ano = request.form['ano']
        valor = request.form['taxa']
        data = date.today()  # Esta é a data que será registrada para a taxa
        id_usuario = session['usuario'][0]

        # CORREÇÃO: Verificar se já existe uma taxa para esta data específica
        cursor.execute('SELECT COUNT(*) FROM TAXA_JURO WHERE DATA_CRIACAO = ?', (data,))
        taxa_existente = cursor.fetchone()[0]

        if taxa_existente > 0:
            flash(f"Já existe uma taxa registrada para a data {data.strftime('%d/%m/%Y')}. Cada data deve ter apenas uma taxa.", "error")
            return redirect(url_for('nova_taxa'))

        # Validação: Verificar se o ano é válido
        ano_atual = datetime.now().year
        try:
            ano_int = int(ano)
            if ano_int != ano_atual:
                flash(f"O ano deve ser {ano_atual}.", "error")
                return redirect(url_for('nova_taxa'))
        except ValueError:
            flash("Ano inválido.", "error")
            return redirect(url_for('nova_taxa'))

        # Validação: Verificar se a taxa é um número válido
        try:
            valor_float = float(valor)
            if valor_float <= 0:
                flash("A taxa deve ser um valor positivo.", "error")
                return redirect(url_for('nova_taxa'))
        except ValueError:
            flash("Valor da taxa inválido.", "error")
            return redirect(url_for('nova_taxa'))

        cursor.execute('INSERT INTO TAXA_JURO (ANO, TAXA_MENSAL, DATA_CRIACAO, ID_USUARIO) VALUES (?, ?, ?, ?)',
                       (ano, valor, data, id_usuario))
        con.commit()

        flash("Taxa de juros criada com sucesso!", "success")
    except Exception as e:
        flash("Erro ao criar taxa de juros. Por favor, tente novamente.", "error")
    finally:
        cursor.close()

    return redirect(url_for('taxas'))

# Define a rota para editar uma taxa, recebendo um ID e aceitando GET/POST.
@app.route('/app/taxas/editar/<int:id>', methods=['GET', 'POST'])
def editar_taxa(id):
    if 'usuario' not in session:
        flash("Você precisa fazer login para acessar esta página.", "error")
        return redirect(url_for('login'))

    if session['usuario'][4] != 'admin':
        flash("Acesso negado. Apenas administradores podem acessar esta página.", "error")
        return redirect(url_for('dashboard'))

    if request.method == "GET":
        cursor = con.cursor()
        dadosTaxa = None

        try:
            cursor.execute('SELECT ano, taxa_mensal, data_criacao FROM taxa_juro WHERE id_taxajuro = ?', (id,))
            dadosTaxa_raw = cursor.fetchone()

            if not dadosTaxa_raw:
                flash("Taxa não encontrada.", "error")
                return redirect(url_for('taxas'))

            # Formata a data para exibição
            data_criacao = dadosTaxa_raw[2]
            if isinstance(data_criacao, str):
                data_obj = datetime.strptime(data_criacao.split()[0], '%Y-%m-%d')
            else:
                data_obj = data_criacao
            data_formatada = data_obj.strftime('%d/%m/%Y')

            # Cria tupla com dados formatados
            dadosTaxa = (dadosTaxa_raw[0], dadosTaxa_raw[1], data_formatada)

        except Exception as e:
            flash("Erro ao buscar dados da taxa.", "error")
        finally:
            cursor.close()

        return render_template('editar_taxa.html', dadosTaxa=dadosTaxa)

    # Se for POST, atualiza os dados
    cursor = con.cursor()

    try:
        vigencia = request.form['ano']
        valor = request.form['taxa']

        # Validações
        ano_atual = datetime.now().year
        try:
            ano_int = int(vigencia)
            if ano_int != ano_atual:
                flash(f"O ano deve ser {ano_atual}.", "error")
                return redirect(url_for('editar_taxa', id=id))
        except ValueError:
            flash("Ano inválido.", "error")
            return redirect(url_for('editar_taxa', id=id))

        try:
            valor_float = float(valor)
            if valor_float <= 0:
                flash("A taxa deve ser um valor positivo.", "error")
                return redirect(url_for('editar_taxa', id=id))
        except ValueError:
            flash("Valor da taxa inválido.", "error")
            return redirect(url_for('editar_taxa', id=id))

        cursor.execute('UPDATE TAXA_JURO SET ano = ?, taxa_mensal = ? WHERE id_taxajuro = ?',
                       (vigencia, valor, id))
        con.commit()

        flash("Taxa atualizada com sucesso!", "success")
    except Exception as e:
        flash("Houve um erro ao atualizar as informações. Por favor, tente novamente.", "error")
    finally:
        cursor.close()

    return redirect(url_for('taxas'))

# Define a rota para excluir uma taxa, recebendo um ID inteiro.
@app.route('/app/taxas/excluir/<int:id>')
# Define a função 'excluir_taxa' que recebe o ID da taxa.
def excluir_taxa(id):
    # Verifica se o usuário não está logado ou não é admin.
    if 'usuario' not in session or session['usuario'][4] != 'admin':
        # Exibe mensagem de acesso negado.
        flash("Acesso negado. Apenas administradores podem realizar esta ação.", "error")
        # Redireciona para o dashboard.
        return redirect(url_for('dashboard'))

    # Cria um cursor para o banco de dados.
    cursor = con.cursor()

    # Inicia um bloco de tratamento de exceções.
    try:
        # Exclui a taxa do banco de dados
        # Executa o comando SQL para deletar a taxa pelo ID.
        cursor.execute('DELETE FROM TAXA_JURO WHERE id_taxajuro = ?', (id,))
        # Confirma a transação.
        con.commit()

        # Exibe uma mensagem de sucesso.
        flash("Taxa excluída com sucesso!", "success")
    # Captura qualquer exceção.
    except Exception as e:
        # Exibe uma mensagem de erro.
        flash("Erro ao excluir taxa. Por favor, tente novamente.", "error")
    # Bloco que sempre será executado.
    finally:
        # Fecha o cursor.
        cursor.close()

    # Redireciona para a página de listagem de taxas.
    return redirect(url_for('taxas'))


# Define a rota para '/app/taxas'.
@app.route('/app/taxas')
def taxas():
    if 'usuario' not in session:
        flash("Você precisa fazer login para acessar esta página.", "error")
        return redirect(url_for('login'))

    todastaxas = []
    cursor = con.cursor()

    try:
        # Busca todas as taxas com JOIN para obter o nome do usuário criador e formata a data
        cursor.execute('''SELECT id_taxajuro
                               , ano
                               , taxa_mensal
                               , data_criacao
                               , u.NOME
                               FROM TAXA_JURO tj
                               INNER JOIN USUARIO u ON u.ID_USUARIO = tj.ID_USUARIO''')
        taxas_raw = cursor.fetchall()

        # Formata as datas para o padrão brasileiro
        todastaxas = []
        for taxa in taxas_raw:
            # Converte a data para o formato brasileiro
            data_criacao = taxa[3]
            if isinstance(data_criacao, str):
                data_obj = datetime.strptime(data_criacao.split()[0], '%Y-%m-%d')
            else:
                data_obj = data_criacao
            data_formatada = data_obj.strftime('%d/%m/%Y')

            # Cria nova tupla com a data formatada
            taxa_formatada = (taxa[0], taxa[1], taxa[2], data_formatada, taxa[4])
            todastaxas.append(taxa_formatada)

    except Exception as e:
        flash("Houve um erro ao obter as taxas. Por favor, tente novamente.", "error")
    finally:
        cursor.close()

    return render_template('tabelaJuro.html', taxas=todastaxas)


@app.route('/confirmar_emprestimo', methods=['POST'])
def confirmar_emprestimo():
    if 'usuario' not in session:
        flash("Você precisa fazer login para acessar esta página.", "error")
        return redirect(url_for('login'))

    cursor = con.cursor()
    try:
        id_usuario = session['usuario'][0]

        # Dados do formulário
        valor = float(request.form['valor'])
        prazo = int(request.form['prazo'])
        parcela_mensal = float(request.form['parcela_mensal'])
        data_criacao = request.form.get('data_criacao', date.today().strftime('%d/%m/%Y'))

        # Data atual como data de contratação
        data_contratacao = date.today()

        # Calcular próximo vencimento (primeiro dia do próximo mês)
        if data_contratacao.month == 12:
            proximo_vencimento = data_contratacao.replace(year=data_contratacao.year + 1, month=1, day=1)
        else:
            proximo_vencimento = data_contratacao.replace(month=data_contratacao.month + 1, day=1)

        # Inserir empréstimo COM data_contratacao
        cursor.execute("""
            INSERT INTO EMPRESTIMOS 
            (ID_USUARIO, VALOR_EMPRESTIMO, PARCELAS_RESTANTES, PROXIMO_VENCIMENTO, 
             PARCELA_MENSAL, STATUS, DATA_CONTRATACAO) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id_usuario, valor, prazo, proximo_vencimento, parcela_mensal, 'ativo', data_contratacao))

        # Inserir APENAS a parcela mensal como despesa COM CLASSIFICAÇÃO "Empréstimo"
        descricao = f"Parcela de empréstimo - {prazo}x de R$ {parcela_mensal:.2f}"
        cursor.execute("""
            INSERT INTO TRANSACOES 
            (ID_USUARIO, TIPO, VALOR, DESCRICAO, DATA_TRANSACAO, CLASSIFICACAO) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id_usuario, 'despesa', parcela_mensal, descricao, proximo_vencimento, 'Empréstimo'))

        con.commit()

        # Limpar a simulação da sessão após confirmar
        if 'simulacao_resultado' in session:
            session.pop('simulacao_resultado')

        flash(
            f"Empréstimo contratado com sucesso! A parcela mensal de R$ {parcela_mensal:.2f} foi adicionada às suas despesas.",
            "success")

    except Exception as e:
        flash(f"Erro ao confirmar empréstimo: {e}", "error")
    finally:
        cursor.close()

    return redirect(url_for('dashboard'))

# Define a rota para '/app/simulacao/criar'.
@app.route('/app/simulacao/criar', methods=['GET', 'POST'])
def nova_simulacao():
    if 'usuario' not in session:
        flash("Você precisa fazer login para acessar esta página.", "error")
        return redirect(url_for('login'))

    cursor = con.cursor()
    # Buscar administradores para select no formulário
    cursor.execute("""
        SELECT DISTINCT u.NOME
        FROM TAXA_JURO tj
        JOIN USUARIO u ON u.ID_USUARIO = tj.ID_USUARIO
        WHERE u.TIPO = 'admin'
    """)
    admins = [{'nome': row[0]} for row in cursor.fetchall()]

    current_year = datetime.now().year
    current_date = datetime.now().strftime('%Y-%m-%d')

    if request.method == 'GET':
        cursor.close()
        return render_template('nova_simulacao.html', admins=admins, current_year=current_year,
                               current_date=current_date)

    # Se for POST
    try:
        id_usuario = session['usuario'][0]

        # Usar get() para evitar KeyError
        valor_str = request.form.get('valor', '').replace(',', '.')
        ano_emprestimo = request.form.get('ano', '')
        adm = request.form.get('adm', '')
        prazo_str = request.form.get('prazo', '')
        data_criacao = request.form.get('data_criacao', '')

        # Validações básicas
        if not all([valor_str, ano_emprestimo, adm, prazo_str]):
            flash('Por favor, preencha todos os campos obrigatórios.', "error")
            return render_template('nova_simulacao.html', admins=admins, current_year=current_year,
                                   current_date=current_date)

        try:
            valor = float(valor_str)
            prazo = int(prazo_str)

            if valor <= 0:
                flash("O valor deve ser maior que zero.", "error")
                return render_template('nova_simulacao.html', admins=admins, current_year=current_year,
                                       current_date=current_date)

            if prazo <= 0:
                flash("O prazo deve ser maior que zero.", "error")
                return render_template('nova_simulacao.html', admins=admins, current_year=current_year,
                                       current_date=current_date)

        except ValueError:
            flash('Por favor, insira valores válidos nos campos numéricos.', "error")
            return render_template('nova_simulacao.html', admins=admins, current_year=current_year,
                                   current_date=current_date)

        # Buscar taxa do administrador
        cursor.execute("""
            SELECT FIRST 1 TAXA_MENSAL FROM TAXA_JURO
            WHERE ID_USUARIO = (SELECT ID_USUARIO FROM USUARIO WHERE NOME = ?)
            AND ANO = ?
            ORDER BY DATA_CRIACAO DESC
        """, (adm, ano_emprestimo))
        taxa = cursor.fetchone()

        if not taxa:
            flash('Taxa não encontrada para o administrador e ano informado', "error")
            return render_template('nova_simulacao.html', admins=admins, current_year=current_year,
                                   current_date=current_date)

        # CORREÇÃO DO CÁLCULO DA PARCELA
        i = float(taxa[0]) / 100
        PV = valor
        n = prazo

        if i == 0:
            PMT = PV / n
        else:
            PMT = PV * i / (1 - (1 + i) ** -n)

        total_pagar = PMT * n
        juros_total = total_pagar - PV
        lucro_mensal = juros_total / n  # Lucro mensal aproximado

        # Calcular renda líquida atual (sem parcelas futuras)
        cursor.execute("""
            SELECT TIPO, VALOR, DESCRICAO 
            FROM TRANSACOES 
            WHERE ID_USUARIO = ?
        """, (id_usuario,))
        transacoes = cursor.fetchall()

        total_receitas = 0.0
        total_despesas_atual = 0.0  # CORREÇÃO: Mantido como total_despesas_atual

        for transacao in transacoes:
            tipo = transacao[0]
            valor_transacao = float(transacao[1])  # CORREÇÃO: Renomeado para evitar conflito
            descricao = transacao[2].lower() if transacao[2] else ""

            # Ignorar parcelas de empréstimo no cálculo das despesas normais
            if 'parcela de empréstimo' not in descricao:
                if tipo.lower() == 'receita':
                    total_receitas += valor_transacao
                elif tipo.lower() == 'despesa':
                    total_despesas_atual += valor_transacao  # CORREÇÃO: Usando total_despesas_atual

        # Calcular limite (30% da renda líquida atual)
        renda_liquida_atual = total_receitas - total_despesas_atual
        limite_emprestimo = renda_liquida_atual * 0.3
        if limite_emprestimo < 0:
            limite_emprestimo = 0

        if valor > limite_emprestimo:
            flash(f"O valor do empréstimo (R$ {valor:.2f}) excede seu limite permitido (R$ {limite_emprestimo:.2f}).",
                  "error")
            return render_template('nova_simulacao.html', admins=admins, current_year=current_year,
                                   current_date=current_date)

        # Calcular comprometimento com a renda líquida atual
        comprometimento = (PMT / renda_liquida_atual) * 100 if renda_liquida_atual > 0 else 0

        if comprometimento < 20:
            risco = "Baixo"
        elif comprometimento <= 35:
            risco = "Médio"
        else:
            risco = "Alto"

        cursor.close()

        # CORREÇÃO: SALVAR NA SESSÃO ANTES DE REDIRECIONAR
        session['simulacao_resultado'] = {
            'valor': valor,
            'ano': ano_emprestimo,
            'adm': adm,
            'prazo': prazo,
            'parcela': PMT,
            'total': total_pagar,
            'lucro': lucro_mensal,
            'comprometimento': comprometimento,
            'risco': risco,
            'data_criacao': datetime.now().strftime('%d/%m/%Y')
        }

        # REDIRECIONAR para a rota de resultado em vez de renderizar diretamente
        return redirect(url_for('resultado_simulacao'))

    except Exception as e:
        flash(f'Erro ao processar simulação: {str(e)}', "error")
        return render_template('nova_simulacao.html', admins=admins, current_year=current_year,
                               current_date=current_date)
    finally:
        cursor.close()

@app.route('/app/simulacao/resultado')
def resultado_simulacao():
    if 'usuario' not in session:
        flash("Você precisa fazer login para acessar esta página.", "error")
        return redirect(url_for('login'))

    simulacao = session.get('simulacao_resultado')

    if not simulacao:
        flash("Nenhum resultado de simulação encontrado. Faça a simulação primeiro.", "error")
        return redirect(url_for('nova_simulacao'))

    return render_template('resultado_simulacao.html',
                           valor=simulacao['valor'],
                           ano=simulacao['ano'],
                           adm=simulacao['adm'],
                           prazo=simulacao['prazo'],
                           parcela=simulacao['parcela'],
                           total=simulacao['total'],
                           lucro=simulacao['lucro'],
                           comprometimento=simulacao['comprometimento'],
                           risco=simulacao['risco'],
                           data_criacao=simulacao['data_criacao'])

# Define a rota para '/app/transacoes'.
# Define a rota '/app/transacoes' para acessar a página de transações
@app.route('/app/transacoes')
def transacoes():
    # Verifica se o usuário não está na sessão (não está logado)
    if 'usuario' not in session:
        # Exibe mensagem de erro para o usuário
        flash("Você precisa fazer login para acessar esta página.", "error")
        # Redireciona para a página de login
        return redirect(url_for('login'))

    # Obtém o ID do usuário da sessão (primeira posição do array)
    id_usuario = session['usuario'][0]
    # Cria um cursor para executar queries no banco de dados
    cursor = con.cursor()
    try:
        # Executa query para buscar todas as transações do usuário
        cursor.execute("""
            SELECT ID_TRANSACOES, TIPO, VALOR, DESCRICAO, DATA_TRANSACAO, CLASSIFICACAO
            FROM TRANSACOES
            WHERE ID_USUARIO = ?
            ORDER BY DATA_TRANSACAO DESC
        """, (id_usuario,))
        # Busca todos os resultados da query
        transacoes_raw = cursor.fetchall()

        # Inicializa lista vazia para armazenar transações formatadas
        transacoes = []
        # Inicializa saldo com valor zero
        saldo = 0.0

        # Itera sobre cada transação retornada do banco
        for t in transacoes_raw:
            # Obtém a data da transação (quinta coluna - índice 4)
            dt = t[4]

            # Verifica se a data é uma string (precisa de parsing)
            if isinstance(dt, str):
                # Converte string para objeto datetime (ignora hora se existir)
                dt_obj = datetime.strptime(dt.split()[0], '%Y-%m-%d')
            else:
                # Se já for objeto datetime, usa diretamente
                dt_obj = dt

            # Formata a data para o padrão brasileiro (dia/mês/ano)
            data_formatada = dt_obj.strftime('%d/%m/%Y') if dt_obj else ''

            # Adiciona transação formatada à lista, convertendo valor para float
            transacoes.append((t[0], t[1], float(t[2]), t[3], data_formatada, t[5]))

            # Atualiza o saldo baseado no tipo de transação
            if t[1].lower() == 'receita':
                # Se for receita, adiciona ao saldo
                saldo += float(t[2])
            else:
                # Se for despesa, subtrai do saldo
                saldo -= float(t[2])

    # Captura qualquer exceção que ocorrer durante o processamento
    except Exception as e:
        # Exibe mensagem de erro para o usuário
        flash(f"Erro ao carregar transações: {e}", "error")
        # Define transações como lista vazia em caso de erro
        transacoes = []
        # Define saldo como zero em caso de erro
        saldo = 0.0
    finally:
        # Fecha o cursor para liberar recursos do banco de dados
        cursor.close()

    # Renderiza o template passando as transações e saldo calculado
    return render_template('transacoes.html', transacoes=transacoes, saldo=saldo)


# Define a rota para '/nova_receita'.
# Define a rota '/nova_receita' que aceita métodos GET e POST
@app.route('/nova_receita', methods=['GET', 'POST'])
def nova_receita():
    # Verifica se o usuário não está na sessão (não está logado)
    if 'usuario' not in session:
        # Exibe mensagem de erro para o usuário
        flash("Você precisa fazer login para acessar esta página.", "error")
        # Redireciona para a página de login
        return redirect(url_for('login'))

    # Verifica se a requisição é do tipo POST (envio de formulário)
    if request.method == 'POST':
        # Obtém o ID do usuário da sessão (primeira posição do array)
        id_usuario = session['usuario'][0]
        # Obtém a data do formulário
        data_str = request.form['data']
        # Obtém o tipo do formulário (provavelmente 'receita')
        tipo = request.form['tipo']
        # Obtém o valor do formulário e substitui vírgula por ponto para conversão decimal
        valor_str = request.form['valor'].replace(',', '.')
        # Obtém a descrição do formulário
        descricao = request.form['descricao']

        # Tenta converter o valor para float e validá-lo
        try:
            valor = float(valor_str)
            # Verifica se o valor é positivo (não permite zero ou negativo)
            if valor <= 0:
                flash("Valor inválido. Não é permitido valor negativo ou zero.", "error")
                # Redireciona de volta para o formulário em caso de erro
                return redirect(url_for('nova_receita'))
        except ValueError:
            # Se a conversão para float falhar, exibe mensagem de erro
            flash("Valor inválido.", "error")
            # Redireciona de volta para o formulário
            return redirect(url_for('nova_receita'))

        # Tenta inserir os dados no banco de dados
        try:
            # Converte a string de data para objeto datetime
            data_obj = datetime.strptime(data_str, '%Y-%m-%d')
            # Formata a data para o padrão ISO (banco de dados)
            data_formatada = data_obj.strftime('%Y-%m-%d')

            # Cria cursor para executar queries no banco
            cursor = con.cursor()
            # Executa query para inserir nova transação na tabela
            cursor.execute("""
                INSERT INTO TRANSACOES (ID_USUARIO, TIPO, VALOR, DESCRICAO, DATA_TRANSACAO)
                VALUES (?, ?, ?, ?, ?)
            """, (id_usuario, tipo, valor, descricao, data_formatada))
            # Confirma a transação no banco de dados
            con.commit()
            # Exibe mensagem de sucesso para o usuário
            flash("Receita cadastrada com sucesso!", "success")
            # Redireciona para a página de transações após sucesso
            return redirect(url_for('transacoes'))
        except Exception as e:
            # Captura qualquer erro durante a inserção no banco
            flash(f"Erro ao cadastrar receita: {e}", "error")
        finally:
            # Garante que o cursor seja fechado mesmo em caso de erro
            if 'cursor' in locals():
                cursor.close()

    # Renderiza o template do formulário (para GET ou se houve erro no POST)
    return render_template('nova_receita.html')


# Define a rota '/perfil', que aceita os métodos GET e POST.
@app.route('/perfil', methods=['GET', 'POST'])
# Define a função 'perfil' para editar os dados do usuário.
def perfil():
    # Verifica se o usuário não está logado na sessão.
    if 'usuario' not in session:
        # Mostra uma mensagem de erro.
        flash("Você precisa fazer login para acessar esta página.", "error")
        # Redireciona para a página de login.
        return redirect(url_for('login'))

    # Verifica se o método da requisição é GET.
    if request.method == 'GET':
        # Se for GET, exibe a página de edição de perfil.
        return render_template('editar_perfil.html')

    # Cria um cursor para executar comandos no banco de dados.
    cursor = con.cursor()

    # Inicia um bloco try para tratamento de erros.
    try:
        # Obtém os dados do formulário
        # Pega o nome enviado pelo formulário.
        nome = request.form['nome']
        # Pega o email enviado pelo formulário.
        email = request.form['email']
        # Pega o CPF enviado pelo formulário.
        cpf = request.form["cpf"]
        # Pega o telefone enviado pelo formulário.
        telefone = request.form["telefone"]
        # Pega a senha enviada pelo formulário.
        senha = request.form["senha"]
        # Pega a confirmação de senha enviada pelo formulário.
        confirmarSenha = request.form['confirmar']

        # NOVA LÓGICA IMPLEMENTADA AQUI #

        # Verifica se o usuário preencheu o campo de senha, indicando que quer alterá-la.
        # Se o campo senha não estiver vazio.
        if senha:
            # Se a senha foi preenchida, fazemos todas as validações necessárias.
            # Verifica se a nova senha atende aos critérios de segurança.
            if not verificar_senha_forte(senha):
                # Se não atender, mostra uma mensagem de erro.
                flash(
                    # Texto da mensagem.
                    "A nova senha deve ter pelo menos 8 caracteres, uma letra maiúscula, uma minúscula, um número e um caractere especial.",
                    # Categoria da mensagem.
                    "error")
                # Redireciona de volta para a página de perfil.
                return redirect(url_for('perfil'))

            # Verifica se a senha e a confirmação são diferentes.
            if senha != confirmarSenha:
                # Mostra uma mensagem de erro.
                flash("As senhas não coincidem. Por favor, tente novamente.", "error")
                # Redireciona de volta para a página de perfil.
                return redirect(url_for('perfil'))

            # Criptografa a NOVA senha
            # Gera um hash seguro para a nova senha.
            hashSenha = generate_password_hash(senha).decode('utf-8')

            # Prepara a query SQL para atualizar TUDO, incluindo a senha
            # Comando SQL para atualizar nome, email, cpf, telefone e senha.
            cursor.execute('''UPDATE USUARIO SET
                           nome = ?, email = ?, cpf = ?, telefone = ?, senha = ?
                           WHERE id_usuario = ?''',
                           # Passa os novos dados e o ID do usuário como parâmetros.
                           (nome, email, cpf, telefone, hashSenha, session['usuario'][0]))

        # Se o campo senha estiver vazio.
        else:
            # Se a senha foi deixada em branco, atualizamos tudo, MENOS a senha.
            # Comando SQL para atualizar apenas nome, email, cpf e telefone.
            cursor.execute('''UPDATE USUARIO SET
                           nome = ?, email = ?, cpf = ?, telefone = ?
                           WHERE id_usuario = ?''',
                           # Passa os novos dados (sem a senha) e o ID do usuário como parâmetros.
                           (nome, email, cpf, telefone, session['usuario'][0]))

        # Confirma a transação no banco de dados
        # Efetiva as alterações no banco de dados.
        con.commit()

        # Após a atualização, busca os dados mais recentes para atualizar a sessão
        # Executa uma nova consulta para buscar os dados atualizados do usuário.
        cursor.execute(
            # Comando SQL de seleção.
            "SELECT id_usuario, nome, email, senha, tipo, tentativas, cpf, ativo, telefone FROM usuario WHERE id_usuario = ?",
            # Passa o ID do usuário da sessão como parâmetro.
            (session["usuario"][0],))
        # Armazena os dados atualizados do usuário.
        usuarioAtualizado = cursor.fetchone()

        # Atualiza a sessão com os novos dados
        # Substitui os dados antigos na sessão pelos novos.
        session["usuario"] = usuarioAtualizado

        # Mostra uma mensagem de sucesso.
        flash("Informações atualizadas com sucesso!", "success")

        # Redireciona para o dashboard.
        return redirect(url_for('dashboard'))

    # Se ocorrer qualquer erro no bloco try.
    except Exception as e:
        # Mostra uma mensagem de erro detalhada.
        flash(f"Houve um erro ao atualizar as informações: {e}", "error")
    # Bloco que é executado independentemente de erro.
    finally:
        # Garante que o cursor do banco de dados seja fechado.
        cursor.close()

    # Redireciona para o dashboard em caso de erro.
    return redirect(url_for('dashboard'))


# Define a rota '/nova_despesa' que aceita métodos GET e POST
@app.route('/nova_despesa', methods=['GET', 'POST'])
def nova_despesa():
    # Verifica se o usuário não está na sessão (não está logado)
    if 'usuario' not in session:
        # Exibe mensagem de erro informando que precisa estar logado
        flash("Você precisa fazer login para acessar esta página.", "error")
        # Redireciona para a página de login
        return redirect(url_for('login'))

    # Verifica se a requisição é do tipo POST (envio de formulário)
    if request.method == 'POST':
        # Obtém o ID do usuário da sessão (primeira posição do array)
        id_usuario = session['usuario'][0]
        # Obtém a data do formulário
        data_str = request.form['data']
        # Obtém o tipo do formulário (provavelmente 'despesa')
        tipo = request.form['tipo']
        # Obtém o valor do formulário e substitui vírgula por ponto para conversão decimal
        valor_str = request.form['valor'].replace(',', '.')
        # Obtém a descrição da despesa do formulário
        descricao = request.form['descricao']
        classificacao = request.form['classificacao']

        # Tenta converter o valor para float e validá-lo
        try:
            valor = float(valor_str)
            # Verifica se o valor é positivo (não permite zero ou negativo)
            if valor <= 0:
                flash("Valor inválido. Não é permitido valor negativo ou zero.", "error")
                # Redireciona de volta para o formulário em caso de erro
                return redirect(url_for('nova_despesa'))
        except ValueError:
            # Se a conversão para float falhar, exibe mensagem de erro
            flash("Valor inválido.", "error")
            # Redireciona de volta para o formulário
            return redirect(url_for('nova_despesa'))

        # Tenta inserir os dados no banco de dados
        try:
            # Converte a string de data para objeto datetime
            data_obj = datetime.strptime(data_str, '%Y-%m-%d')
            # Formata a data para o padrão ISO (banco de dados)
            data_formatada = data_obj.strftime('%Y-%m-%d')

            # Cria cursor para executar queries no banco
            cursor = con.cursor()
            # Executa query para inserir nova transação na tabela TRANSACOES
            cursor.execute("""
                INSERT INTO TRANSACOES (ID_USUARIO, TIPO, VALOR, DESCRICAO, DATA_TRANSACAO, CLASSIFICACAO)
                VALUES (?, ?, ?, ?, ?,?)
            """, (id_usuario, tipo, valor, descricao, data_formatada, classificacao))
            # Confirma a transação no banco de dados
            con.commit()
            # Exibe mensagem de sucesso para o usuário
            flash("Despesa cadastrada com sucesso!", "success")
            # Redireciona para a página de transações após sucesso
            return redirect(url_for('transacoes'))
        except Exception as e:
            # Captura qualquer erro durante a inserção no banco
            flash(f"Erro ao cadastrar despesa: {e}", "error")
        finally:
            # Garante que o cursor seja fechado mesmo em caso de erro
            if 'cursor' in locals():
                cursor.close()

    # Renderiza o template do formulário de nova despesa
    # (para requisições GET ou se houve erro no POST)
    return render_template('nova_despesa.html')


# Define a rota '/editar_transacao/<int:id_transacao>' que aceita GET e POST
# O <int:id_transacao> captura um parâmetro inteiro da URL
@app.route('/editar_transacao/<int:id_transacao>', methods=['GET', 'POST'])
def editar_transacao(id_transacao):
    if 'usuario' not in session:
        flash("Você precisa fazer login para acessar esta página.", "error")
        return redirect(url_for('login'))

    id_usuario = session['usuario'][0]
    cursor = con.cursor()
    transacao = None

    try:
        # Busca a transação específica do usuário no banco
        cursor.execute("""
            SELECT ID_TRANSACOES, TIPO, VALOR, DESCRICAO, DATA_TRANSACAO, CLASSIFICACAO
            FROM TRANSACOES
            WHERE ID_TRANSACOES = ? AND ID_USUARIO = ?
        """, (id_transacao, id_usuario))
        t = cursor.fetchone()

        if not t:
            flash("Transação não encontrada.", "error")
            cursor.close()
            return redirect(url_for('transacoes'))

        # VERIFICA SE É UMA TRANSAÇÃO DE EMPRÉSTIMO (BLOQUEAR EDIÇÃO/EXCLUSÃO)
        if t[5] and t[5].lower() == 'empréstimo':
            flash("Esta transação é uma parcela de empréstimo e não pode ser editada ou excluída.", "error")
            cursor.close()
            return redirect(url_for('transacoes'))

        dt = t[4]
        if isinstance(dt, str):
            dt_obj = datetime.strptime(dt.split()[0], '%Y-%m-%d')
        else:
            dt_obj = dt
        data_formatada = dt_obj.strftime('%Y-%m-%d')

        transacao = (t[0], t[1], float(t[2]), t[3], data_formatada, t[5])

        if request.method == 'POST':
            if 'excluir' in request.form:
                try:
                    cursor.execute("DELETE FROM TRANSACOES WHERE ID_TRANSACOES = ? AND ID_USUARIO = ?",
                                   (id_transacao, id_usuario))
                    con.commit()
                    flash("Exclusão da transação com sucesso!", "success")
                    cursor.close()
                    return redirect(url_for('transacoes'))
                except Exception as e:
                    flash(f"Erro ao excluir transação: {e}", "error")
                    return redirect(url_for('editar_transacao', id_transacao=id_transacao))

            data_str = request.form['data']
            tipo = request.form['tipo']
            valor_str = request.form['valor'].replace(',', '.')
            descricao = request.form['descricao']
            classificacao = request.form['classificacao']

            try:
                valor = float(valor_str)
                if valor <= 0:
                    flash("Valor inválido. Não é permitido valor negativo ou zero.", "error")
                    cursor.close()
                    return redirect(url_for('editar_transacao', id_transacao=id_transacao))
            except ValueError:
                flash("Valor inválido.", "error")
                cursor.close()
                return redirect(url_for('editar_transacao', id_transacao=id_transacao))

            try:
                cursor.execute("""
                    UPDATE TRANSACOES SET DATA_TRANSACAO = ?, TIPO = ?, VALOR = ?, DESCRICAO = ?, CLASSIFICACAO = ?
                    WHERE ID_TRANSACOES= ? AND ID_USUARIO = ?
                """, (data_str, tipo, valor, descricao, classificacao, id_transacao, id_usuario))
                con.commit()
                flash("Transação atualizada com sucesso!", "success")
                cursor.close()
                return redirect(url_for('transacoes'))
            except Exception as e:
                flash(f"Erro ao atualizar transação: {e}", "error")
                return redirect(url_for('editar_transacao', id_transacao=id_transacao))

    except Exception as e:
        flash(f"Erro ao processar a transação: {e}", "error")
        return redirect(url_for('transacoes'))
    finally:
        cursor.close()

    return render_template('editar_transacao.html', transacao=transacao)

# Define a rota '/app/admin/users'.
@app.route('/app/admin/users')
# Define a função 'admin_users' para listar usuários.
def admin_users():
    # Verifica se não há usuário logado na sessão.
    if 'usuario' not in session:
        # Mostra uma mensagem de erro.
        flash("Você precisa fazer login para acessar esta página.", "error")
        # Redireciona para a página de login.
        return redirect(url_for('login'))

    # Verifica se o usuário logado não é um administrador.
    if session['usuario'][4] != 'admin':
        # Mostra uma mensagem de acesso negado.
        flash("Pá Acesso negado. Apenas administradores podem acessar esta página.", "error")
        # Redireciona para o dashboard.
        return redirect(url_for('dashboard'))

    # Inicializa uma lista vazia para armazenar os usuários.
    all_users = []
    # Cria um cursor para interagir com o banco de dados.
    cursor = con.cursor()

    # Inicia um bloco de tratamento de erros.
    try:
        # Executa uma consulta para selecionar todos os usuários.
        cursor.execute("SELECT id_usuario, nome, email, tipo, tentativas, ativo, cpf, telefone FROM usuario")
        # Armazena todos os resultados da consulta na lista.
        all_users = cursor.fetchall()
    # Se ocorrer um erro na consulta.
    except Exception as e:
        # Mostra uma mensagem de erro.
        flash("Houve um erro ao obter os usuários. Por favor, tente novamente.", "error")
    # Bloco que sempre será executado.
    finally:
        # Fecha o cursor do banco de dados.
        cursor.close()

    # Renderiza a página de administração de usuários, passando a lista de usuários.
    return render_template('admin_users.html', users=all_users)


# Define a rota para editar um usuário específico, aceitando GET e POST.
@app.route("/app/admin/users/edit/<int:user_id>", methods=["GET", "POST"])
def admin_edit_user(user_id):
    if "usuario" not in session or session["usuario"][4] != "admin":
        flash("Acesso negado. Apenas administradores podem acessar esta página.", "error")
        return redirect(url_for("login"))

    cursor = con.cursor()
    user_to_edit = None

    try:
        if request.method == "GET":
            cursor.execute(
                "SELECT id_usuario, nome, email, cpf, telefone, tipo, tentativas, ativo FROM usuario WHERE id_usuario = ?",
                (user_id,))
            user_to_edit = cursor.fetchone()

            if not user_to_edit:
                flash("Usuário não encontrado.", "error")
                cursor.close()
                return redirect(url_for("admin_users"))

            cursor.close()
            return render_template("admin_edit_user.html", user=user_to_edit)

        elif request.method == "POST":
            nome = request.form["nome"]
            email = request.form["email"]
            cpf = request.form["cpf"]
            telefone = request.form["telefone"]
            tipo = request.form["tipo"]
            ativo = True if request.form.get("ativo") == "on" else False
            senha = request.form["senha"]
            confirmar_senha = request.form["confirmar"]

            # Validação de senha
            if senha:
                if senha != confirmar_senha:
                    flash("As senhas não coincidem.", "error")
                    cursor.close()
                    return redirect(url_for("admin_edit_user", user_id=user_id))

                if not verificar_senha_forte(senha):
                    flash(
                        "A senha deve ter pelo menos 8 caracteres, uma letra maiúscula, uma minúscula, um número e um caractere especial.",
                        "error")
                    cursor.close()
                    return redirect(url_for("admin_edit_user", user_id=user_id))

                hash_senha = generate_password_hash(senha).decode("utf-8")
                cursor.execute(
                    "UPDATE usuario SET nome = ?, email = ?, cpf = ?, telefone = ?, tipo = ?, ativo = ?, senha = ? WHERE id_usuario = ?",
                    (nome, email, cpf, telefone, tipo, ativo, hash_senha, user_id))
            else:
                cursor.execute(
                    "UPDATE usuario SET nome = ?, email = ?, cpf = ?, telefone = ?, tipo = ?, ativo = ? WHERE id_usuario = ?",
                    (nome, email, cpf, telefone, tipo, ativo, user_id))

            con.commit()
            flash("Usuário atualizado com sucesso!", "success")
            cursor.close()
            return redirect(url_for("admin_users"))

    except Exception as e:
        flash(f"Erro ao atualizar usuário: {e}", "error")
        cursor.close()
        return redirect(url_for("admin_edit_user", user_id=user_id))


# Define a rota para resetar as tentativas de login de um usuário.
@app.route("/app/admin/users/reset_attempts/<int:user_id>")
# Define a função que recebe o ID do usuário.
def admin_reset_attempts(user_id):
    # Verifica se o usuário não está logado ou não é um administrador.
    if "usuario" not in session or session["usuario"][4] != "admin":
        # Mostra uma mensagem de acesso negado.
        flash("Acesso negado. Apenas administradores podem realizar esta ação.", "error")
        # Redireciona para a página de login.
        return redirect(url_for("login"))

    # Cria um cursor para o banco de dados.
    cursor = con.cursor()
    # Inicia um bloco de tratamento de erros.
    try:
        # Executa o comando para zerar as tentativas e ativar a conta.
        cursor.execute("UPDATE usuario SET tentativas = 0, ativo = True WHERE id_usuario = ?", (user_id,))
        # Confirma a transação.
        con.commit()
        # Mostra uma mensagem de sucesso.
        flash("Tentativas de login resetadas e conta ativada com sucesso!", "success")
    # Se ocorrer um erro.
    except Exception as e:
        # Mostra uma mensagem de erro detalhada.
        flash(f"Erro ao resetar tentativas de login: {e}", "error")
    # Bloco que sempre será executado.
    finally:
        # Fecha o cursor.
        cursor.close()
    # Redireciona para a lista de usuários.
    return redirect(url_for("admin_users"))

@app.route("/simulacao/criar", methods=['POST'])
def simular():
    if not 'usuario' in session:
        return redirect(url_for('login'))

    userId = session['usuario'][0]
    cursor = con.cursor()

    try:
        cursor.execute("INSERT INTO ")
    except Exception as e:
        flash("Houve um erro ao fazer simuclação", 'error')
    finally:
        cursor.close()

    return redirect(request.referrer)

# Executa a aplicação Flask em modo de desenvolvimento
# Verifica se o script está sendo executado diretamente (não importado).
if __name__ == '__main__':
    criar_admin_fixo()
    # Inicia o servidor de desenvolvimento do Flask com o modo de depuração ativado.
    app.run(debug=True)

### **Linguagem Python (Palavras-chave e Funções Nativas)**
# `from`: Para importar partes de uma biblioteca.
# `import`: Para importar uma biblioteca inteira.
# `def`: Para definir uma função.
# `if`, `elif`, `else`: Para criar blocos de condição.
# `for`: Para criar laços de repetição.
# `in`: Usado em laços `for` e para verificar se um item existe em uma lista, string ou dicionário (como `if 'usuario' in session`).
# `try`, `except`, `finally`: Para tratamento de erros e exceções.
# `return`: Para retornar um valor de uma função.
# `len()`: Para obter o tamanho de uma string ou lista.
# `True`, `False`: Valores booleanos.
# `not`: Operador lógico de negação.
# `and`: Operador lógico "E".
# `is`: Para verificar identidade (usado em `char.isupper()`, `char.islower()`, `char.isdigit()`).

### **Framework Flask**
# `Flask()`: Para criar a instância da sua aplicação web.
# `@app.route()`: Decorador para definir as URLs (rotas) da aplicação.
# `app.run()`: Para iniciar o servidor de desenvolvimento.
# `app.secret_key`: Para configurar a chave secreta da sessão.
# `render_template()`: Para carregar e exibir um arquivo HTML.
# `redirect()`: Para redirecionar o usuário para outra URL.
# `url_for()`: Para gerar URLs dinamicamente a partir do nome da função da rota.
# `session`: Objeto para armazenar informações do usuário entre requisições (login).
# `request`: Objeto que contém as informações da requisição do usuário (como dados de formulário com `request.form`).
# `flash()`: Para exibir mensagens temporárias para o usuário (alertas de sucesso ou erro).

# **Biblioteca Flask-Bcrypt (Segurança de Senha)**
# `generate_password_hash()`: Para criptografar (gerar o hash) de uma senha.
# `check_password_hash()`: Para comparar uma senha em texto puro com uma senha criptografada.

# **Biblioteca FDB (Banco de Dados Firebird)**
# `fdb.connect()`: Para estabelecer a conexão com o banco de dados.
# `con.cursor()`: Para criar um objeto cursor que executa os comandos SQL.
# `con.commit()`: Para salvar (confirmar) as alterações feitas no banco de dados.
# `cursor.execute()`: Para executar um comando SQL.
# `cursor.fetchone()`: Para buscar apenas um resultado da sua consulta SQL.
# `cursor.fetchall()`: Para buscar todos os resultados da sua consulta SQL.
# `cursor.close()`: Para fechar o cursor e liberar recursos.

### **Biblioteca Datetime (Datas e Horas)**
# `date.today()`: Para obter a data atual.

# **Comandos SQL (dentro de strings)**
# `SELECT`: Para consultar dados.
# `INSERT INTO`: Para inserir novos registros.
# `UPDATE`: Para atualizar registros existentes.
# `DELETE FROM`: Para apagar registros.
# `WHERE`: Para filtrar os registros em uma consulta.
# `INNER JOIN`: Para combinar tabelas com base em uma coluna em comum.i{% extends 'templateDashboard.html' %}
