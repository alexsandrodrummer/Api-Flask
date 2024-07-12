from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
import jwt
from functools import wraps

# Configuração do banco de dados SQLAlchemy
db = SQLAlchemy()

# Definindo a classe do usuário
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_de_usuario = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    senha = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<Usuario %r>' % self.nome_de_usuario

# Função para gerar um JWT
def gerar_jwt(payload):
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

# Função para verificar um JWT
def verificar_jwt(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return 'Token expirado. Faça login novamente.'
    except jwt.InvalidTokenError:
        return 'Token inválido. Faça login novamente.'

# Decorador para verificar o token JWT
def token_requerido(f):
    @wraps(f)
    def decorado(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'mensagem': 'Token está faltando!'}), 401
        try:
            payload = verificar_jwt(token)
        except:
            payload = 'Token inválido. Faça login novamente.'
        if not payload or isinstance(payload, str):
            return jsonify({'mensagem': payload}), 401
        return f(payload, *args, **kwargs)
    return decorado

# Rota para registrar um novo usuário
def registrar_usuario():
    data = request.get_json()
    novo_usuario = Usuario(nome_de_usuario=data['nome_de_usuario'], email=data['email'], senha=data['senha'])
    db.session.add(novo_usuario)
    db.session.commit()
    return jsonify({'mensagem': 'Usuário criado com sucesso!'}), 201

# Rota para fazer login e obter token JWT
def fazer_login():
    data = request.get_json()
    usuario = Usuario.query.filter_by(nome_de_usuario=data['nome_de_usuario'], senha=data['senha']).first()
    if usuario:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            'iat': datetime.datetime.utcnow(),
            'sub': usuario.id
        }
        token = gerar_jwt(payload)
        return jsonify({'token': token}), 200
    return jsonify({'mensagem': 'Nome de usuário ou senha inválidos!'}), 401

# Rota para obter um usuário
@token_requerido
def obter_usuario(payload, id_usuario):
    usuario = Usuario.query.get(id_usuario)
    if not usuario:
        return jsonify({'mensagem': 'Usuário não encontrado!'}), 404
    return jsonify({'nome_de_usuario': usuario.nome_de_usuario, 'email': usuario.email}), 200

# Rota para deletar um usuário
@token_requerido
def deletar_usuario(payload, id_usuario):
    usuario = Usuario.query.get(id_usuario)
    if not usuario:
        return jsonify({'mensagem': 'Usuário não encontrado!'}), 404
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({'mensagem': 'Usuário deletado com sucesso!'}), 200

# Rota para listar todos os usuários
@token_requerido
def listar_usuarios(payload):
    usuarios = Usuario.query.all()
    if not usuarios:
        return jsonify({'mensagem': 'Não há usuários cadastrados!'}), 404
    result = [{'nome_de_usuario': usuario.nome_de_usuario, 'email': usuario.email} for usuario in usuarios]
    return jsonify({'usuarios': result}), 200

# Função de criação do aplicativo Flask
def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Registro de blueprints (rotas)
    app.add_url_rule('/registro', view_func=registrar_usuario, methods=['POST'])
    app.add_url_rule('/login', view_func=fazer_login, methods=['POST'])
    app.add_url_rule('/obter_usuario/<int:id_usuario>', view_func=obter_usuario, methods=['GET'])
    app.add_url_rule('/usuario/<int:id_usuario>', view_func=deletar_usuario, methods=['DELETE'])
    app.add_url_rule('/usuarios', view_func=listar_usuarios, methods=['GET'])

    return app

# Rodando o aplicativo Flask
if __name__ == "__main__":
    app = create_app('config.DevelopmentConfig')
    app.run(port=5000, debug=True)
