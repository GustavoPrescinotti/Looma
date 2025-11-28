# Importa classes e funções do Flask para criar a app, renderizar templates, redirecionar, usar sessões, etc.
from flask import Flask, render_template, redirect, session, url_for, request, flash
# Importa funções do Flask-Bcrypt para gerar e verificar hashes de senhas.
from flask_bcrypt import generate_password_hash, check_password_hash
# Importa a classe date do módulo datetime para trabalhar com datas.
from datetime import datetime, date
from flask import send_from_directory
from werkzeug.utils import secure_filename
from fpdf import FPDF
from flask_mail import Mail, Message
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
database = r'C:\Users\Aluno\Downloads\Looma.FDB'
# Define o nome de usuário para a conexão com o banco de dados.
user = 'sysdba'
# Define a senha para a conexão com o banco de dados.
password = 'sysdba'

app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 20 * 1000 * 1000
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'loomasistema@gmail.com' # O seu e-mail
app.config['MAIL_PASSWORD'] = 'hmmghiewzrhpraus'     # Gere uma senha de app no Google
app.config['MAIL_DEFAULT_SENDER'] = 'loomasistema@gmail.com'

mail = Mail(app)






def allowed_file(filename):
    if '.' not in filename:
        return False
    extensao = filename.rsplit('.', 1)[1].lower()
    return extensao in app.config['ALLOWED_EXTENSIONS']


con = fdb.connect(host=host, database=database, user=user, password=password)


def criar_admin_fixo():
    cursor = con.cursor()
    try:

        cursor.execute("SELECT id_usuario FROM usuario WHERE email = ?", ('adm.looma@gmail.com',))
        admin_existente = cursor.fetchone()

        if not admin_existente:

            hash_senha = generate_password_hash('M8#$%oA123456789ert').decode('utf-8')


            cursor.execute(
                "INSERT INTO usuario (email, nome, senha, cpf, telefone, tipo, tentativas, ativo, foto) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ('adm.looma@gmail.com', 'Administrador Looma', hash_senha, '000.000.000-00', '(00) 00000-0000', 'admin',
                 0, True, 'default.png')
            )
            con.commit()
            print("Admin criado com sucesso!")
        else:

            cursor.execute(
                "UPDATE usuario SET foto = ? WHERE email = ?",
                ('default.png', 'adm.looma@gmail.com')
            )
            con.commit()
            print("Admin atualizado com foto padrão!")
    except Exception as e:
        print(f"Erro ao criar admin: {e}")
    finally:
        cursor.close()


def verificar_tipo_usuario():
    """Verifica se o usuário é do tipo correto para a rota"""
    if 'usuario' not in session:
        flash("Você precisa fazer login para acessar esta página.", "error")
        return redirect(url_for('login'))

    # Se for admin tentando acessar rota de usuário comum
    if session['usuario'][4] == 'admin':
        flash("Acesso negado. Administradores não podem acessar esta funcionalidade.", "error")
        return redirect(url_for('dashboard'))

    return None


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

@app.route('/contato', methods=["GET", "POST"])
def contato():
    if request.method == "POST":
        try:
            # Captura dados do formulário
            nome = request.form['name']  # Atenção: no HTML o name="name"
            email_cliente = request.form['email']
            telefone = request.form.get('phone', '')  # Telefone é opcional
            mensagem_texto = request.form['message']  # Atenção: no HTML o name="message"

            # Cria a mensagem de e-mail
            msg = Message(subject=f"Looma - Contato de {nome}",
                          recipients=['seu.email.para.receber@gmail.com'])  # Para onde vai o e-mail

            # Corpo do e-mail
            msg.body = f"""
            Nova mensagem recebida pelo site:

            Nome: {nome}
            E-mail: {email_cliente}
            Telefone: {telefone}

            Mensagem:
            {mensagem_texto}
            """

            # Envia
            mail.send(msg)
            flash("Mensagem enviada com sucesso! Entraremos em contacto em breve.", "success")

        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")
            flash("Erro ao enviar e-mail. Tente pelo WhatsApp.", "error")

        # Redireciona para o index, na secção de contacto
        return redirect(url_for('index', _anchor='contato'))

    return redirect(url_for('index'))


