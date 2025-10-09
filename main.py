from flask import Flask, render_template, redirect, session, url_for, request, flash
from flask_bcrypt import generate_password_hash, check_password_hash
from datetime import date
import fdb

app = Flask(__name__)
app.secret_key = 'IgorELaisMeDeemNota'

host = 'localhost' 
database = r'C:\Looma\db\Looma.FDB'
user = 'sysdba' 
password = 'masterkey'

con = fdb.connect(host=host, database=database, user=user, password=password)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    if 'usuario' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'GET':
        return render_template('login.html')

    cursor = con.cursor()

    try:
        email = request.form['email']
        senha = request.form['password']

        cursor.execute("SELECT id_usuario, nome, email, senha, tipo FROM usuario WHERE email = ?", (email,))
        usuario = cursor.fetchone()

        if not usuario:
            return redirect(url_for('login'))
        
        if check_password_hash(usuario[3], senha):
            session['usuario'] = usuario
            return redirect(url_for('dashboard'))

    except Exception as e:
        flash("Houve um erro ao fazer login", "error")
    finally:
        cursor.close()

    return redirect(url_for('dashboard'))

@app.route('/auth/cadastro', methods=['GET', 'POST'])
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

        cursor.execute("SELECT id_usuario FROM usuario WHERE email = ?", (email,))
        usuario = cursor.fetchone()

        if usuario:
            cursor.close()
            return redirect(url_for('cadastro'))

        hash_senha = generate_password_hash(senha).decode('utf-8')

        cursor.execute("INSERT INTO usuario(email, nome, senha, cpf, telefone, tipo) VALUES (?, ?, ?, ?, ?, ?)", 
                       (email, nome, hash_senha, cpf, telefone, 'user'))
        con.commit()

        return redirect(url_for('login'))
    except Exception as e:
        print(e)
        return redirect(url_for('cadastro'))
    finally:
        cursor.close()

@app.route('/app')
def dashboard():
    # O usuário não pode utilizar o sistema sem estar logado
    if 'usuario' not in session:
        return redirect(url_for('login'))

    if session['usuario'][4] == 'admin':
        return render_template('dashboard_admin.html')

    return render_template('dashboard_usuario.html')

@app.route('/logout')
def logout():
    if 'usuario' in session:
        session.pop("usuario", None)
    return redirect(url_for('login'))

# APENAS ADMINS
@app.route('/app/taxas/criar', methods=['GET', 'POST'])
def nova_taxa():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if session['usuario'][4] != 'admin':
        return redirect(url_for('dashboard'))
    
    if request.method == 'GET':
        return render_template('nova_taxa.html')

    cursor = con.cursor()

    try:
        ano = request.form['ano']
        valor = request.form['taxa']
        data = date.today()
        id_usuario = session['usuario'][0]

        cursor.execute('INSERT INTO TAXA_JURO (ANO, TAXA_MENSAL, DATA_CRIACAO, ID_USUARIO) VALUES (?, ?, ?, ?)', (ano, valor, data, id_usuario))

        con.commit()
    finally:
        cursor.close()

    return redirect(url_for('taxas'))

@app.route('/app/taxas/editar/<id>', methods=['GET', 'POST'])
def editar_taxa(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if session['usuario'][4] != 'admin':
        return redirect(url_for('dashboard'))
    
    if request.method == "GET":
        cursor = con.cursor()
        dadosTaxa = None

        try:
            cursor.execute('SELECT ano, taxa_mensal FROM taxa_juro WHERE id_taxajuro = ?', (id,))
            dadosTaxa = cursor.fetchone()
        finally:
            cursor.close()

        return render_template('editar_taxa.html', dadosTaxa=dadosTaxa)
    
    cursor = con.cursor()

    try:
        vigencia = request.form['ano']
        valor = request.form['taxa']

        cursor.execute('UPDATE TAXA_JURO SET ano = ?, taxa_mensal = ? WHERE id_taxajuro = ?', (vigencia, valor, id))
        con.commit()
    finally:
        cursor.close()
    
    return redirect(url_for('taxas'))

@app.route('/app/taxas/excluir/<int:id>')
def excluir_taxa(id):
    if session['usuario'][4] == 'user':
        return redirect(url_for('dashboard'))

    cursor = con.cursor()

    try:
        cursor.execute('DELETE FROM TAXA_JURO WHERE id_taxajuro = ?', (id,))
        con.commit()
    finally:
        cursor.close()
    
    return redirect(url_for('taxas'))

@app.route('/app/taxas')
def taxas():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    todastaxas = []
    cursor = con.cursor()

    try:
        cursor.execute('SELECT id_taxajuro, ano, taxa_mensal, data_criacao, id_usuario FROM TAXA_JURO')
        taxasObtidas = cursor.fetchall()

        for taxa in taxasObtidas:
            cursor.execute('SELECT nome FROM usuario u WHERE u.id_usuario = ?', (taxa[4],))
            username = cursor.fetchone()[0]

            taxaFinal = (taxa[0], taxa[1], taxa[2], taxa[3], username)

            todastaxas.append(taxaFinal)
    finally:
        cursor.close()
    
    return render_template('tabelaJuro.html', taxas=todastaxas)

@app.route('/app/simulacao/criar')
def nova_simulacao():
    return render_template('nova_simulacao.html')

@app.route('/app/transacoes')
def transacoes():
    return render_template('transacoes.html')

@app.route('/perfil')
def perfil():
    return render_template('editar_perfil.html')

if __name__ == '__main__':
    app.run(debug=True)