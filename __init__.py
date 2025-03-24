from flask import Flask
from .extensions import db, migrate, bcrypt, login_manager, mail, socketio 
from .config import Config
from os import environ
from app.cli import create_admin_command
from flask_mail import Mail
from app.routes.voter_routes import voter_routes  
from app.routes.vote_routes import vote_routes

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    socketio.init_app(app)  
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from .models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.login_view = "auth_routes.login"  
    login_manager.login_message_category = "info"  

    from .routes.main_routes import main_routes
    from .routes.auth_routes import auth_routes
    from .routes.admin_routes import admin_routes
    from app.routes.candidate_routes import candidate_routes 
    from app.routes.vote_routes import vote_routes

    app.register_blueprint(main_routes)  
    app.register_blueprint(auth_routes, url_prefix="/auth")
    app.register_blueprint(admin_routes, url_prefix="/admin")
    app.register_blueprint(voter_routes, url_prefix='/voter')  
    app.register_blueprint(candidate_routes, url_prefix='/candidate')
    app.register_blueprint(vote_routes)

    app.cli.add_command(create_admin_command)

    return app, socketio  
