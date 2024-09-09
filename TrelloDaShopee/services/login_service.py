from werkzeug.security import check_password_hash
from models import User


def login_service(username, password):
    if not username or not password:
        return False, "Por favor, preencha todos os campos.", None

    user = User.query.filter_by(username=username).first()
    if user is None:
        return False, "Nome de usuário inválido.", None

    if not check_password_hash(user.password, password):
        return False, "Senha inválida.", None

    return True, "Sucesso no login!", user.id
