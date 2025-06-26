"""This module contains custom commands for the application. """
import click
from flask.cli import with_appcontext

from budgetron.seeder.run_seeder import run_seed


class SeedCommand(click.Command):
    def __init__(self):
        super().__init__(
            name='seed',
            help="Seed data: flask seed [roles|users|categories|all]",
            params=[
                click.Argument(['name'], default='all', required=False)
            ],
            callback=self.run
        )

    @with_appcontext
    def run(self, name):
        run_seed(name)
