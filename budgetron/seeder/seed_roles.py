from budgetron.models import Role
from budgetron.utils.db import db

def seed_roles():
    roles = ['admin', 'user']
    for role_name in roles:
        if not Role.query.filter_by(name=role_name).first():
            role = Role(name=role_name)
            db.session.add(role)
            print(f"Seeded role: {role_name}")
    db.session.commit()