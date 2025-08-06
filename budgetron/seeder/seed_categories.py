from budgetron.models import Category
from budgetron.utils.db import db

def seed_categories():
    DEFAULT_CATEGORIES = [
        # Expense Categories
        {"name": "Food", "type": "expense"},
        {"name": "Rent", "type": "expense"},
        {"name": "Utilities", "type": "expense"},
        {"name": "Transport", "type": "expense"},
        {"name": "Health", "type": "expense"},
        {"name": "Entertainment", "type": "expense"},
        {"name": "Groceries", "type": "expense"},
        {"name": "Insurance", "type": "expense"},
        {"name": "Education", "type": "expense"},
        {"name": "Debt Payment", "type": "expense"},
        {"name": "Miscellaneous", "type": "expense"},

        # Income Categories
        {"name": "Salary", "type": "income"},
        {"name": "Business", "type": "income"},
        {"name": "Freelance", "type": "income"},
        {"name": "Investments", "type": "income"},
        {"name": "Interest", "type": "income"},
        {"name": "Dividends", "type": "income"},
        {"name": "Gift", "type": "income"},
        {"name": "Rental Income", "type": "income"},
        {"name": "Refunds", "type": "income"},
        {"name": "Other Income", "type": "income"},
    ]

    for cat in DEFAULT_CATEGORIES:
        category_name = cat['name']
        category_type = cat['type']

        existing = Category.query.filter_by(name=category_name, type=category_type).first()
        if not existing:
            category = Category(name=cat['name'], type=category_type, is_default=True, user_id=None)
            db.session.add(category)
            print(f"Seeded category: {category_name} ({category_type})")

    db.session.commit()