from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import os
import sys

# Initialize Flask extensions
db = SQLAlchemy()
jwt = JWTManager()

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__,
                static_folder='../frontend',
                static_url_path='/')

    # Load configuration directly
    if test_config is None:
        app.config.update(
            SECRET_KEY='your-development-secret-key',
            SQLALCHEMY_DATABASE_URI='sqlite:///app.db',
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            DEBUG=True,
            TESTING=False,
            JWT_SECRET_KEY='jwt-secret-key-for-token-generation'
        )
    else:
        app.config.from_mapping(test_config)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # JWT Configuration
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

    # Import and register blueprints using absolute imports
    from backend.routes.auth_routes import auth_bp
    from backend.routes.admin_routes import admin_bp
    from backend.routes.lecturer_routes import lecturer_bp
    from backend.routes.student_routes import student_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(lecturer_bp, url_prefix='/api/lecturer')
    app.register_blueprint(student_bp, url_prefix='/api/student')

    # Create database tables
    with app.app_context():
        db.create_all()

    # Root route to serve frontend
    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    # Catch-all route for SPA frontend routing
    @app.route('/<path:path>')
    def catch_all(path):
        return app.send_static_file('index.html')

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error=str(e)), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify(error=str(e)), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)