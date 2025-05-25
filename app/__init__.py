
from flask import Flask, jsonify
from flask_migrate import Migrate
from config import Config
from app.db import db
from app.auth import auth_bp, token_required


migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)


    app.config['SECRET_KEY'] = 'your secret key'

    db.init_app(app)
    migrate.init_app(app, db)


    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    app.register_blueprint(auth_bp, url_prefix='/auth')

    #tratamento de erros
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'message': 'Bad request'}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'message': 'Unauthorized request'}), 401

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'message': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({'message': 'Internal server error'}), 500

    @app.errorhandler(503)
    def service_unavailable(error):
        return jsonify({'message': 'Service unavailable'}), 503

    return app