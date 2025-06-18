import os

from flask import Flask, render_template
from flask_migrate import Migrate
from flask_restful import Api

from .resources import (
    UserResource, CategoryResource, TransactionResource, ReportResource
)
from .utils.db import db

migrate = Migrate()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Configurations
    app.config.from_object("budgetron.config.Config")

    # Initialize database and migrations
    db.init_app(app)
    migrate.init_app(app, db)

    api = Api(app)

    # Test configuration
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Resources
    api.add_resource(UserResource, '/api/users/', '/api/users/<int:user_id>')
    api.add_resource(CategoryResource, '/api/categories/', '/api/categories/<int:category_id>')
    api.add_resource(TransactionResource, '/api/transactions/', '/api/transactions/<int:transaction_id>')
    api.add_resource(ReportResource, '/api/reports/', '/api/reports/<int:report_id>')

    # Index route
    @app.route('/')
    def index():
        return render_template("index.html")

    return app
