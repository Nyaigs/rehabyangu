# Secrets Management with Doppler

**Status:** Current
**Last Updated:** 2026-09-23

RehabYangu uses Doppler for production secrets. Local development uses a `.env` file.

## Why Doppler

- Secrets never stored in code or Git.
- Single source of truth across environments.
- Rotate without code change.
- Access control per team member.
- Audit log of secret access.

## Setup (Local)

Doppler is optional locally. If you don't use it, `backend/.env` is enough.

Install the CLI:

    curl -Ls https://cli.doppler.com/install.sh | sh

Authenticate and link the repo:

    doppler login
    cd ~/rehabyangu
    doppler setup

Select project `rehabyangu`, then config `dev`.

Run any command with secrets injected:

    doppler run -- python backend/manage.py runserver

## Setup (Production)

The backend container runs:

    doppler run -- python manage.py runserver 0.0.0.0:8000

`DOPPLER_TOKEN` is injected by the host.

## Secrets in Doppler

| Secret | Purpose |
|---|---|
| SECRET_KEY | Django signing key |
| DB_PASSWORD | PostgreSQL password |
| MFA_ENCRYPTION_KEY | Fernet key for TOTP secrets |
| FIELD_ENCRYPTION_KEY | Fernet key for tenant M-Pesa credentials |
| DEFAULT_FROM_EMAIL | Outbound email sender |
| EMAIL_HOST | SMTP host |
| EMAIL_HOST_USER | SMTP username |
| EMAIL_HOST_PASSWORD | SMTP password |
| MPESA_CONSUMER_KEY | Platform M-Pesa (later) |
| MPESA_CONSUMER_SECRET | Platform M-Pesa (later) |
| MPESA_PASSKEY | Platform M-Pesa (later) |
| SENTRY_DSN | Error tracking (later) |

## Not in Doppler

Non-sensitive defaults like DEBUG, ALLOWED_HOSTS, LANGUAGE_CODE.

## Adding a Team Member

    doppler workplace members add benjie@weiralynk.com --role collaborator --project rehabyangu

## Rotating a Secret

    doppler secrets set DB_PASSWORD=new-value --config prd

## CI Access

GitHub Actions uses a repository secret named `DOPPLER_TOKEN`.

    - name: Run backend tests
      env:
        DOPPLER_TOKEN: ${{ secrets.DOPPLER_TOKEN }}
      run: doppler run -- python manage.py test

## Adding a New Secret

1. `doppler secrets set NEW_SECRET=value --config dev`
2. `doppler secrets set NEW_SECRET=value --config prd`
3. Add the name to `backend/.env.example`
4. Add a startup check in `settings.py` if required
