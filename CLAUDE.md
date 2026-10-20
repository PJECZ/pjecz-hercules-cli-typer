# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Command-line interface (Typer + SQLAlchemy 2.0) for maintaining the PostgreSQL database of "Plataforma Web" (Hércules, Poder Judicial del Estado de Coahuila de Zaragoza). Each command group works on the database table with the same name; each subcommand is a verb describing the action (`consultar`, `exportar`, ...). Code, docstrings, comments and CLI names are written in Spanish — keep it that way.

## Commands

Requires Python >= 3.14 and `uv`. Dependencies are managed with `uv` (`uv.lock`).

```bash
uv sync                                                  # install dependencies into .venv
uv run src/pjecz_hercules_cli_typer/main.py --help       # run the CLI
uv run src/pjecz_hercules_cli_typer/main.py roles consultar --nombre ADMIN --limit 10
```

`source .bashrc` (the repo-local one) is the author's workflow: it requires the `mnemosine-developer` toolbox, exports `.env` into the environment, sets `GOOGLE_APPLICATION_CREDENTIALS` and `PG*` vars, activates `.venv`, and defines the alias `cli` for the command above.

Formatting/linting config lives in `pyproject.toml`: black and isort (profile black) with line length 128, ruff (line length 128), basedpyright in basic mode. There is no test suite.

Note: the `[project.scripts]` entry point (`pjecz_hercules_cli_typer:main`) points to a placeholder in `__init__.py`; the real Typer app is `app` in `main.py`.

## Configuration

`config/setttings.py` (note the triple "t" in the filename) defines a pydantic-settings `Settings` loaded from `.env` (see `.env.example`), accessed via the cached `get_settings()`. `SQLALCHEMY_DATABASE_URI` takes precedence; otherwise it is built from `DB_*`. `.env.example` also lists Google Cloud Storage bucket names (`CLOUD_STORAGE_DEPOSITO_*`) and `SALT` (HashID) for upcoming features.

## Architecture

```
src/pjecz_hercules_cli_typer/
  main.py           # root Typer app; registers each command module with app.add_typer(..., name="tabla-con-guiones")
  commands/<tabla>.py  # one Typer sub-app per table: `app = Typer(help="...")` + @app.command() verbs
  models/<tabla>.py    # one SQLAlchemy declarative model per table
  core/database.py     # Base, engine/sessionmaker (lru_cached), session_scope()
  core/safe_string.py  # input sanitizers: safe_string, safe_email, safe_clave
exports/            # output directory for exported files
logs/               # output directory for execution logs
```

### Models (`models/`)

- All models inherit `core.database.Base`, which already provides the audit columns `creado`, `modificado` and `estatus` (CHAR, `"A"` = active). Do not redeclare them.
- Style: SQLAlchemy 2.0 `Mapped[...]` / `mapped_column`, sections commented `# Nombre de la tabla`, `# Clave primaria`, `# Claves foráneas`, `# Columnas`, `# Hijos`, plus a `__repr__`.
- Relationships use string class names (`relationship("Permiso", back_populates="rol")`). These resolve only if every referenced model module has been imported before the mappers configure, so when adding a model, make sure the related models are imported somewhere on the command path. Relationships to tables not yet modeled are left commented out.
- Models mirror an existing database; this project does not create or migrate the schema.

### Commands (`commands/`)

Commands follow a consistent pattern (see `commands/roles.py`, and `commands/usuarios_roles.py` for joins):

1. Options are function params with defaults, always including `offset: int = 0` and `limit: int = 25`, plus optional filters (`str | None = None`).
2. Build a `rich.table.Table` for output.
3. Build a `where_clauses` list starting with `Model.estatus == "A"` (and the same for each joined table); sanitize each filter with `safe_string` / `safe_email(..., search_fragment=True)` / `safe_clave` and append `like("%...%")` only if the sanitized value is non-empty.
4. Build a `select(...)` of specific columns (use `.label()` and `.select_from(...).join(...)` for joins), `.order_by`, `.offset`, `.limit`.
5. Execute inside `with session_scope() as session:` (auto commit/rollback) and add rows to the table.

When adding a new table: create the model, create `commands/<tabla>.py`, and register it in `main.py`. Some command modules (`edictos`, `glosas`, `listas_de_acuerdos`, `sentencias`, `materias_tipos_de_juicios`) are currently empty stubs and not registered.

## Skills

Project skills `spec` and `spec-impl` (in `.agents/skills/`, linked from `.claude/skills/`) implement a spec-driven workflow: `/spec` designs a spec saved under `specs/`, `/spec-impl <NN-name>` implements an approved spec on its own branch.
