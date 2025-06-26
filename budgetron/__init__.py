import os

from flask import Flask, render_template
from flask_migrate import Migrate
from flask_restful import Api

from .config import Config
from .resources import (
    LoginResource,
    RegisterResource,
    ProfileResource,
    UserResource,
    CategoryResource,
    TransactionResource,
    ReportResource
)
from .utils.db import db
from .utils.logging_config import setup_logging
from .utils.security import bcrypt
from .utils.jwt import jwt
from .seeder.run_seeder import run_seed
from .commands import create_admin, seed

migrate = Migrate()


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Configurations
    app.config.from_object("budgetron.config.Config")
    setup_logging(app)

    # App extensions
    api = Api(app)
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Create instance directory
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Resources
    api.add_resource(LoginResource, '/api/auth/login/')
    api.add_resource(RegisterResource, '/api/auth/register/')
    api.add_resource(ProfileResource, '/api/auth/me/')
    api.add_resource(UserResource, '/api/users/', '/api/users/<int:user_id>')
    api.add_resource(CategoryResource, '/api/categories/', '/api/categories/<int:category_id>')
    api.add_resource(TransactionResource, '/api/transactions/', '/api/transactions/<int:transaction_id>')
    api.add_resource(ReportResource, '/api/reports/', '/api/reports/<int:report_id>')

    # Commands
    app.cli.add_command(create_admin)
    app.cli.add_command(seed)

    # Index route
    @app.route('/')
    def index():
        return render_template("index.html")

    return app
