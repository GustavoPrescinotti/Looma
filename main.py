# Importações necessárias para o funcionamento da aplicação Flask
from flask import Flask, render_template, redirect, session, url_for, request, flash
from flask_bcrypt import generate_password_hash, check_password_hash
from datetime import date
import fdb

# Inicialização da aplicação Flask
app = Flask(__name__)

# Chave secreta para gerenciar sessões de forma segura
# IMPORTANTE: Em produção, use uma chave mais complexa e armazenada em variável de ambiente
app.secret_key = 'IgorELaisMeDeemNota'

# Configurações de conexão com o banco de dados Firebird
host = 'localhost'
database = r'C:\Users\Aluno\Downloads\Looma_atualizado\Looma\db\Looma.FDB'
user = 'sysdba'
password = 'sysdba'

# Estabelece a conexão com o banco de dados
con = fdb.connect(host=host, database=database, user=user, password=password)


def verificar_senha_forte(senha):
    """
    Função que verifica se a senha atende aos critérios de segurança.

    Critérios:
    - Mínimo de 8 caracteres
    - Pelo menos uma letra maiúscula
    - Pelo menos uma letra minúscula
    - Pelo menos um número
    - Pelo menos um caractere especial

    Args:
        senha (str): A senha a ser validada

    Returns:
        bool: True se a senha for forte, False caso contrário
    """
    # Verificar o comprimento da senha
    if len(senha) < 8:
        return False

    # Inicializa as variáveis de controle para cada critério
    tem_maiuscula = False
    tem_minuscula = False
    tem_numero = False
    tem_especial = False
    caracteres_especiais = "!@#$%^&*()_-+=<>?/.,;:"

    # Verificar cada caractere da senha
    for char in senha:
        if char.isupper():
            tem_maiuscula = True
        elif char.islower():
            tem_minuscula = True
        elif char.isdigit():
            tem_numero = True
        elif char in caracteres_especiais:
            tem_especial = True

    # Verificar se todas as condições foram atendidas
    if tem_maiuscula and tem_minuscula and tem_numero and tem_especial:
        return True
    return False


@app.route('/')
def index():
    """
    Rota principal da aplicação.
    Renderiza a página inicial (home).

    Returns:
        Template HTML da página inicial
    """
    return render_template('index.html')


@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    """
    Rota de autenticação de usuários.

    GET: Exibe o formulário de login
    POST: Processa as credenciais e autentica o usuário

    Validações:
    - Verifica se o usuário já está logado
    - Valida email e senha
    - Verifica se a conta está ativa
    - Controla tentativas de login (máximo 3 tentativas)

    Returns:
        Template de login ou redirecionamento para dashboard
    """
    # Se o usuário já está logado, redireciona para o dashboard
    if 'usuario' in session:
        return redirect(url_for('dashboard'))

    # Se for uma requisição GET, apenas exibe o formulário
    if request.method == 'GET':
        return render_template('login.html')

    # Cria um cursor para executar comandos SQL
    cursor = con.cursor()

    try:
        # Obtém os dados do formulário
        email = request.form['email']
        senha = request.form['password']

        # Busca o usuário no banco de dados pelo email
        cursor.execute(
            "SELECT id_usuario, nome, email, senha, tipo, tentativas, cpf, ativo FROM usuario WHERE email = ?",
            (email,))
        usuario = cursor.fetchone()

        # Se o usuário não existe, exibe mensagem de erro e redireciona
        if not usuario:
            flash("Email ou senha incorretos. Por favor, tente novamente.", "error")
            return redirect(url_for('login'))

        # Extrai informações do usuário
        tipo = usuario[4]
        tentativas = usuario[5]
        ativo = usuario[7]

        # Verifica se a conta está ativa
        if not ativo:
            flash("Sua conta foi bloqueada devido a múltiplas tentativas de login. Entre em contato com o suporte.",
                  "error")
            return redirect(url_for('login'))

        # Verifica se a senha está correta
        if check_password_hash(usuario[3], senha):
            # Senha correta: cria a sessão do usuário
            session['usuario'] = usuario
            flash("Login realizado com sucesso! Bem-vindo(a)!", "success")
            return redirect(url_for('dashboard'))
        else:
            # Senha incorreta: incrementa o contador de tentativas
            flash("Email ou senha incorretos. Por favor, tente novamente.", "error")

            # Apenas usuários comuns têm limite de tentativas
            if tipo == 'user':
                tentativas = tentativas + 1

                # Se atingiu 3 tentativas, bloqueia a conta
                try:
                    cursor.execute("UPDATE USUARIO SET TENTATIVAS = ?, ATIVO = ? WHERE ID_USUARIO = ?",
                                   (tentativas, (True if tentativas < 3 else False), usuario[0]))
                    con.commit()

                    # Se a conta foi bloqueada, informa o usuário
                    if tentativas >= 3:
                        flash("Sua conta foi bloqueada devido a múltiplas tentativas de login incorretas.", "error")
                except Exception as e:
                    flash("Erro ao processar tentativa de login.", "error")
                finally:
                    cursor.close()
    except Exception as e:
        # Captura qualquer erro durante o processo de login
        flash("Houve um erro ao fazer login. Por favor, tente novamente.", "error")
    finally:
        cursor.close()

    return redirect(url_for('login'))


