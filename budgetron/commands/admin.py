import click

from flask.cli import with_appcontext
from marshmallow import ValidationError

from budgetron.models import User, Role, db
from budgetron.schemas import UserSchema


class CreateAdminCommand(click.Command):
    def __init__(self):
        super().__init__(
            name="create-admin",
            help="Create an admin user.",
            params=[
                click.Option(['--username'], prompt=True, help='Username for the admin'),
                click.Option(['--email'], prompt=True, help='Email address'),
                click.Option(
                    ['--password'], prompt=True, hide_input=True, confirmation_prompt=True,
                    help='Password for the admin'
                )
            ],
            callback=self.run
        )

    @with_appcontext
    def run(self, username, email, password):
        """Creates a new admin user."""
        user_schema = UserSchema()
        user_data = {
            'username': username,
            'email': email,
            'password': password,
            'roles': ['admin']
        }

        # Validate user_data
        try:
            user_schema.load(user_data)
        except ValidationError as err:
            click.echo(err.messages)
            return

        if User.query.filter((User.username == username) | (User.email == email)).first():
            click.echo("A user with that username or email already exists.")
            return

        user = User(username=username, email=email)
        user.set_password(password)

        # Convert role names into Role instances
        role_names = user_data['roles']
        roles = Role.query.filter(Role.name.in_(role_names)).all()

        user.roles = roles

        db.session.add(user)
        db.session.commit()

        click.echo(f"Admin '{username}' created successfully.")