# Define um decorador para a URL '/auth/login', aceitando os métodos GET e POST.
@app.route('/auth/login', methods=['GET', 'POST'])
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
            "SELECT id_usuario, nome, email, senha, tipo, tentativas, cpf, ativo, telefone, foto FROM usuario WHERE email = ?",
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
            # Senha correta: cria a sessão do usuário

            # Converter para lista para poder modificar
            usuario_list = list(usuario)

            # CORREÇÃO: Se a foto for None, NoneType ou string vazia, usar 'default.png'
            if usuario_list[9] is None or usuario_list[9] == '' or usuario_list[9] == 'None':
                usuario_list[9] = 'default.png'

            # Atualizar a sessão com os dados corrigidos
            session['usuario'] = tuple(usuario_list)

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
@app.route('/auth/cadastro', methods=['GET', 'POST']) #sprint
def cadastro():
    if 'usuario' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'GET':
        return render_template('cadastro.html')

    cursor = con.cursor()

    try:
        email = request.form['email']
        nome = request.form['name']
        senha = request.form['password']
        cpf = request.form['cpf']
        telefone = request.form['phone']
        confirmar_senha = request.form['confirm_password']


        foto = 'default.png'
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    filename = f"{timestamp}_{filename}"


                    file.save(f"{app.config['UPLOAD_FOLDER']}/{filename}")
                    foto = filename
                else:
                    flash("Formato de imagem não permitido. Use apenas PNG, JPG, JPEG ou GIF.", "error")
                    return redirect(url_for('cadastro'))

        if not verificar_senha_forte(senha):
            flash(
                "A senha deve ter pelo menos 8 caracteres, uma letra maiúscula, uma letra minúscula, um número e um caractere especial.",
                "error")
            return redirect(url_for('cadastro'))

        if senha != confirmar_senha:
            flash("As senhas não coincidem. Por favor, tente novamente.", "error")
            return redirect(url_for('cadastro'))

        cursor.execute("SELECT id_usuario FROM usuario WHERE email = ?", (email,))
        usuario = cursor.fetchone()

        if usuario:
            flash("Este email já está cadastrado. Por favor, use outro email ou faça login.", "error")
            cursor.close()
            return redirect(url_for('cadastro'))

        hash_senha = generate_password_hash(senha).decode('utf-8')

        cursor.execute(
            "INSERT INTO usuario(email, nome, senha, cpf, telefone, tipo, tentativas, ativo, foto) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (email, nome, hash_senha, cpf, telefone, 'user', 0, True, foto))  # Garantir que foto nunca seja NULL
        con.commit()

        flash("Cadastro realizado com sucesso! Faça login para continuar.", "success")
    except Exception as e:
        flash(f"Não foi possível criar sua conta. Erro: {str(e)}", "error")
        return redirect(url_for('cadastro'))
    finally:
        cursor.close()

    return redirect(url_for('login'))

# Define a rota para '/app'.
@app.route('/app')
def dashboard():
    if 'usuario' not in session:
        flash("Você precisa fazer login para acessar esta página.", "error")
        return redirect(url_for('login'))

    # Se for admin, mostra o dashboard do admin
    if session['usuario'][4] == 'admin':
        cursor = con.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM usuario WHERE ativo = ?", (1,))
            usuariosAtivos = cursor.fetchone()
            total_usuarios_ativos = usuariosAtivos[0] if usuariosAtivos else 0
            return render_template('dashboard_admin.html', total_usuarios=total_usuarios_ativos)
        except Exception as e:
            flash(f"Erro ao carregar dashboard: {e}", "error")
            return redirect(url_for('login'))
        finally:
            cursor.close()
    else:
        # Se for usuário comum, mostra o dashboard do usuário
        cursor = con.cursor()
        try:
            usuario = session.get('usuario')

            if usuario is None or len(usuario) < 10:
                user_id = usuario[0] if usuario and len(usuario) > 0 else None

                if user_id:
                    cursor.execute(
                        "SELECT id_usuario, nome, email, senha, tipo, tentativas, cpf, ativo, telefone, foto FROM usuario WHERE id_usuario = ?",
                        (user_id,))
                    usuario_completo = cursor.fetchone()
                else:
                    flash("Sessão inválida. Faça login novamente.", "error")
                    session.pop('usuario', None)
                    return redirect(url_for('login'))

                if usuario_completo:
                    usuario_list = list(usuario_completo)
                    if not usuario_list[9] or usuario_list[9] == 'None':
                        usuario_list[9] = 'default.png'
                    session['usuario'] = tuple(usuario_list)
                    usuario = session['usuario']
                else:
                    flash("Erro ao carregar dados do usuário. Faça login novamente.", "error")
                    session.pop('usuario', None)
                    return redirect(url_for('login'))

            id_usuario = usuario[0]

            # CORREÇÃO: Buscar transações EXCLUINDO parcelas de empréstimo para cálculo da renda real
            cursor.execute("""
                SELECT TIPO, VALOR, DESCRICAO, DATA_TRANSACAO
                FROM TRANSACOES
                WHERE ID_USUARIO = ? 
                AND (DESCRICAO NOT LIKE '%Parcela%empréstimo%' AND DESCRICAO NOT LIKE '%Parcela%do empréstimo%')
                ORDER BY DATA_TRANSACAO DESC
            """, (id_usuario,))
            transacoes = cursor.fetchall()

            total_receitas = 0.0
            total_despesas = 0.0

            for transacao in transacoes:
                tipo = transacao[0]
                valor = float(transacao[1])

                # Calcular apenas transações reais (não parcelas de empréstimo)
                if tipo.lower() == 'receita':
                    total_receitas += valor
                elif tipo.lower() == 'despesa':
                    total_despesas += valor

            renda_liquida_real = total_receitas - total_despesas

            if renda_liquida_real <= 0:
                limite_emprestimo = 0
            else:
                limite_emprestimo = renda_liquida_real * 0.35

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

            # CORREÇÃO: Calcular despesas totais incluindo parcelas atuais
            total_despesas_com_parcelas = total_despesas + soma_parcelas_mensais

            # CORREÇÃO: Calcular renda líquida FINAL incluindo empréstimos
            renda_liquida_final = (total_receitas + valor_total_emprestimos) - total_despesas_com_parcelas

            emprestimos = {
                'valor_total': valor_total_emprestimos,
                'total_a_pagar': total_a_pagar,
                'parcelas_restantes': sum(e['parcelas_restantes'] for e in emprestimos_lista),
                'lista_emprestimos': emprestimos_lista
            }

            return render_template('dashboard_usuario.html',
                                   total_receitas=total_receitas,
                                   total_despesas=total_despesas_com_parcelas,  # Despesas + parcelas
                                   renda_liquida=renda_liquida_final,  # Renda líquida final
                                   limite_emprestimo=limite_emprestimo,  # Limite baseado na renda real
                                   emprestimos=emprestimos,
                                   valor_emprestimos=valor_total_emprestimos  # Valor total dos empréstimos
                                   )
        except Exception as e:
            flash(f"Erro ao carregar dashboard: {e}", "error")
            print(f"ERRO DETALHADO: {str(e)}")
            session.pop('usuario', None)
            return redirect(url_for('login'))
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


@app.route('/confirmar_emprestimo', methods=['POST']) #sprint
def confirmar_emprestimo():
    if 'usuario' not in session:
        flash("Você precisa fazer login para acessar esta página.", "error")
        return redirect(url_for('login'))

    resultado = verificar_tipo_usuario()
    if resultado:
        return resultado

    simulacao = session.get('simulacao_resultado')
    if not simulacao:
        flash("Nenhuma simulação encontrada. Por favor, faça uma simulação primeiro.", "error")
        return redirect(url_for('nova_simulacao'))

    if simulacao.get('risco') == 'Alto':
        flash("Não é possível confirmar empréstimos com risco alto. Por favor, ajuste os valores da simulação.",
              "error")
        return redirect(url_for('resultado_simulacao'))

    cursor = con.cursor()
    try:
        id_usuario = session['usuario'][0]

        # Dados do formulário
        valor = float(request.form['valor'])
        prazo = int(request.form['prazo'])
        parcela_mensal = float(request.form['parcela_mensal'])

        # **VALIDAÇÃO FINAL DA PARCELA vs LIMITE**
        cursor.execute("""
            SELECT TIPO, VALOR, DESCRICAO 
            FROM TRANSACOES 
            WHERE ID_USUARIO = ?
        """, (id_usuario,))
        transacoes = cursor.fetchall()

        total_receitas = 0.0
        total_despesas_atual = 0.0

        for transacao in transacoes:
            tipo = transacao[0]
            valor_transacao = float(transacao[1])
            descricao = transacao[2].lower() if transacao[2] else ""

            if 'parcela de empréstimo' not in descricao:
                if tipo.lower() == 'receita':
                    total_receitas += valor_transacao
                elif tipo.lower() == 'despesa':
                    total_despesas_atual += valor_transacao

        renda_liquida_atual = total_receitas - total_despesas_atual
        limite_parcela_mensal = renda_liquida_atual * 0.35

        # **VALIDAÇÃO FINAL - PARCELA NÃO PODE EXCEDER O LIMITE**
        if parcela_mensal > limite_parcela_mensal:
            flash(
                f"Empréstimo bloqueado: parcela mensal (R$ {parcela_mensal:.2f}) excede o limite de segurança (R$ {limite_parcela_mensal:.2f}).",
                "error")
            return redirect(url_for('resultado_simulacao'))

        # Data atual como data de contratação
        data_contratacao = date.today()

        # **ADICIONAR O EMPRÉSTIMO COMO RECEITA**
        cursor.execute("""
            INSERT INTO TRANSACOES 
            (ID_USUARIO, TIPO, VALOR, DESCRICAO, DATA_TRANSACAO, CLASSIFICACAO) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            id_usuario, 'receita', valor, f'Empréstimo contratado - {prazo} parcelas', data_contratacao, 'Empréstimo'))

        # **INSERIR TODAS AS PARCELAS COMO DESPESAS FUTURAS**
        for i in range(prazo):
            # Calcular data de vencimento de cada parcela
            meses_a_adicionar = i + 1

            # Calcular ano e mês corretamente
            ano_novo = data_contratacao.year
            mes_novo = data_contratacao.month + meses_a_adicionar

            while mes_novo > 12:
                mes_novo -= 12
                ano_novo += 1

            data_vencimento = date(ano_novo, mes_novo, 1)  # Primeiro dia do mês

            # Inserir cada parcela individualmente
            descricao_parcela = f"Parcela {i + 1}/{prazo} do empréstimo"
            cursor.execute("""
                INSERT INTO TRANSACOES 
                (ID_USUARIO, TIPO, VALOR, DESCRICAO, DATA_TRANSACAO, CLASSIFICACAO) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (id_usuario, 'despesa', parcela_mensal, descricao_parcela, data_vencimento, 'Empréstimo'))

        # Calcular próximo vencimento para o empréstimo (primeira parcela)
        if data_contratacao.month == 12:
            proximo_vencimento = date(data_contratacao.year + 1, 1, 1)
        else:
            proximo_vencimento = date(data_contratacao.year, data_contratacao.month + 1, 1)

        # Inserir registro do empréstimo
        cursor.execute("""
            INSERT INTO EMPRESTIMOS 
            (ID_USUARIO, VALOR_EMPRESTIMO, PARCELAS_RESTANTES, PROXIMO_VENCIMENTO, 
             PARCELA_MENSAL, STATUS, DATA_CONTRATACAO) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id_usuario, valor, prazo, proximo_vencimento, parcela_mensal, 'ativo', data_contratacao))

        con.commit()

        # Limpar a simulação da sessão após confirmar
        if 'simulacao_resultado' in session:
            session.pop('simulacao_resultado')

        flash(f"Empréstimo contratado com sucesso! {prazo} parcelas de R$ {parcela_mensal:.2f} foram agendadas.",
              "success")

    except Exception as e:
        flash(f"Erro ao confirmar empréstimo: {e}", "error")
        con.rollback()  # Reverter em caso de erro
    finally:
        cursor.close()

    return redirect(url_for('dashboard'))


@app.route('/app/simulacao/criar', methods=['GET', 'POST'])
def nova_simulacao():
    if 'usuario' not in session:
        flash("Você precisa fazer login para acessar esta página.", "error")
        return redirect(url_for('login'))

    resultado = verificar_tipo_usuario()
    if resultado:
        return resultado

    cursor = con.cursor()
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

        # **CORREÇÃO DEFINITIVA DA FÓRMULA**
        i = float(taxa[0]) / 100  # Taxa mensal em decimal
        PV = valor  # Valor presente (valor do empréstimo)
        n = prazo  # Número de parcelas

        # Fórmula correta do sistema price (parcelas fixas)
        if i == 0:
            PMT = PV / n
        else:
            # Fórmula: PMT = PV * i / (1 - (1 + i)^-n)
            PMT = (PV * i) / (1 - (1 + i) ** -n)

        total_pagar = PMT * n
        juros_total = total_pagar - PV
        lucro_mensal = juros_total / n

        # **BUSCAR LIMITE REAL DO DASHBOARD**
        cursor.execute("""
            SELECT TIPO, VALOR, DESCRICAO 
            FROM TRANSACOES 
            WHERE ID_USUARIO = ?
            AND (DESCRICAO NOT LIKE '%Parcela%empréstimo%' AND DESCRICAO NOT LIKE '%Parcela%do empréstimo%')
        """, (id_usuario,))
        transacoes = cursor.fetchall()

        total_receitas = 0.0
        total_despesas_atual = 0.0

        for transacao in transacoes:
            tipo = transacao[0]
            valor_transacao = float(transacao[1])

            if tipo.lower() == 'receita':
                total_receitas += valor_transacao
            elif tipo.lower() == 'despesa':
                total_despesas_atual += valor_transacao

        renda_liquida_atual = total_receitas - total_despesas_atual

        # **LIMITE CORRETO (35% da renda líquida)**
        limite_parcela_mensal = renda_liquida_atual * 0.35
        if limite_parcela_mensal < 0:
            limite_parcela_mensal = 0

        # **VERIFICAÇÃO CORRETA DA PARCELA vs LIMITE**
        if PMT > limite_parcela_mensal:
            # Calcular comprometimento para determinar o risco
            comprometimento = (PMT / renda_liquida_atual) * 100 if renda_liquida_atual > 0 else 0

            # Determinar nível de risco
            if comprometimento < 20:
                risco = "Baixo"
            elif comprometimento <= 35:
                risco = "Médio"
            else:
                risco = "Alto"

            # **MENSAGEM CORRIGIDA - MOSTRANDO VALORES REAIS**
            flash(f"Parcela mensal calculada: R$ {PMT:,.2f} excede seu limite: R$ {limite_parcela_mensal:,.2f} e seu risco está {risco}. Reduza o valor ou aumente o prazo do empréstimo. ", "error")
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

        # Salvar na sessão
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
            'limite_parcela': limite_parcela_mensal,
            'data_criacao': datetime.now().strftime('%d/%m/%Y')
        }

        return redirect(url_for('resultado_simulacao'))

    except Exception as e:
        flash(f'Erro ao processar simulação: {str(e)}', "error")
        return render_template('nova_simulacao.html', admins=admins, current_year=current_year,
                               current_date=current_date)
    finally:
        cursor.close()

# Define a rota para '/app/simulacao/criar'.
@app.route('/app/simulacao/resultado') #sprint
def resultado_simulacao():
    if 'usuario' not in session:
        flash("Você precisa fazer login para acessar esta página.", "error")
        return redirect(url_for('login'))

    resultado = verificar_tipo_usuario()
    if resultado:
        return resultado

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
                           limite_parcela=simulacao['limite_parcela'],
                           data_criacao=simulacao['data_criacao'])

# Define a rota para '/app/transacoes'.
# Define a rota '/app/transacoes' para acessar a página de transações
@app.route('/app/transacoes')
def transacoes():
    if 'usuario' not in session:
        flash("Você precisa fazer login para acessar esta página.", "error")
        return redirect(url_for('login'))
    resultado = verificar_tipo_usuario()
    if resultado:
        return resultado

    id_usuario = session['usuario'][0]
    cursor = con.cursor()
    try:
        # Query mais simples sem comentários
        cursor.execute("SELECT ID_TRANSACOES, TIPO, VALOR, DESCRICAO, DATA_TRANSACAO, CLASSIFICACAO FROM TRANSACOES WHERE ID_USUARIO = ? ORDER BY DATA_TRANSACAO ASC", (id_usuario,))
        transacoes_raw = cursor.fetchall()

        transacoes = []
        saldo = 0.0

        for t in transacoes_raw:
            dt = t[4]
            if isinstance(dt, str):
                try:
                    dt_obj = datetime.strptime(dt.split()[0], '%Y-%m-%d')
                except:
                    dt_obj = None
            else:
                dt_obj = dt

            data_formatada = dt_obj.strftime('%d/%m/%Y') if dt_obj else 'Data inválida'

            # Verificar se é transação futura
            hoje = date.today()
            if dt_obj:
                data_transacao = dt_obj.date() if hasattr(dt_obj, 'date') else dt_obj
                is_futura = data_transacao > hoje
            else:
                is_futura = False

            transacoes.append((t[0], t[1], float(t[2]), t[3], data_formatada, t[5], is_futura))

            # Calcular saldo apenas para transações não futuras
            if not is_futura:
                if t[1].lower() == 'receita':
                    saldo += float(t[2])
                else:
                    saldo -= float(t[2])

    except Exception as e:
        flash(f"Erro ao carregar transações: {e}", "error")
        transacoes = []
        saldo = 0.0
    finally:
        cursor.close()

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

    resultado = verificar_tipo_usuario()
    if resultado:
        return resultado

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
        classificacao = request.form['classificacao']

        # NOVO: Verificar se é transação fixa
        eh_fixa = True if classificacao == 'Fixa' else False

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

            # VALIDAÇÃO: Verificar se a data não é anterior ao dia atual
            data_hoje = datetime.now().date()
            if data_obj.date() < data_hoje:
                flash("Não é permitido cadastrar receitas com data retroativa.", "error")
                return redirect(url_for('nova_receita'))

            # Cria cursor para executar queries no banco
            cursor = con.cursor()
            # Executa query para inserir nova transação na tabela
            cursor.execute("""
                INSERT INTO TRANSACOES (ID_USUARIO, TIPO, VALOR, DESCRICAO, DATA_TRANSACAO, CLASSIFICACAO, EH_FIXA)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (id_usuario, tipo, valor, descricao, data_formatada, classificacao, eh_fixa))
            # Confirma a transação no banco de dados
            con.commit()

            # Mensagem personalizada baseada no tipo de transação
            if eh_fixa:
                flash("Receita fixa cadastrada com sucesso! Ela será repetida mensalmente nos relatórios.", "success")
            else:
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
@app.route('/perfil', methods=['GET', 'POST']) #perfil
def perfil():
    if 'usuario' not in session:
        flash("Você precisa fazer login para acessar esta página.", "error")
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('editar_perfil.html')

    cursor = con.cursor()

    try:
        nome = request.form['nome']
        email = request.form['email']
        cpf = request.form["cpf"]
        telefone = request.form["telefone"]
        senha = request.form["senha"]
        confirmarSenha = request.form['confirmar']

        nova_foto = None
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    filename = f"{timestamp}_{filename}"

                    # Salva o arquivo
                    file.save(f"{app.config['UPLOAD_FOLDER']}/{filename}")
                    nova_foto = filename
                else:
                    flash("Formato de imagem não permitido. Use apenas PNG, JPG, JPEG ou GIF.", "error")
                    return redirect(url_for('perfil'))

        # Resto da lógica permanece igual...
        if senha:
            if not verificar_senha_forte(senha):
                flash("A nova senha deve ter pelo menos 8 caracteres, uma letra maiúscula, uma letra minúscula, um número e um caractere especial.", "error")
                return redirect(url_for('perfil'))

            if senha != confirmarSenha:
                flash("As senhas não coincidem. Por favor, tente novamente.", "error")
                return redirect(url_for('perfil'))

            hashSenha = generate_password_hash(senha).decode('utf-8')

            if nova_foto:
                cursor.execute(
                    '''UPDATE USUARIO SET nome=?, email=?, cpf=?, telefone=?, senha=?, foto=? WHERE id_usuario=?''',
                    (nome, email, cpf, telefone, hashSenha, nova_foto, session['usuario'][0]))
            else:
                cursor.execute('''UPDATE USUARIO SET nome=?, email=?, cpf=?, telefone=?, senha=? WHERE id_usuario=?''',
                               (nome, email, cpf, telefone, hashSenha, session['usuario'][0]))
        else:
            if nova_foto:
                cursor.execute('''UPDATE USUARIO SET nome=?, email=?, cpf=?, telefone=?, foto=? WHERE id_usuario=?''',
                               (nome, email, cpf, telefone, nova_foto, session['usuario'][0]))
            else:
                cursor.execute('''UPDATE USUARIO SET nome=?, email=?, cpf=?, telefone=? WHERE id_usuario=?''',
                               (nome, email, cpf, telefone, session['usuario'][0]))

        con.commit()

        cursor.execute(
            "SELECT id_usuario, nome, email, senha, tipo, tentativas, cpf, ativo, telefone, foto FROM usuario WHERE id_usuario = ?",
            (session["usuario"][0],))
        usuarioAtualizado = cursor.fetchone()
        session["usuario"] = usuarioAtualizado

        flash("Informações atualizadas com sucesso!", "success")
        return redirect(url_for('dashboard'))

    except Exception as e:
        flash(f"Houve um erro ao atualizar as informações: {e}", "error")
    finally:
        cursor.close()

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

    resultado = verificar_tipo_usuario()
    if resultado:
        return resultado

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

        # NOVO: Verificar se é transação fixa
        eh_fixa = True if classificacao == 'Fixa' else False

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

            # VALIDAÇÃO: Verificar se a data não é anterior ao dia atual
            data_hoje = datetime.now().date()
            if data_obj.date() < data_hoje:
                flash("Não é permitido cadastrar despesas com data retroativa.", "error")
                return redirect(url_for('nova_despesa'))

            # Cria cursor para executar queries no banco
            cursor = con.cursor()
            # Executa query para inserir nova transação na tabela TRANSACOES
            cursor.execute("""
                INSERT INTO TRANSACOES (ID_USUARIO, TIPO, VALOR, DESCRICAO, DATA_TRANSACAO, CLASSIFICACAO, EH_FIXA)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (id_usuario, tipo, valor, descricao, data_formatada, classificacao, eh_fixa))
            # Confirma a transação no banco de dados
            con.commit()

            # Mensagem personalizada baseada no tipo de transação
            if eh_fixa:
                flash("Despesa fixa cadastrada com sucesso! Ela será repetida mensalmente nos relatórios.", "success")
            else:
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

    resultado = verificar_tipo_usuario()
    if resultado:
        return resultado

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
        cursor.execute("SELECT id_usuario, nome, email, tipo, tentativas, ativo, cpf, telefone FROM usuario ORDER BY id_usuario ASC")
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

@app.route("/simulacao/criar", methods=['POST']) #sprint
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


@app.route('/app/admin/emprestimos-por-mes')
def emprestimos_por_mes():
    if 'usuario' not in session or session['usuario'][4] != 'admin':
        return {'success': False, 'error': 'Acesso negado'}

    cursor = con.cursor()
    try:
        # ALTERNATIVA COMPATÍVEL: Buscar todos os empréstimos do ano atual e processar em Python
        cursor.execute("""
            SELECT DATA_CONTRATACAO
            FROM EMPRESTIMOS 
            WHERE EXTRACT(YEAR FROM DATA_CONTRATACAO) = EXTRACT(YEAR FROM CURRENT_DATE)
        """)

        resultados = cursor.fetchall()

        # Inicializar array com 12 meses (todos zero)
        emprestimos_por_mes = [0] * 12

        # Processar os resultados em Python
        for row in resultados:
            data_contratacao = row[0]
            if data_contratacao:
                # Extrair o mês da data
                if isinstance(data_contratacao, str):
                    try:
                        # Se for string, converter para datetime
                        data_obj = datetime.strptime(data_contratacao.split()[0], '%Y-%m-%d')
                        mes = data_obj.month
                    except:
                        continue
                else:
                    # Se já for objeto de data
                    mes = data_contratacao.month

                if 1 <= mes <= 12:
                    emprestimos_por_mes[mes - 1] += 1

        return {
            'success': True,
            'emprestimosPorMes': emprestimos_por_mes
        }

    except Exception as e:
        print(f"Erro na query emprestimos_por_mes: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        cursor.close()

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/app/relatorios') #sprint
def relatorios():
    if 'usuario' not in session:
        flash("Você precisa fazer login para acessar esta página.", "error")
        return redirect(url_for('login'))
    return render_template('relatorios.html')


# --- ADICIONE ESTA CLASSE ANTES DAS ROTAS DE RELATÓRIO ---

class PDFPersonalizado(FPDF):
    def header(self):
        # Logo (Caminho, x, y, largura)
        # Ajuste o caminho conforme necessário. Se der erro, use o caminho completo (r'C:\...')
        try:
            self.image('static/img/Logo_pdf.png', 10, 9, 33)
        except:
            pass  # Se não achar a logo, segue sem ela

        # Fonte Arial Bold 15
        self.set_font('Arial', 'B', 15)
        # Move para a direita
        self.cell(80)
        # Título
        self.set_text_color(44, 62, 80)  # Cor Azul Escuro (RGB)
        self.cell(30, 10, 'Relatório de Empréstimos', 0, 0, 'C')
        # Quebra de linha
        self.ln(35)

        # Linha divisória colorida



    def footer(self):
        # Posiciona a 1.5 cm do fim da página
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)  # Cinza
        # Número da página
        self.cell(0, 10, 'Página ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')


# --- ATUALIZE A SUA ROTA DE EMPRÉSTIMOS ---

@app.route('/app/relatorios/emprestimos', methods=['GET', 'POST'])
def relatorio_emprestimos():
    if 'usuario' not in session:
        flash("Faça login.", "error")
        return redirect(url_for('login'))

    # Configuração de Datas (Padrão: Ano Atual)
    if request.method == 'GET':
        ano = datetime.now().year
        data_inicio = f"{ano}-01-01"
        data_fim = f"{ano}-12-31"
    else:
        data_inicio = request.form.get('data_inicio')
        data_fim = request.form.get('data_fim')

    cursor = con.cursor()
    try:
        id_usuario = session['usuario'][0]
        eh_admin = session['usuario'][4] == 'admin'

        # Query para buscar parcelas de empréstimo dentro do período
        # Filtra por CLASSIFICACAO='Empréstimo' ou descricao contendo 'Parcela'
        query = """
            SELECT t.DATA_TRANSACAO, t.VALOR, t.DESCRICAO, u.NOME
            FROM TRANSACOES t
            JOIN USUARIO u ON t.ID_USUARIO = u.ID_USUARIO
            WHERE (t.CLASSIFICACAO = 'Empréstimo' OR t.DESCRICAO LIKE '%Parcela%')
            AND t.DATA_TRANSACAO BETWEEN ? AND ?
        """
        params = [data_inicio, data_fim]

        if not eh_admin:
            query += " AND t.ID_USUARIO = ?"
            params.append(id_usuario)

        query += " ORDER BY t.DATA_TRANSACAO ASC"

        cursor.execute(query, tuple(params))
        parcelas = cursor.fetchall()

        # Agrupamento por Mês
        dados_por_mes = {}
        meses_nomes = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
                       7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}

        total_geral = 0.0

        for p in parcelas:
            # Tratamento de data
            dt_trans = p[0]
            if isinstance(dt_trans, str): dt_trans = datetime.strptime(dt_trans.split()[0], '%Y-%m-%d')

            # Chave: "Janeiro 2025"
            chave = f"{meses_nomes[dt_trans.month]} {dt_trans.year}"

            if chave not in dados_por_mes:
                dados_por_mes[chave] = {'itens': [], 'total': 0.0}

            valor = float(p[1])
            dados_por_mes[chave]['itens'].append({
                'data': dt_trans.strftime('%d/%m/%Y'),
                'valor': valor,
                'descricao': p[2],
                'nome': p[3]
            })
            dados_por_mes[chave]['total'] += valor
            total_geral += valor

        # Geração do PDF
        pdf = PDFPersonalizado()
        pdf.alias_nb_pages()
        pdf.add_page()

        # Cabeçalho de Informações
        pdf.set_font('Arial', '', 10)
        di_fmt = datetime.strptime(data_inicio, '%Y-%m-%d').strftime('%d/%m/%Y')
        df_fmt = datetime.strptime(data_fim, '%Y-%m-%d').strftime('%d/%m/%Y')
        pdf.cell(0, 6, f'Período: {di_fmt} até {df_fmt}', 0, 1)
        pdf.cell(0, 6, f'Gerado por: {session["usuario"][1]}', 0, 1)
        pdf.ln(5)

        if not dados_por_mes:
            pdf.set_font('Arial', 'I', 12)
            pdf.cell(0, 10, 'Nenhuma parcela encontrada neste período.', 0, 1, 'C')
        else:
            # Loop pelos meses
            for mes_ano, dados in dados_por_mes.items():
                qtd = len(dados['itens'])

                # Título do Mês (Destaque conforme pedido)
                # Ex: "Janeiro 2025 - 3 parcelas - Total: R$ 500.00"
                pdf.set_font('Arial', 'B', 12)
                pdf.set_fill_color(52, 152, 219)  # Azul
                pdf.set_text_color(255, 255, 255)  # Branco
                titulo = f"{mes_ano} - {qtd} parcelas - Total: R$ {dados['total']:,.2f}"
                pdf.cell(0, 8, titulo, 0, 1, 'L', True)

                # Cabeçalho da Tabela
                pdf.set_font('Arial', 'B', 9)
                pdf.set_text_color(0, 0, 0)
                pdf.set_fill_color(230, 230, 230)

                # Larguras das colunas
                cw = [30, 90, 40] if not eh_admin else [30, 70, 40, 20]  # Ajuste se for admin

                pdf.cell(30, 6, 'Vencimento', 1, 0, 'C', True)
                pdf.cell(90 if not eh_admin else 60, 6, 'Descrição', 1, 0, 'L', True)
                if eh_admin: pdf.cell(50, 6, 'Cliente', 1, 0, 'L', True)
                pdf.cell(0, 6, 'Valor', 1, 1, 'R', True)  # 0 vai até o fim da linha

                # Linhas
                pdf.set_font('Arial', '', 9)
                for item in dados['itens']:
                    pdf.cell(30, 6, item['data'], 1, 0, 'C')
                    pdf.cell(90 if not eh_admin else 60, 6, item['descricao'][:40], 1, 0, 'L')
                    if eh_admin: pdf.cell(50, 6, item['nome'][:25], 1, 0, 'L')
                    pdf.cell(0, 6, f"R$ {item['valor']:,.2f}", 1, 1, 'R')

                pdf.ln(5)  # Espaço entre meses

            # Total Geral
            pdf.ln(5)
            pdf.set_font('Arial', 'B', 12)
            pdf.set_fill_color(44, 62, 80)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(0, 10, f"TOTAL GERAL: R$ {total_geral:,.2f}", 0, 1, 'R', True)

        filename = f"fluxo_emprestimos_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        pdf.output(f"uploads/{filename}")
        return send_from_directory('uploads', filename, as_attachment=True)

    except Exception as e:
        flash(f"Erro ao gerar relatório: {e}", "error")
        print(f"ERRO PDF: {e}")
        return redirect(url_for('relatorios'))
    finally:
        cursor.close()


@app.route('/app/relatorios/transacoes', methods=['POST'])
def relatorio_transacoes():
    if 'usuario' not in session:
        flash("Você precisa fazer login para acessar esta página.", "error")
        return redirect(url_for('login'))

    data_inicio = request.form['data_inicio']
    data_fim = request.form['data_fim']

    cursor = con.cursor()

    try:
        id_usuario = session['usuario'][0]

        # 1. Busca transações no banco
        try:
            cursor.execute("""
                SELECT tipo, valor, descricao, data_transacao, classificacao, eh_fixa
                FROM transacoes
                WHERE id_usuario = ? 
                ORDER BY data_transacao ASC
            """, (id_usuario,))
        except fdb.DatabaseError as db_err:
            if "Column unknown" in str(db_err):
                cursor.execute("""
                    SELECT tipo, valor, descricao, data_transacao, classificacao, 0
                    FROM transacoes
                    WHERE id_usuario = ? 
                    ORDER BY data_transacao ASC
                """, (id_usuario,))
            else:
                raise db_err

        todas_transacoes = cursor.fetchall()

        # 2. Processamento: Expandir Fixas e Filtrar por Data
        data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()

        transacoes_finais = []

        for transacao in todas_transacoes:
            tipo, valor, descricao, data_transacao, classificacao, eh_fixa = transacao

            # Garante que é objeto date
            if isinstance(data_transacao, str):
                data_base = datetime.strptime(data_transacao.split()[0], '%Y-%m-%d').date()
            else:
                data_base = data_transacao.date() if hasattr(data_transacao, 'date') else data_transacao

            valor_float = float(valor)
            eh_fixa_bool = bool(eh_fixa)

            if eh_fixa_bool:
                # Lógica para REPETIR transações fixas (Salário, Aluguel, etc) mês a mês
                data_atual = data_base

                # Avança a data até chegar perto do inicio selecionado para não processar anos passados desnecessariamente
                while data_atual < data_inicio_obj:
                    # Avança um mês
                    mes = data_atual.month
                    ano = data_atual.year
                    if mes == 12:
                        mes = 1
                        ano += 1
                    else:
                        mes += 1
                    try:
                        data_atual = date(ano, mes, data_atual.day)
                    except ValueError:
                        data_atual = date(ano, mes, 28)

                # Agora adiciona enquanto estiver dentro do prazo final
                while data_atual <= data_fim_obj:
                    if data_atual >= data_inicio_obj:
                        transacoes_finais.append({
                            'tipo': tipo,
                            'valor': valor_float,
                            'descricao': f"{descricao} (Fixo)",
                            'data': data_atual,
                            'classificacao': classificacao
                        })

                    # Avança um mês para a próxima iteração
                    mes = data_atual.month
                    ano = data_atual.year
                    if mes == 12:
                        mes = 1
                        ano += 1
                    else:
                        mes += 1
                    try:
                        data_atual = date(ano, mes, data_atual.day)
                    except ValueError:
                        data_atual = date(ano, mes, 28)

            else:
                # Transações normais (incluindo parcelas de empréstimo já lançadas individualmente no banco)
                if data_inicio_obj <= data_base <= data_fim_obj:
                    transacoes_finais.append({
                        'tipo': tipo,
                        'valor': valor_float,
                        'descricao': descricao,
                        'data': data_base,
                        'classificacao': classificacao
                    })

        # 3. Agrupamento por Mês (Igual ao Relatório de Empréstimos)
        # Ordena por data para garantir a ordem cronológica
        transacoes_finais.sort(key=lambda x: x['data'])

        dados_por_mes = {}
        meses_nomes = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
                       7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}

        saldo_geral_periodo = 0.0

        for item in transacoes_finais:
            dt = item['data']
            chave_mes = f"{meses_nomes[dt.month]} {dt.year}"

            # Calcula impacto no saldo
            val = item['valor']
            if item['tipo'].lower() == 'despesa':
                val = -val

            saldo_geral_periodo += val

            if chave_mes not in dados_por_mes:
                dados_por_mes[chave_mes] = {'itens': [], 'saldo_mensal': 0.0}

            dados_por_mes[chave_mes]['itens'].append(item)
            dados_por_mes[chave_mes]['saldo_mensal'] += val

        # ==============================================================================
        # GERAÇÃO DO PDF (Visual Agrupado por Mês)
        # ==============================================================================

        pdf = PDFPersonalizado()
        pdf.alias_nb_pages()
        pdf.add_page()

        # Cabeçalho do Relatório
        pdf.set_font('Arial', '', 10)
        di_fmt = data_inicio_obj.strftime('%d/%m/%Y')
        df_fmt = data_fim_obj.strftime('%d/%m/%Y')

        pdf.cell(0, 6, f'Período: {di_fmt} a {df_fmt}', 0, 1)
        pdf.cell(0, 6, f'Cliente: {session["usuario"][1]}', 0, 1)
        pdf.ln(5)

        # Saldo Total do Período no topo
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(40, 10, 'Saldo do Período: ', 0, 0)
        if saldo_geral_periodo >= 0:
            pdf.set_text_color(39, 174, 96)  # Verde
        else:
            pdf.set_text_color(192, 57, 43)  # Vermelho
        pdf.cell(0, 10, f'R$ {saldo_geral_periodo:,.2f}', 0, 1)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

        if not dados_por_mes:
            pdf.set_font('Arial', 'I', 12)
            pdf.cell(0, 10, 'Nenhuma transação encontrada neste período.', 0, 1, 'C')
        else:
            # Loop pelos Meses (Janeiro, Fevereiro...)
            for mes_ano, dados in dados_por_mes.items():
                qtd = len(dados['itens'])
                saldo_mes = dados['saldo_mensal']

                # --- Cabeçalho do Mês (Azul) ---
                pdf.set_font('Arial', 'B', 12)
                pdf.set_fill_color(52, 152, 219)  # Azul
                pdf.set_text_color(255, 255, 255)  # Branco

                # Texto do título do mês (Ex: Janeiro 2025 - Saldo: R$ 500.00)
                titulo = f"{mes_ano} - Saldo Mensal: R$ {saldo_mes:,.2f}"
                pdf.cell(0, 8, titulo, 0, 1, 'L', True)

                # --- Cabeçalho da Tabela ---
                pdf.set_font('Arial', 'B', 9)
                pdf.set_text_color(0, 0, 0)
                pdf.set_fill_color(230, 230, 230)  # Cinza claro

                # Larguras: Data, Tipo, Descrição, Valor
                col_w = [25, 25, 110, 30]

                pdf.cell(col_w[0], 6, 'Data', 1, 0, 'C', True)
                pdf.cell(col_w[1], 6, 'Tipo', 1, 0, 'C', True)
                pdf.cell(col_w[2], 6, 'Descrição', 1, 0, 'L', True)
                pdf.cell(col_w[3], 6, 'Valor', 1, 1, 'R', True)

                # --- Itens do Mês ---
                pdf.set_font('Arial', '', 9)
                fill = False  # Alternar cores

                for item in dados['itens']:
                    if fill:
                        pdf.set_fill_color(245, 245, 245)
                    else:
                        pdf.set_fill_color(255, 255, 255)

                    data_fmt = item['data'].strftime('%d/%m/%Y')
                    tipo = item['tipo'].capitalize()

                    # Cor do Texto do Tipo
                    if tipo.lower() == 'receita':
                        pdf.set_text_color(39, 174, 96)
                    else:
                        pdf.set_text_color(192, 57, 43)

                    pdf.cell(col_w[0], 6, data_fmt, 1, 0, 'C', fill)
                    pdf.cell(col_w[1], 6, tipo, 1, 0, 'C', fill)

                    # Volta para preto para o resto
                    pdf.set_text_color(0, 0, 0)
                    pdf.cell(col_w[2], 6, item['descricao'][:55], 1, 0, 'L', fill)
                    pdf.cell(col_w[3], 6, f"R$ {item['valor']:,.2f}", 1, 1, 'R', fill)

                    fill = not fill

                pdf.ln(5)  # Espaço entre os meses

        filename = f'relatorio_transacoes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        pdf.output(f"uploads/{filename}")

        return send_from_directory('uploads', filename, as_attachment=True)

    except Exception as e:
        print(f"Erro PDF: {str(e)}")
        flash(f'Erro ao gerar relatório: {e}', 'error')
        return redirect(url_for('relatorios'))
    finally:
        cursor.close()
if __name__ == '__main__':
    criar_admin_fixo()
    # Inicia o servidor de desenvolvimento do Flask com o modo de depuração ativado.
    app.run(debug=True)

