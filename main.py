from flask import Flask, render_template, redirect, session, url_for, request, flash
from flask_bcrypt import generate_password_hash, check_password_hash
import fdb

app = Flask(__name__)
app.secret_key = 'IgorELaisMeDeemNota'

host = 'localhost' 
database = r'C:\Users\Aluno\Desktop\PauloH\Looma\db\Looma.FDB'
user = 'sysdba' 
password = 'sysdba'

con = fdb.connect(host=host, database=database, user=user, password=password)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    if 'id_usuario' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'GET':
        return render_template('login.html')

    cursor = con.cursor()

    try:
        email = request.form['email']
        senha = request.form['password']

        hash_senha = generate_password_hash(senha).decode('utf-8')

        cursor.execute("SELECT id_usuario, nome, email, senha FROM usuario WHERE email = ?", (email,))
        usuario = cursor.fetchone()

        if not usuario:
            return redirect(url_for('login'))
        
        if check_password_hash(usuario[3], senha):
            session['id_usuario'] = usuario[0]
            return redirect(url_for('dashboard'))

    except Exception as e:
        flash("Houve um erro ao fazer login", "error")
    finally:
        cursor.close()

    return redirect(url_for('dashboard'))

@app.route('/auth/cadastro', methods=['GET', 'POST'])
def cadastro():
    if 'id_usuario' in session:
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
                       (email, nome, hash_senha, cpf, telefone, 'User'))
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
    if 'id_usuario' not in session:
        return redirect(url_for('login'))

    return render_template('dashboard_usuario.html')

@app.route('/logout')
def logout():
    if 'id_usuario' in session:
        session.pop("id_usuario", None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)