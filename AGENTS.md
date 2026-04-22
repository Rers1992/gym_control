# AGENTS.md

## Run Commands

```bash
# Run the app (requires venv active or flet installed)
python main.py

# Compile to exe
pyinstaller build.spec

# Syntax check
python -m py_compile main.py pages/*.py
```

## Key Constraints

- **Flet version**: 0.25.2 — do not use `ft.SelectableText` (added in 0.26+), use `ft.Text` instead
- **Python**: 3.9.5+ required; older Python versions cause warnings with google-auth libraries
- **Firebase Firestore** must be enabled in Google Cloud Console AND a database created before first run
- Local settings stored in `config_local.db` (SQLite); Firebase credentials stored separately

## Architecture

- `main.py` — entry point, NavigationRail with 5 pages
- `pages/` — one file per page (dashboard, clientes, membresias, asistencia**s**_page, settings_page)
- `database.py` — Firestore operations
- `settings_db.py` — local SQLite for app settings
- `email_service.py` — SMTP notifications
- `models.py` — data classes (Cliente, Membresia, Asistencia)
- `config.py` — plan definitions and env loading

## Flet Quirks

- `ft.Column` and `ft.ListView` accept `scroll=ft.ScrollMode.AUTO`
- Page navigation via `page.run_task()` for async periodic updates (not `on_interval`)
- `NavigationRail` + content_area Row layout for sidebar navigation
- File paths with non-ASCII chars need UTF-8 handling in PowerShell

## Firebase Setup (common failure point)

1. Enable API: https://console.developers.google.com/apis/api/firestore.googleapis.com/overview?project={id}
2. Create database: https://console.cloud.google.com/datastore/setup?project={id}
3. Both steps required before any Firestore query will work

## Naming Conventions

- Page functions: `*_page(page: ft.Page)` return Flet controls
- Model classes: PascalCase (`Cliente`, `Membresia`, `Asistencia`)
- Database functions: snake_case (`obtener_clientes`, `registrar_asistencia`)