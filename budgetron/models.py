from budgetron.utils.security import bcrypt
from budgetron.utils.db import db

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

    def __repr__(self):
        return '<Role %r>' % self.name

user_roles = db.Table(
    'user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    roles = db.relationship('Role', secondary=user_roles, backref='users', lazy='dynamic')
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')
    reports = db.relationship('Report', backref='user', lazy='dynamic')

    @property
    def is_admin(self):
        """Checks whether the user is an admin."""
        return any(role.name == 'admin' for role in self.roles)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    type = db.Column(db.String(10), nullable=False)
    last_updated = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    transactions = db.relationship('Transaction', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.id}>'


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    def __repr__(self):
        return f'<Transaction {self.id}>'


class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    format = db.Column(db.String(10), nullable=False)
    file_url = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
