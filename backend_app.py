from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dilbilim.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Kullanıcı Modeli
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Dil Modeli
class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    code = db.Column(db.String(10))
    word_count = db.Column(db.Integer, default=0)

# Lehçe Modeli
class Dialect(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'))

# Kelime Modeli
class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100))
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'))
    dialect_id = db.Column(db.Integer, db.ForeignKey('dialect.id'), nullable=True)
    root = db.Column(db.String(50))
    suffixes = db.Column(db.String(200))
    meaning = db.Column(db.String(300))
    status = db.Column(db.String(20), default="approved")  # pending, approved, rejected
    suggested_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    etymology = db.Column(db.Text)

# Alfabe Modeli
class Alphabet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'))
    status = db.Column(db.String(20), default="pending")
    description = db.Column(db.Text)

# Basit API Endpointleri (örnekler)
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Bu e-posta ile zaten kayıt olmuşsunuz."}), 400
    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Kayıt başarılı!"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        return jsonify({"message": "Giriş başarılı!", "user_id": user.id, "is_admin": user.is_admin})
    return jsonify({"error": "Bilgiler yanlış!"}), 401

@app.route('/languages', methods=['GET'])
def get_languages():
    languages = Language.query.all()
    return jsonify([{"id": l.id, "name": l.name, "code": l.code, "word_count": l.word_count} for l in languages])

@app.route('/add_language', methods=['POST'])
def add_language():
    data = request.json
    name = data.get('name')
    code = data.get('code')
    language = Language(name=name, code=code)
    db.session.add(language)
    db.session.commit()
    return jsonify({"message": "Dil eklendi!"})

# Diğer endpointler (kelime ekleme, öneri, alfabe, etimoloji vs.) eklenebilir

if __name__ == '__main__':
    if not os.path.exists('dilbilim.db'):
        db.create_all()
    app.run(debug=True)