# AGENTS.md

## Run Commands

```bash
# Run the app (requires envGymControl active)
python main.py

# Compile to exe
pyinstaller build.spec

# Syntax check
python -m compileall main.py ui.py resource_utils.py pages
```

## Key Constraints

- **Flet version**: 0.86.1 — use the current class helpers (`ft.Alignment`, `ft.Padding`, `ft.Border`, `ft.BorderRadius`)
- **Python**: 3.14.4; recreate `envGymControl` with `py -3.14 -m venv --clear envGymControl`
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
- Dialogs use `page.show_dialog()` / `page.pop_dialog()`; `page.open()`, `page.close()`, and `page.snack_bar` were removed
- `FilePicker.pick_files()` is async and must be awaited
- File paths with non-ASCII chars need UTF-8 handling in PowerShell

## Firebase Setup (common failure point)

1. Enable API: https://console.developers.google.com/apis/api/firestore.googleapis.com/overview?project={id}
2. Create database: https://console.cloud.google.com/datastore/setup?project={id}
3. Both steps required before any Firestore query will work

## Naming Conventions

- Page functions: `*_page(page: ft.Page)` return Flet controls
- Model classes: PascalCase (`Cliente`, `Membresia`, `Asistencia`)
- Database functions: snake_case (`obtener_clientes`, `registrar_asistencia`)
