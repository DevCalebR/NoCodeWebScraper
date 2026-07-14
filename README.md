# ScraperPro Prototype

## Project status

This repository is an early, private prototype for configurable web scraping. It is not a production SaaS, enterprise platform, hosted service, or supported commercial product.

The code is retained privately for reference while its security, persistence, billing, and operational design are evaluated. Do not deploy it to untrusted users without a separate production hardening effort.

## Current capabilities

- Create CSS-selector-based scraping configurations.
- Fetch and parse web pages with Requests and Beautiful Soup.
- Store prototype client/configuration data on the local filesystem.
- Export collected data in several file formats.
- Run a Streamlit user interface and a Flask API prototype.
- Run a separate Streamlit administrator view.
- Exercise an incomplete Stripe subscription integration when explicitly configured.

The tier, trial, email, scheduling, visual-recorder, and payment code is prototype-quality. It has not been validated as a complete billing or multi-tenant production system.

## Setup

Use Python 3.10 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Load environment variables using your preferred local process manager or shell. Never commit `.env`.

Start the primary interface:

```bash
streamlit run app.py
```

Start the API prototype separately:

```bash
python api_server.py
```

Start the admin interface only after setting a strong administrator password:

```bash
export SCRAPERPRO_ADMIN_PASSWORD="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
streamlit run admin_panel.py
```

## Environment variables

See `.env.example` for the complete list.

- `SCRAPERPRO_ADMIN_PASSWORD` is required for admin access. The admin panel fails closed when it is absent.
- Stripe variables are optional and required only for the incomplete billing prototype.
- Email-provider variables are optional and required only for the corresponding delivery integration.
- `PORT` controls the Flask API port.

## Validation

Run a syntax check over the tracked Python modules:

```bash
python -m py_compile *.py
```

There is currently no automated test suite. External integrations require isolated test accounts before use.

## Known limitations

- Local JSON/file persistence is not safe multi-tenant storage.
- Authentication and authorization have not received a production security review.
- Billing, email, scheduling, proxy, and visual-recorder paths are incomplete or unverified.
- Scraping behavior must be reviewed against each site’s terms, robots guidance, rate limits, and applicable law.
- There is no CI, hosted demo, monitoring, queue, durable database migration strategy, or deployment support.
- Marketing, pricing, revenue, customer, and performance claims are intentionally not made.

## Recommendation

Retain this repository privately or archive it. A future public release should be a smaller, tested scraping utility rather than a SaaS claim.
