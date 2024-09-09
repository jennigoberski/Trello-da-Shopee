from werkzeug.security import generate_password_hash
from models import User
from extensions import db


def register_user(username, password):
    if not username or not password:
        return {"error": "Ambos os campos são obrigatórios"}

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return {"error": "Nome de usuário já está em uso"}

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    new_user = User(username=username, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return {"success": "Usuário criado com sucesso", "user": new_user}
