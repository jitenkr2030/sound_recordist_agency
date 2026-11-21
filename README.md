# Sound Recordist Agency Management System

A Django-based agency operations starter application with public website, role-aware portals, client and professional records, project production workflows, bookings, equipment, studios, recording sessions, audio asset delivery, quotations, contracts, GST-enabled invoices, payments, expenses, reports, insights, audit logs and backup utility.

## Important scope note

This is a functional, extensible **MVP/starter implementation**, not a certified accounting package or a fully integrated production audio recorder. It provides database-backed CRUD workflows and role-aware views for the included modules. GST calculations are basic percentage calculations; have a qualified accountant validate invoice compliance, place-of-supply rules, CGST/SGST/IGST treatment, e-invoicing and statutory reporting before commercial use. The "AI insights" page currently provides transparent rule-based indicators, not an external AI model. WhatsApp/SMS/email gateways, payment gateway, e-signatures, cloud storage and real-time collaborative features require credentials and integration work.

## Requirements

- Python 3.10+
- pip
- Windows, WSL or Linux

## Run on Windows PowerShell

```powershell
cd sound_recordist_agency
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Run on WSL / Linux

```bash
cd sound_recordist_agency
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

## Demo accounts

| Portal / role | Username | Password |
|---|---|---|
| Admin | `admin` | `Admin@12345` |
| Manager | `manager` | `Demo@12345` |
| Sound recordist | `recordist` | `Demo@12345` |
| Client | `client` | `Demo@12345` |
| Freelancer | `freelancer` | `Demo@12345` |
| Equipment manager | `equipment` | `Demo@12345` |
| Accountant | `accountant` | `Demo@12345` |

Change all demo passwords immediately. The Django admin is at `/admin/`.

## Main URLs

- `/` public agency website
- `/contact/` public enquiry form
- `/login/` login
- `/dashboard/` dashboard
- `/portal/admin/`, `/portal/recordist/`, `/portal/client/`, `/portal/freelancer/`, `/portal/equipment/`
- `/modules/clients/`, `/modules/projects/`, `/modules/bookings/`, `/modules/equipment/`, etc.
- `/audio/` audio delivery library
- `/reports/` reports and CSV exports
- `/insights/` management insights
- `/backup/` administrator backup

## Included business modules

Branches, user profiles, clients, sound professionals, freelancers, services, projects, bookings, equipment, equipment allocations, studios, studio sessions, recording sessions, audio assets, quotations, contracts, invoices, payments, expenses, leads, tasks, documents, reviews, notifications and audit logs.

## PostgreSQL configuration

Set `DATABASE_URL` in `.env`, for example:

```text
DATABASE_URL=postgresql://dbuser:dbpassword@localhost:5432/sound_agency
```

Then install requirements and run migrations. For a production PostgreSQL backup use:

```bash
pg_dump -Fc -d sound_agency > sound_agency.dump
pg_restore -d sound_agency sound_agency.dump
```

## Production deployment checklist

1. Set `DEBUG=0` and a long random `SECRET_KEY`.
2. Set `ALLOWED_HOSTS` and configure HTTPS.
3. Use PostgreSQL and scheduled database backups.
4. Configure persistent media storage and private download permissions.
5. Configure email/SMS/WhatsApp providers if required.
6. Review role permissions and object-level data access.
7. Add malware scanning and upload size/type restrictions for client audio uploads.
8. Configure logging, monitoring, static collection and secure secrets.
9. Test restore procedures and business workflows using staging data.
10. Obtain accountant/legal review of GST, contracts, privacy and retention policies.

## Development commands

```bash
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
```

## Backup

Admin can download SQLite database and media files from `/backup/`. The archive contains database and media content. For PostgreSQL, use `pg_dump` as shown above. Restoring a live system is intentionally a manual, controlled operation.

## Customisation

Brand name, contact details, GSTIN and agency settings can be expanded through `AgencySetting` and `Branch`. Extend forms, object-level permissions, invoice line items, tax rules, PDF templates and notifications before using the platform for production operations.
