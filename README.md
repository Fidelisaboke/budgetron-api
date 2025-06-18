# Budgetron
A web-based budget tracker application.

## Installation and Setup
### Pre-requisites
- Python 3.12

### Setup Instructions
- Clone the repository:
```bash
git clone https://github.com/Fidelisaboke/budgetron.git
```

- Navigate to the repository:
```bash
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

- Install the required packages:
```bash
pip install -r requirements.txt
```

- Create the `.env` file by copying the `.env.example` file:
```bash
cp .env.example .env
```

Set the environment variables in the `.env` file.

- Create the `.flaskenv` file by copying the `.flaskenv.example` file:
```bash
cp .flaskenv.example .flaskenv
```
This step is optional, if you need extra configuration, and to avoid having to do 
`--app budgetron` when writing the flask commands.

- Create `migrations/` directory if not present in the project:
```bash
flask db init
```

- Generate migration scripts:
```bash
flask db migrate -m "Initial"
```

- Apply migrations to the database:
```bash
flask db upgrade
```

## Usage
- Run the application specified in the `.flaskenv`:
```bash
flask run
```
