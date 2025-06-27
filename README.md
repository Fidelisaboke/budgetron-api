# Budgetron
## Project Overview
Budgetron is a web-based personal finance management application that allows users to categorize transactions, create monthly 
budgets, and generate downloadable reports.

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation and Setup](#installation-and-setup)
  - [Pre-requisites](#pre-requisites)
  - [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)

## Features
- JWT Authentication (Register, Login, Profile)
- Category Management (Income/Expense)
- Transaction Tracking
- Budget Creation and Monitoring
- Monthly Financial Report Generation (.csv)
- Pagination, Filtering, and Admin Access

## Tech Stack
- **Backend:** Python (Flask + Flask-RESTful)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy + Flask-Migrate
- **Auth:** JWT (via `flask-jwt-extended`)
- **Serialization**: Marshmallow
- **Docs:** Postman Collection

## Installation and Setup
### Pre-requisites
- Python 3.12 or above

### Setup Instructions
- Clone the repository:
```bash
git clone https://github.com/Fidelisaboke/budgetron.git
cd budgetron
```

- Create a virtual environment:
```bash
python3 -m venv .venv
```

- Activate the virtual environment:
    - On Windows:
    ```bash
    .venv\Scripts\activate
    ```
    - on macOS or Linux:
    ```bash
    source .venv/bin/activate
    ```

- Install dependencies:
```bash
pip install -r requirements.txt
```

- Copy environment example files:
```bash
cp .env.example .env
cp .flaskenv.example .flaskenv  # Optional but useful for Flask CLI
```

- Create `migrations/` directory if not present in the project:
```bash
flask db init
```

- Create and apply migrations:
```bash
flask db migrate -m "Initial"
flask db upgrade
```

- Seed the database with initial data:
```bash
flaask seed
```

- Create an admin user account:
```bash
flask create-admin
```

## Usage
- Run the application:
```bash
flask run
```
Runs the server at `http://127.0.0.1:5000`

## Project Structure
```bash
.
├── app.py                  # Entry point for the Flask application
├── budgetron/              # Main application package
│   ├── __init__.py         # App factory
│   ├── config.py           # Configuration settings
│   ├── models.py           # SQLAlchemy models
│   ├── resources/          # API route handlers (Flask-RESTful)
│   ├── schemas/            # Marshmallow schemas for validation/serialization
│   ├── services/           # Business logic (e.g., report generation)
│   ├── utils/              # Utility functions (logging, JWT, pagination, etc.)
│   ├── templates/          # Jinja templates (if any)
│   ├── commands/           # Custom Flask CLI commands
│   └── seeder/             # Data seeders for roles and initial data
├── migrations/             # Alembic migrations for DB schema management
├── requirements.txt        # List of Python dependencies
├── .env.example            # Environment variable sample file
├── .flaskenv.example       # Flask-specific environment config
├── .gitignore              # Files and directories to exclude from Git
├── README.md               # Project documentation

```

## API Documentation
Explore all available endpoints using the official Postman Collection:
- [Postman Collection](https://documenter.getpostman.com/view/31418538/2sB2xFenjK)