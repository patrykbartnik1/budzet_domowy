from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget.db'
app.config['SECRET_KEY'] = 'tajny_klucz_do_formularzy'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10))
    category = db.Column(db.String(50))
    amount = db.Column(db.Float)
    description = db.Column(db.String(200))
    receipt = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    balance = sum([t.amount if t.type == 'income' else -t.amount for t in transactions])
    return render_template('index.html', transactions=transactions, balance=balance)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        t_type = request.form['type']
        category = request.form['category']
        amount = float(request.form['amount'])
        description = request.form['description']
        receipt = request.form['receipt']
        new_transaction = Transaction(
            type=t_type, category=category, amount=amount,
            description=description, receipt=receipt, user_id=current_user.id
        )
        db.session.add(new_transaction)
        db.session.commit()
        return redirect('/')
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    transaction = Transaction.query.get_or_404(id)
    if transaction.user_id != current_user.id:
        return redirect('/')
    if request.method == 'POST':
        transaction.type = request.form['type']
        transaction.category = request.form['category']
        transaction.amount = float(request.form['amount'])
        transaction.description = request.form['description']
        transaction.receipt = request.form['receipt']
        db.session.commit()
        return redirect('/')
    return render_template('edit.html', transaction=transaction)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    transaction = Transaction.query.get_or_404(id)
    if transaction.user_id != current_user.id:
        return redirect('/')
    db.session.delete(transaction)
    db.session.commit()
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return 'Użytkownik już istnieje'
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect('/')
        return 'Nieprawidłowy login lub hasło'
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/export/pdf')
@login_required
def export_pdf():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    y = 800
    p.drawString(100, y, f"Raport PDF - Użytkownik: {current_user.username}")
    y -= 20
    for t in transactions:
        p.drawString(100, y, f"{t.type} | {t.category} | {t.amount} PLN | {t.description} | Dowód: {t.receipt}")
        y -= 20
        if y < 50:
            p.showPage()
            y = 800
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="raport.pdf", mimetype='application/pdf')

@app.route('/export/csv')
@login_required
def export_csv():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    data = [{
        'type': t.type,
        'category': t.category,
        'amount': t.amount,
        'description': t.description,
        'receipt': t.receipt
    } for t in transactions]
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="raport.csv", mimetype='text/csv')

@app.route('/chart')
@login_required
def chart():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    df = pd.DataFrame([{
        'category': t.category,
        'amount': t.amount if t.type == 'expense' else 0
    } for t in transactions])
    df = df.groupby('category').sum()
    plt.figure(figsize=(6,6))
    df.plot.pie(y='amount', autopct='%1.1f%%')
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    return send_file(buffer, mimetype='image/png')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)