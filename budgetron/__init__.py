import os

from flask import Flask, render_template, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask_migrate import Migrate
from flask_restful import Api

from .config import Config
from .models import User
from .resources import (
    LoginResource,
    RegisterResource,
    ProfileResource,
    UserListResource,
    UserDetailResource,
    CategoryListResource,
    CategoryDetailResource,
    TransactionListResource,
    TransactionDetailResource,
    ReportListResource,
    ReportDetailResource
)
from .utils.db import db
from .utils.logging_config import setup_logging
from .utils.logging_utils import log_event
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

    # Auth Resources
    api.add_resource(LoginResource, '/api/auth/login/')
    api.add_resource(RegisterResource, '/api/auth/register/')
    api.add_resource(ProfileResource, '/api/auth/me/')

    # User resource
    api.add_resource(UserListResource, '/api/auth/users/')
    api.add_resource(UserDetailResource,  '/api/users/<int:user_id>')

    # Category resource
    api.add_resource(CategoryListResource, '/api/categories/')
    api.add_resource(CategoryDetailResource, '/api/categories/<int:category_id>')

    # Transaction resource
    api.add_resource(TransactionListResource, '/api/transactions/')
    api.add_resource(TransactionDetailResource, '/api/transactions/<int:transaction_id>')

    # Report resource
    api.add_resource(ReportListResource, '/api/reports/')
    api.add_resource(ReportDetailResource, '/api/reports/<int:report_id>')

    # Commands
    app.cli.add_command(create_admin)
    app.cli.add_command(seed)

    @app.before_request
    def load_user_from_jwt():
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            if user_id:
                g.user = User.query.get(user_id)
        except Exception as e:
            g.user = None
            log_event(action='load_user_from_jwt', level='error', status='failure', details={'msg': str(e)})

    # Index route
    @app.route('/')
    def index():
        return render_template("index.html")

    return app
