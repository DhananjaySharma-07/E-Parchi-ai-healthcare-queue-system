from flask import Flask, redirect, url_for, request
from flask_login import LoginManager
import os
import threading
import webbrowser
from dotenv import load_dotenv
from sqlalchemy import text

# Load environment variables
load_dotenv('../key.env')

# Import models and database
from backend.models import db, Hospital, Doctor

# Import extensions
from backend.extensions import socketio

# Import blueprints
from backend.routes.patient_routes import patient_bp
from backend.routes.doctor_routes import doctor_bp
from backend.routes.admin_routes import admin_bp
from backend.routes.queue_routes import queue_bp
from backend.assistant.assistant_routes import assistant_bp

# Import socket handlers (registers socket events)
import backend.socket_handlers  # noqa: F401

# Import seed function
from backend.seed.seed_data import seed_database


def sync_sqlite_schema(app):
    database_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if not database_uri.startswith('sqlite:'):
        return

    existing_tables = {
        row[0]
        for row in db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
    }

    if 'token' in existing_tables:
        token_columns = {
            row[1]
            for row in db.session.execute(text('PRAGMA table_info(token)'))
        }
        missing_token_columns = {
            'priority_level': "ALTER TABLE token ADD COLUMN priority_level VARCHAR(20) DEFAULT 'NORMAL'",
            'session_type': 'ALTER TABLE token ADD COLUMN session_type VARCHAR(50)',
            'session_date': 'ALTER TABLE token ADD COLUMN session_date DATE',
        }

        for column_name, ddl in missing_token_columns.items():
            if column_name not in token_columns:
                db.session.execute(text(ddl))

    if 'patient' in existing_tables:
        patient_columns = {
            row[1]
            for row in db.session.execute(text('PRAGMA table_info(patient)'))
        }
        missing_patient_columns = {
            'severity_score': 'ALTER TABLE patient ADD COLUMN severity_score INTEGER DEFAULT 10',
            'arrival_time': 'ALTER TABLE patient ADD COLUMN arrival_time DATETIME',
            'emergency_flag': 'ALTER TABLE patient ADD COLUMN emergency_flag BOOLEAN DEFAULT 0',
            'triage_notes': 'ALTER TABLE patient ADD COLUMN triage_notes TEXT',
        }

        for column_name, ddl in missing_patient_columns.items():
            if column_name not in patient_columns:
                db.session.execute(text(ddl))

        if 'arrival_time' in patient_columns or 'arrival_time' in missing_patient_columns:
            db.session.execute(text('UPDATE patient SET arrival_time = COALESCE(arrival_time, CURRENT_TIMESTAMP)'))
        if 'severity_score' in patient_columns or 'severity_score' in missing_patient_columns:
            db.session.execute(text('UPDATE patient SET severity_score = COALESCE(severity_score, 10)'))
        if 'emergency_flag' in patient_columns or 'emergency_flag' in missing_patient_columns:
            db.session.execute(text('UPDATE patient SET emergency_flag = COALESCE(emergency_flag, 0)'))

    db.session.commit()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database
    db.init_app(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'admin.admin_login'

    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import request
        if request.path.startswith('/doctor'):
            return redirect(url_for('doctor.login'))
        elif request.path.startswith('/admin'):
            return redirect(url_for('admin.admin_login'))
        return redirect(url_for('patient.home'))

    @login_manager.user_loader
    def load_user(user_id):
        # Handle both hospital admins and doctors
        if user_id.startswith('doctor_'):
            doctor_id = int(user_id.split('_')[1])
            return Doctor.query.get(doctor_id)
        else:
            return Hospital.query.get(int(user_id))

    @app.route('/assistant')
    def assistant_redirect():
        return redirect(url_for('assistant.assistant_page'))

    # Register blueprints
    app.register_blueprint(patient_bp)
    app.register_blueprint(doctor_bp, url_prefix='/doctor')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(queue_bp, url_prefix='/queue')
    app.register_blueprint(assistant_bp, url_prefix='/api')

    # Initialize extensions
    socketio.init_app(app)

    # Create database tables and seed data
    with app.app_context():
        db.create_all()
        sync_sqlite_schema(app)
        seed_database()

    return app


# Create the app instance
app = create_app()

if __name__ == '__main__':
    host = '0.0.0.0'
    port = int(os.environ.get('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '1') == '1'

    # Camera APIs may be blocked on plain HTTP for non-localhost origins.
    # Set USE_HTTPS=1 to run with a self-signed cert during development.
    use_https = os.getenv('USE_HTTPS', '0') == '1'

    # Open browser automatically after server starts (development only)
    def open_browser():
        scheme = 'https' if use_https else 'http'
        open_port = int(os.getenv('HTTPS_PORT', '5443')) if use_https else port
        url = f'{scheme}://localhost:{open_port}'
        print(f'\n  * Opening browser at {url}')
        if os.getenv('RAILWAY_ENVIRONMENT') is None:
            webbrowser.open(url)

    if not debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        # Delay slightly so the server is ready before the browser opens
        threading.Timer(1.5, open_browser).start()

    if use_https:
        ssl_port = int(os.getenv('HTTPS_PORT', '5443'))
        socketio.run(
            app,
            debug=debug,
            host='0.0.0.0',
            port=ssl_port,
            ssl_context='adhoc',
            allow_unsafe_werkzeug=True,
        )
    else:
        socketio.run(
            app,
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 5000)),
            allow_unsafe_werkzeug=True,
        )
