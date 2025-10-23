"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_migrate import Migrate
from flask_swagger import swagger
from api.utils import APIException, generate_sitemap
from api.models import db, User
from api.routes import api
from api.admin import setup_admin
from api.commands import setup_commands
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flask_jwt_extended import JWTManager, create_access_token, decode_token
from flask_cors import CORS
from sqlalchemy import select
# from models import Person

ENV = "development" if os.getenv("FLASK_DEBUG") == "1" else "production"
static_file_dir = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '../dist/')

app = Flask(__name__)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = os.getenv("MAIL_PORT")
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_USERNAME")
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

mail = Mail(app)
CORS(app)
app.url_map.strict_slashes = False

# database condiguration
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db, compare_type=True)
db.init_app(app)

# add the admin
setup_admin(app)

# add the admin
setup_commands(app)

# Add all endpoints form the API with a "api" prefix
app.register_blueprint(api, url_prefix='/api')

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    if ENV == "development":
        return generate_sitemap(app)
    return send_from_directory(static_file_dir, 'index.html')

# any other endpoint will try to serve it like a static file


@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = 'index.html'
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0  # avoid cache memory
    return response


@app.route('/api/registro', methods=['POST'])
def handle_registro():
    try:
        data = request.get_json(silent=True)
        email = data.get('email', None)
        password = data.get('password', None)

        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        user = User(email=email, password=password_hash)
        db.session.add(user)
        db.session.commit()

        token = create_access_token(identity=email, expires_delta=False)
        verify_link = f"{os.getenv('VITE_FRONTEND_URL')}/verify?token={token}"

        msg = Message("Verifica tu cuenta", recipients=[email])
        msg.body = f"Haz click en el enlace para verificar tu cuenta: {verify_link}"
        mail.send(msg)

        return jsonify({"msg": "Usuario creado correctamente"}), 201
    except Exception as error:
        print(error)
        db.session.rollback()
        return jsonify({"msg": "Hubo un error en el servidor"}), 500


@app.route('/api/verify/<token>', methods=['GET'])
def verify_token(token):
    try:
        data = decode_token(token)
        user = db.session.execute(db.select(User).filter_by(
            email=data["sub"])).scalar_one_or_none()
        if user:
            user.is_verified = True
            user.is_active = True
            db.session.commit()
            return jsonify({"msg": "Cuenta verificada con éxito"}), 200
        return jsonify({"msg": "Usuario no encontrado"}), 404
    except Exception as error:
        print(error)
        db.session.rollback()
        return jsonify({"msg": "Token inválido"}), 400


@app.route('/api/forgot', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json(silent=True)
        email = data.get('email', None)
        user = db.session.execute(db.select(User).filter_by(
            email=email)).scalar_one_or_none()

        token = create_access_token(identity=email, expires_delta=False)
        reset_link = f"{os.getenv('VITE_FRONTEND_URL')}/reset?token={token}"

        msg = Message("Recupera tu contraseña", recipients=[email])
        msg.body = f"Haz click en el enlace para cambiar tu contraseña: {reset_link}"
        mail.send(msg)

        return jsonify({"msg": "Correo enviado"}), 200

    except Exception as error:
        print(error)
        db.session.rollback()
        return jsonify({"msg": "Token inválido"}), 400


@app.route('/api/reset/<token>', methods=['POST'])
def handle_reset(token):
    try:
        decoded_data = decode_token(token)
        data = request.get_json(silent=True)
        new_password = data.get("password", None)
        print(new_password)
        email = decoded_data["sub"]
        print(email)
        user = db.session.execute(db.select(User).filter_by(
            email=email)).scalar_one_or_none()

        password_hash = bcrypt.generate_password_hash(
            new_password).decode('utf-8')
        user.password = password_hash
        db.session.commit()

        return jsonify({"msg": "Contraseña actualizada"}), 200
    except Exception as error:
        print(error)
        db.session.rollback()
        return jsonify({"msg": "Token inválido"}), 400


@app.route('/api/login', methods=['POST'])
def handle_login():
    data = request.get_json(silent=True)
    return jsonify({"msg": "Usuario inició sesión correctamente"}), 200


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)
