from flask import Flask, render_template, redirect, session, url_for, request
from flask_bcrypt import generate_password_hash
import fdb

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    if 'id_usuario' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form['email']
    senha = request.form['password']

    print(generate_password_hash(senha).decode('utf-8'))
    return redirect(url_for('dashboard'))

@app.route('/auth/cadastro', methods=['GET', 'POST'])
def cadastro():
    if 'id_usuario' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'GET':
        return render_template('cadastro.html')

@app.route('/app')
def dashboard():
    # O usuário não pode utilizar o sistema sem estar logado
    if 'id_usuario' not in session:
        return redirect(url_for('login'))

    

    return render_template('dashboard_usuario.html')

if __name__ == '__main__':
    app.run(debug=True)