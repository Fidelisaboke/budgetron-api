from budgetron.seeder.seed_roles import seed_roles

SEEDERS = {
    "roles": seed_roles,
    "all": lambda: [f() for f in [seed_roles]],
}


def run_seed(name="all"):
    from budgetron import create_app

    app = create_app()
    with app.app_context():
        if name not in SEEDERS:
            print(f"Seeder '{name}' not found.")
            return
        seeder = SEEDERS[name]
        seeder()
        print(f"Seeder '{name}' executed successfully.")
