"""Module for report generation functionality."""
import os
import logging
import pandas as pd
from flask import current_app, request
from sqlalchemy import extract
from datetime import datetime

from budgetron.utils.logging_utils import log_event
from budgetron.models import Transaction, Category

logger = logging.getLogger(__name__)


def generate_transaction_summary(user_id, month):
    """Aggregate transaction data for a given user and month."""

    # Filter transactions by user and month
    transactions = Transaction.query.join(Category, Transaction.category_id == Category.id).filter(
        Transaction.user_id == user_id).filter(
        extract('month', Transaction.timestamp) == int(month.split('-')[1])).filter(
        extract('year', Transaction.timestamp) == int(month.split('-')[0])
    ).all()

    data = []
    for transaction in transactions:
        row = {
            'Date': transaction.timestamp.strftime('%d-%m-%Y'),
            'Category': transaction.category.name,
            'Type': transaction.category.type,
            'Description': transaction.description,
            'Amount': transaction.amount
        }
        data.append(row)

    return data


def save_csv_report(user_id, data_rows, month):
    """
    Save data rows in a CSV file and return the filepath if
    successful, otherwise return `None`.
    """
    try:
        filename = f"report_{user_id}_{month}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        filepath = os.path.join(current_app.root_path, 'static', 'reports', filename)

        # Save transactions to CSV
        df = pd.DataFrame(data_rows)
        df.to_csv(filepath, index=False)

        log_event(action='csv_report_save_success', details={'file_path': filepath})

        return f"{request.host_url}static/reports/{filename}"

    except Exception as e:
        log_event('csv_report_save_failed', status='failure', details={'error': str(e)})
        return None
