import os

from flask import Flask, render_template, g, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
from jwt import ExpiredSignatureError

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
    ReportDetailResource,
    BudgetListResource,
    BudgetDetailResource,
)
from .utils.db import db
from .utils.logging_config import setup_logging
from .utils.logging_utils import log_event
from .utils.security import bcrypt
from .utils.jwt import jwt
from .commands import create_admin, seed

migrate = Migrate()


def create_app():
    app = Flask(__name__)

    # Configurations
    app.config.from_object("budgetron.config.Config")
    setup_logging(app)

    # Get the frontend URL
    frontend_url = os.getenv("FRONTEND_URL").split(',')

    # App extensions
    api = Api(app)
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": frontend_url}})

    # Ensure instance directory exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Ensure static/reports directory exists
    try:
        reports_dir = os.path.join(app.root_path, 'static', 'reports')
        os.makedirs(reports_dir)
    except OSError:
        pass

    # Auth Resources
    api.add_resource(LoginResource, '/api/auth/login/')
    api.add_resource(RegisterResource, '/api/auth/register/')
    api.add_resource(ProfileResource, '/api/auth/me/')

    # User resource
    api.add_resource(UserListResource, '/api/users/')
    api.add_resource(UserDetailResource, '/api/users/<int:user_id>')

    # Category resource
    api.add_resource(CategoryListResource, '/api/categories/')
    api.add_resource(CategoryDetailResource, '/api/categories/<int:category_id>')

    # Transaction resource
    api.add_resource(TransactionListResource, '/api/transactions/')
    api.add_resource(TransactionDetailResource, '/api/transactions/<int:transaction_id>')

    # Report resource
    api.add_resource(ReportListResource, '/api/reports/')
    api.add_resource(ReportDetailResource, '/api/reports/<int:report_id>')

    # Budget resource
    api.add_resource(BudgetListResource, '/api/budgets/')
    api.add_resource(BudgetDetailResource, '/api/budgets/<int:budget_id>')

    # Commands
    app.cli.add_command(create_admin)
    app.cli.add_command(seed)

    @app.before_request
    def load_user_from_jwt():
        # Skip for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return

        # List of unauthenticated endpoints
        unauthenticated_paths = [
            "/api/auth/login/",
            "/api/auth/register/",
        ]
        if request.path in unauthenticated_paths:
            return

        # Only try to load JWT if Authorization header is present
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            g.user = None
            return

        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            if user_id:
                g.user = User.query.get(user_id)
            else:
                g.user = None
        except ExpiredSignatureError:
            g.user = None
            log_event(action='load_user_from_jwt', level='error', status='failure', details={'msg': 'Token expired'})
        except Exception as e:
            g.user = None
            log_event(action='load_user_from_jwt', level='error', status='failure', details={'msg': str(e)})

    # Index route
    @app.route('/')
    def index():
        return render_template("index.html")

    return app
