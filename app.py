# app.py
from flask import Flask, render_template, redirect, url_for, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
import os
from dotenv import load_dotenv
import hashlib # Нужен для SHA-256

app = Flask(__name__)
app.config['SECRET_KEY'] = 'new_year_secret_key_2024'

load_dotenv()
DB_URI = os.getenv('DATABASE_URL')
if not DB_URI:
    # ЗАМЕНИ НА СВОЮ СТРОКУ ПОДКЛЮЧЕНИЯ!!!
    DB_URI = 'postgresql://postgres.твой_юзер:твой_пароль@хост_supabase:6543/postgres' 

# Фикс для некоторых версий SQLAlchemy (postgres:// -> postgresql://)
if DB_URI and DB_URI.startswith("postgres://"):
    DB_URI = DB_URI.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Модель Базы Данных (Под Supabase) ---
class Team(UserMixin, db.Model):
    # Указываем точное имя таблицы в Supabase
    __tablename__ = 'team' 
    
    # Поля должны точно совпадать с колонками в Supabase
    # Предполагаю, что id у тебя там тоже есть (serial primary key)
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String, unique=True, nullable=False) # Было username
    password_hash = db.Column(db.String, nullable=False)     # Было password
    score = db.Column(db.Integer, default=0)

    # Flask-Login требует свойство is_active и т.д., UserMixin это делает,
    # но иногда нужно явно переопределить get_id, если id нестандартный
    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    return Team.query.get(int(user_id))

# --- Маршруты ---

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('index.html', score=current_user.score)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # В форме HTML у нас name="username" и name="password"
        input_name = request.form.get('username') 
        input_password = request.form.get('password')
        
        # 1. Ищем команду по имени (поле name в базе)
        user = Team.query.filter_by(name=input_name).first()
        
        if user:
            # 2. Хешируем введенный пароль в SHA-256
            input_hash = hashlib.sha256(input_password.encode('utf-8')).hexdigest()
            
            # 3. Сравниваем хеши
            if input_hash == user.password_hash:
                login_user(user)
                return redirect(url_for('index'))
            else:
                print(f"Неверный пароль для {input_name}") # Для отладки в консоль
        else:
            print(f"Пользователь {input_name} не найден")

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/room')
@login_required
def room():
    return render_template('room.html')

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    return send_from_directory(os.path.join(app.root_path, 'static/files'), filename, as_attachment=True)

if __name__ == '__main__':
    # create_db() удаляем, так как таблица в Supabase уже есть и мы не хотим её тереть
    # Если нужно создать таблицу с нуля через код, раскомментируй:
    # with app.app_context():
    #     db.create_all() 
    
    port = int(os.environ.get('PORT', 5000))
    debug = not os.environ.get('RENDER')
    app.run(host='0.0.0.0', port=port, debug=debug)