# Fake Bank 
Fake Bank is my personal project to present and practice my programming skills.

 ![Transaction history](docs/images/history.png)![Transfer](docs/images/transfer.png)

## Features
- Client registration and authentication
- Open bank accounts and create linked cards
- Make transfers
- Take loans
- View transaction history

## Tech Stack
- Python 3.12
- Django
- pytest and Django testing tools
- Django Debug Toolbar
- PostgreSQL 18
- Docker and Docker Compose
- Git
- Ubuntu (development environment)

## Localisation
is achieved with Django Locale Middleware. Flags are the switcher.
Available languages: English, Polish

 ![alt localisation](docs/images/flag-localisation.png)

## Architecture
- `bank` is the initial django directory, contains project settings and main URL configuration.
- `banking` responsible for managing clients, accounts, and cards.
- `transfers` additional app responsible for transfers between accounts, and history of those transfers

## Getting Started

This setup is intended for local development.

### Requirements

- Git
- Docker Engine and the Docker Compose plugin
- Python 3.12, if running Django locally

The commands below assume access to Docker without `sudo`. If your installation requires administrator privileges, prefix Docker commands with `sudo`.

### Download the project

```bash
git clone https://github.com/Furiolis/bank.git
cd bank
```

### Environment variables

Create a `.env` file in the project root:

```dotenv
SECRET_KEY=replace-with-a-random-secret-key
POSTGRES_DB=fakebank
POSTGRES_USER=fakebank
POSTGRES_PASSWORD=replace-with-a-strong-password
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
```

Replace the secret key and password placeholders with your own random values before starting the application. Keep `.env` out of version control.

`POSTGRES_HOST=127.0.0.1` is used when Django runs locally. Docker Compose overrides it with `db` for the Django container.

PostgreSQL uses the database name, username and password to initialize an empty data volume. Changing these variables later does not update credentials in an existing database.

### Run Django and PostgreSQL with Docker Compose

Create the external volume required by the Compose configuration:

```bash
docker volume create fakebank_postgres_data
```

Build the application image and start PostgreSQL:

```bash
docker compose build web
docker compose up -d db
```

Apply database migrations:

```bash
docker compose run --rm web python manage.py migrate
```

Start Django:

```bash
docker compose up -d web
```

Open http://127.0.0.1:8001 and register a user.

To view application logs:

```bash
docker compose logs -f web
```

To stop the services:

```bash
docker compose stop
```

To start them again:

```bash
docker compose up -d
```

Database data is stored in the `fakebank_postgres_data` volume and persists when containers are stopped or recreated.

The project directory is mounted into the Django container, so local code changes are available inside it. After changing Python dependencies, rebuild and recreate the application container:

```bash
docker compose up -d --build web
```

### Run Django locally with PostgreSQL in Docker

Complete the download and environment configuration steps above, then create the volume and start PostgreSQL:

```bash
docker volume create fakebank_postgres_data
docker compose up -d db
```

Create and activate a Python virtual environment:

```bash
python3 -m venv vvv
source vvv/bin/activate
```

Install dependencies, apply migrations and start Django:

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000.

Both local Django and the Django container connect to the same PostgreSQL database when using this configuration.

## Testing

Tests cover models, validators, forms and views, including successful and rejected transfers.

With the Docker Compose services running:

```bash
docker compose exec web python -m pytest
```

Alternatively, with the local virtual environment activated and PostgreSQL running:

```bash
python -m pytest
```

Django's test runner is also supported:

```bash
python manage.py test
```

Database tests use a separate test database.

![Tests](docs/images/tests.png)

# Things to do
- TODO Django Rest Framework
- TODO Two-factor authentication (2FA)

- TODO Move redundant code from views to models as property
- TODO Add scheduled and delayed transfers()
- TODO Password restore or edit
- TODO Card pin to restore or edit
