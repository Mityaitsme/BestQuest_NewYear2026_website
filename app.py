# app.py
from flask import Flask, render_template, redirect, url_for, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'new_year_secret_key_2024' # Любой секретный ключ
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Модель Базы Данных ---
class Team(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(150), unique=True, nullable=False)
  password = db.Column(db.String(150), nullable=False)
  score = db.Column(db.Integer, default=0) # Счет команды

@login_manager.user_loader
def load_user(user_id):
  return Team.query.get(int(user_id))

# --- Маршруты ---

@app.route('/')
def index():
  if not current_user.is_authenticated:
    return redirect(url_for('login'))
  
  # Передаем счет в шаблон, чтобы показывать/скрывать оленя
  return render_template('index.html', score=current_user.score)

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    username = request.form.get('username')
    password = request.form.get('password')
    user = Team.query.filter_by(username=username).first()
    
    # Простая проверка пароля (для квеста норм, в продакшене лучше хешировать)
    if user and user.password == password:
      login_user(user)
      return redirect(url_for('index'))
  return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect(url_for('login'))

@app.route('/room')
@login_required
def room():
  # Сюда можно добавить проверку, имеет ли право команда сюда заходить
  return render_template('room.html')

# Маршрут для скачивания файла
@app.route('/download/<filename>')
@login_required
def download_file(filename):
  return send_from_directory(os.path.join(app.root_path, 'static/files'), filename, as_attachment=True)

# Функция для создания базы данных и тестового юзера
def create_db():
  with app.app_context():
    db.create_all()
    if not Team.query.filter_by(username='team1').first():
      # Создаем тестовую команду: логин team1, пароль 1234, счет 100
      new_team = Team(username='team1', password='1234', score=100)
      db.session.add(new_team)
      db.session.commit()
      print("База создана, пользователь team1 добавлен")

if __name__ == '__main__':
	# Всегда 0.0.0.0 - будет работать везде!
	# Но debug только локально
	create_db()
	port = int(os.environ.get('PORT', 5000))
	debug = not os.environ.get('RENDER')  # True локально, False на Render
	app.run(host='0.0.0.0', port=port, debug=debug)