@app.route('/auth/cadastro', methods=['GET', 'POST'])
def cadastro():
    """
    Rota de cadastro de novos usuários.

    GET: Exibe o formulário de cadastro
    POST: Processa os dados e cria um novo usuário

    Validações:
    - Verifica se o usuário já está logado
    - Valida força da senha
    - Verifica se o email já está cadastrado
    - Criptografa a senha antes de armazenar

    Returns:
        Template de cadastro ou redirecionamento para login
    """
    # Se o usuário já está logado, redireciona para o dashboard
    if 'usuario' in session:
        return redirect(url_for('dashboard'))

    # Se for uma requisição GET, apenas exibe o formulário
    if request.method == 'GET':
        return render_template('cadastro.html')

    # Cria um cursor para executar comandos SQL
    cursor = con.cursor()

    try:
        # Obtém os dados do formulário
        email = request.form['email']
        nome = request.form['name']
        senha = request.form['password']
        cpf = request.form['cpf']
        telefone = request.form['phone']

        # Valida a força da senha
        if not verificar_senha_forte(senha):
            flash(
                "A senha deve ter pelo menos 8 caracteres, uma letra maiúscula, uma letra minúscula, um número e um caractere especial.",
                "error")
            return redirect(url_for('cadastro'))

        # Verifica se o email já está cadastrado
        cursor.execute("SELECT id_usuario FROM usuario WHERE email = ?", (email,))
        usuario = cursor.fetchone()

        if usuario:
            flash("Este email já está cadastrado. Por favor, use outro email ou faça login.", "error")
            cursor.close()
            return redirect(url_for('cadastro'))

        # Criptografa a senha usando bcrypt
        hash_senha = generate_password_hash(senha).decode('utf-8')

        # Insere o novo usuário no banco de dados
        cursor.execute(
            "INSERT INTO usuario(email, nome, senha, cpf, telefone, tipo, tentativas, ativo) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (email, nome, hash_senha, cpf, telefone, 'user', 0, True))
        con.commit()

        # Exibe mensagem de sucesso
        flash("Cadastro realizado com sucesso! Faça login para continuar.", "success")
    except Exception as e:
        # Captura qualquer erro durante o cadastro
        flash("Não foi possível criar sua conta. Por favor, tente novamente.", "error")
        return redirect(url_for('cadastro'))
    finally:
        cursor.close()

    return redirect(url_for('login'))


@app.route('/app')
def dashboard():
    """
    Rota do dashboard principal.

    Redireciona para o dashboard apropriado baseado no tipo de usuário:
    - Admin: dashboard administrativo
    - User: dashboard de usuário comum

    Requer autenticação.

    Returns:
        Template do dashboard ou redirecionamento para login
    """
    # Verifica se o usuário está autenticado
    if 'usuario' not in session:
        flash("Você precisa fazer login para acessar esta página.", "error")
        return redirect(url_for('login'))

    # Redireciona para o dashboard apropriado baseado no tipo de usuário
    if session['usuario'][4] == 'admin':
        return render_template('dashboard_admin.html')

    return render_template('dashboard_usuario.html')


@app.route('/logout')
def logout():
    """
    Rota para encerrar a sessão do usuário.

    Remove os dados da sessão e redireciona para a página de login.

    Returns:
        Redirecionamento para a página de login
    """
    # Remove o usuário da sessão
    if 'usuario' in session:
        session.pop("usuario", None)
        flash("Logout realizado com sucesso!", "success")

    return redirect(url_for('login'))


# ========================================================================
# ROTAS ADMINISTRATIVAS - Apenas para usuários com perfil 'admin'
# ========================================================================

@app.route('/app/taxas/criar', methods=['GET', 'POST'])
def nova_taxa():
    """
    Rota para criar uma nova taxa de juros.

    Acesso restrito a administradores.

    GET: Exibe o formulário de criação
    POST: Processa e salva a nova taxa no banco

    Returns:
        Template de criação ou redirecionamento para lista de taxas
    """
    # Verifica se o usuário está autenticado
    if 'usuario' not in session:
        flash("Você precisa fazer login para acessar esta página.", "error")
        return redirect(url_for('login'))

    # Verifica se o usuário é administrador
    if session['usuario'][4] != 'admin':
        flash("Acesso negado. Apenas administradores podem acessar esta página.", "error")
        return redirect(url_for('dashboard'))

    # Se for GET, exibe o formulário
    if request.method == 'GET':
        return render_template('nova_taxa.html')

    # Cria um cursor para executar comandos SQL
    cursor = con.cursor()

    try:
        # Obtém os dados do formulário
        ano = request.form['ano']
        valor = request.form['taxa']
        data = date.today()
        id_usuario = session['usuario'][0]

        # Insere a nova taxa no banco de dados
        cursor.execute('INSERT INTO TAXA_JURO (ANO, TAXA_MENSAL, DATA_CRIACAO, ID_USUARIO) VALUES (?, ?, ?, ?)',
                       (ano, valor, data, id_usuario))
        con.commit()

        flash("Taxa de juros criada com sucesso!", "success")
    except Exception as e:
        flash("Erro ao criar taxa de juros. Por favor, tente novamente.", "error")
    finally:
        cursor.close()

    return redirect(url_for('taxas'))


@app.route('/app/taxas/editar/<id>', methods=['GET', 'POST'])
def editar_taxa(id):
    """
    Rota para editar uma taxa de juros existente.

    Acesso restrito a administradores.

    GET: Exibe o formulário preenchido com os dados atuais
    POST: Atualiza a taxa no banco de dados

    Args:
        id: ID da taxa a ser editada

    Returns:
        Template de edição ou redirecionamento para lista de taxas
    """
    # Verifica se o usuário está autenticado
    if 'usuario' not in session:
        flash("Você precisa fazer login para acessar esta página.", "error")
        return redirect(url_for('login'))

    # Verifica se o usuário é administrador
    if session['usuario'][4] != 'admin':
        flash("Acesso negado. Apenas administradores podem acessar esta página.", "error")
        return redirect(url_for('dashboard'))

    # Se for GET, busca os dados e exibe o formulário
    if request.method == "GET":
        cursor = con.cursor()
        dadosTaxa = None

        try:
            # Busca os dados da taxa pelo ID
            cursor.execute('SELECT ano, taxa_mensal FROM taxa_juro WHERE id_taxajuro = ?', (id,))
            dadosTaxa = cursor.fetchone()

            if not dadosTaxa:
                flash("Taxa não encontrada.", "error")
                return redirect(url_for('taxas'))
        except Exception as e:
            flash("Erro ao buscar dados da taxa.", "error")
        finally:
            cursor.close()

        return render_template('editar_taxa.html', dadosTaxa=dadosTaxa)

    # Se for POST, atualiza os dados
    cursor = con.cursor()

    try:
        # Obtém os novos dados do formulário
        vigencia = request.form['ano']
        valor = request.form['taxa']

        # Atualiza a taxa no banco de dados
        cursor.execute('UPDATE TAXA_JURO SET ano = ?, taxa_mensal = ? WHERE id_taxajuro = ?',
                       (vigencia, valor, id))
        con.commit()

        flash("Taxa atualizada com sucesso!", "success")
    except Exception as e:
        flash("Houve um erro ao atualizar as informações. Por favor, tente novamente.", "error")
    finally:
        cursor.close()

    return redirect(url_for('taxas'))


@app.route('/app/taxas/excluir/<int:id>')
def excluir_taxa(id):
    """
    Rota para excluir uma taxa de juros.

    Acesso restrito a administradores.

    Args:
        id: ID da taxa a ser excluída

    Returns:
        Redirecionamento para lista de taxas
    """
    # Verifica se o usuário é administrador
    if 'usuario' not in session or session['usuario'][4] != 'admin':
        flash("Acesso negado. Apenas administradores podem realizar esta ação.", "error")
        return redirect(url_for('dashboard'))

    # Cria um cursor para executar comandos SQL
    cursor = con.cursor()

    try:
        # Exclui a taxa do banco de dados
        cursor.execute('DELETE FROM TAXA_JURO WHERE id_taxajuro = ?', (id,))
        con.commit()

        flash("Taxa excluída com sucesso!", "success")
    except Exception as e:
        flash("Erro ao excluir taxa. Por favor, tente novamente.", "error")
    finally:
        cursor.close()

    return redirect(url_for('taxas'))


@app.route('/app/taxas')
def taxas():
    """
    Rota para listar todas as taxas de juros cadastradas.

    Requer autenticação.
    Exibe todas as taxas com informações do usuário que as criou.

    Returns:
        Template com a lista de taxas
    """
    # Verifica se o usuário está autenticado
    if 'usuario' not in session:
        flash("Você precisa fazer login para acessar esta página.", "error")
        return redirect(url_for('login'))

    todastaxas = []
    cursor = con.cursor()

    try:
        # Busca todas as taxas com JOIN para obter o nome do usuário criador
        cursor.execute('''SELECT id_taxajuro
                               , ano
                               , taxa_mensal
                               , data_criacao
                               , u.NOME
                               FROM TAXA_JURO tj
                               INNER JOIN USUARIO u ON u.ID_USUARIO = tj.ID_USUARIO''')
        todastaxas = cursor.fetchall()
    except Exception as e:
        flash("Houve um erro ao obter as taxas. Por favor, tente novamente.", "error")
    finally:
        cursor.close()

    return render_template('tabelaJuro.html', taxas=todastaxas)


@app.route('/app/simulacao/criar')
def nova_simulacao():
    """
    Rota para criar uma nova simulação de empréstimo.

    Requer autenticação.

    Returns:
        Template do formulário de simulação
    """
    # Verifica se o usuário está autenticado
    if 'usuario' not in session:
        flash("Você precisa fazer login para acessar esta página.", "error")
        return redirect(url_for('login'))

    return render_template('nova_simulacao.html')


@app.route('/app/transacoes')
def transacoes():
    """
    Rota para listar todas as transações do usuário.

    Requer autenticação.

    Returns:
        Template com a lista de transações
    """
    # Verifica se o usuário está autenticado
    if 'usuario' not in session:
        flash("Você precisa fazer login para acessar esta página.", "error")
        return redirect(url_for('login'))

    return render_template('transacoes.html')


@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    """
    Rota para editar o perfil do usuário.

    GET: Exibe o formulário de edição preenchido com dados atuais
    POST: Atualiza os dados do usuário no banco

    Validações:
    - Verifica se as senhas coincidem
    - Criptografa a nova senha
    - Atualiza a sessão com os novos dados

    Returns:
        Template de edição ou redirecionamento para dashboard
    """
    # Verifica se o usuário está autenticado
    if 'usuario' not in session:
        flash("Você precisa fazer login para acessar esta página.", "error")
        return redirect(url_for('login'))

    # Se for GET, exibe o formulário
    if request.method == 'GET':
        return render_template('editar_perfil.html')

    # Cria um cursor para executar comandos SQL
    cursor = con.cursor()

    try:
        # Obtém os dados do formulário
        nome = request.form['nome']
        email = request.form['email']
        cpf = request.form['cpf']
        senha = request.form['senha']
        confirmarSenha = request.form['confirmar']

        # Verifica se as senhas coincidem
        if senha != confirmarSenha:
            flash("As senhas não coincidem. Por favor, tente novamente.", "error")
            return redirect(url_for('perfil'))

        # Criptografa a nova senha
        hashSenha = generate_password_hash(senha).decode('utf-8')

        # Atualiza os dados do usuário no banco
        cursor.execute('''UPDATE USUARIO SET 
                       nome = ?,
                       email = ?,
                       cpf = ?,
                       senha = ?
                       WHERE id_usuario = ?
                       ''', (nome, email, cpf, hashSenha, session['usuario'][0]))

        # Busca os dados atualizados do usuário
        cursor.execute("SELECT id_usuario, nome, email, senha, tipo, tentativas, cpf FROM usuario WHERE id_usuario = ?",
                       (session['usuario'][0],))
        usuarioAtualizado = cursor.fetchone()

        # Atualiza a sessão com os novos dados
        session['usuario'] = usuarioAtualizado

        # Confirma a transação no banco
        con.commit()

        flash("Informações atualizadas com sucesso!", "success")
    except Exception as e:
        flash("Houve um erro ao atualizar as informações. Por favor, tente novamente.", "error")
    finally:
        cursor.close()

    return redirect(url_for('dashboard'))
@app.route('/nova_receita')
def nova_receita():
    return render_template('nova_receita.html')

@app.route('/nova_despesa')
def nova_despesa():
    return render_template('nova_despesa.html')

# Executa a aplicação Flask em modo de desenvolvimento
if __name__ == '__main__':
    app.run(debug=True)

