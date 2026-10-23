# Django and Next.js Automation Platform

A full-stack project organized around a Django REST Framework backend and a frontend stored as a Git submodule.

The backend includes account, automation, integration, and webhook areas. Its requirements also include Stripe, OpenAI, PostgreSQL, and JWT packages. The frontend directory is a submodule, so initialize it separately when you need its source.

## Backend setup

Use Python 3 and install the dependencies from the backend directory:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a local environment file from the project's documented configuration before running the backend. Never commit credentials. Start the Django development server with:

```bash
python manage.py runserver
```

## Frontend source

After cloning, initialize the frontend submodule with `git submodule update --init --recursive`. Follow that submodule's own setup instructions.
