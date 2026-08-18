# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Telegram bot ("Сники Бот" / Sneaky Bot) for finding and organizing tabletop RPG (D&D) games in the Russian-speaking community. Deployed at dnd-hub.ru. All user-facing strings are in Russian.

Stack: Python 3.12 · [pyTelegramBotAPI](https://pytba.readthedocs.io/) (`telebot`, async) · FastAPI (webhook receiver) · SQLAlchemy 2.0 async + asyncpg (PostgreSQL) · Alembic · Redis (FSM state in prod) · uv (dependency management) · Kamal (deploy).

## Commands

```bash
uv sync                                  # install all deps (main + dev) into ./.venv
uv sync --no-dev                         # production deps only
uv add <pkg>                             # add a dependency (updates pyproject.toml + uv.lock)
uv sync --upgrade-package <pkg>          # update one dep + its transitives, rewrite the lock, reinstall
uv lock                                  # re-resolve the lock from pyproject.toml

uv run ruff check --fix .                # lint, applying the safe autofixes
uv run ruff format .                     # format

uv run python main.py                    # run locally via long-polling (needs .env)
uv run uvicorn main:app --host 0.0.0.0 --port 8080   # run as webhook server (production mode)

uv run python create_webhook.py          # register the Telegram webhook (uses WEBHOOK_URL_BASE)
uv run python remove_webhook.py          # delete the webhook (required before switching back to polling)

uv run alembic upgrade heads             # apply migrations (note: heads, plural)
uv run alembic revision --autogenerate -m "msg"  # generate a migration from model changes
uv run alembic downgrade -1              # roll back one migration

docker compose up --build                # run app container locally (reads .env)
kamal deploy                             # deploy to production (see README.md for full Kamal usage)
```

There are **no automated tests** in this repo, but code style *is* enforced: **Ruff** does both the formatting and the linting, gated by the blocking `lint` job in `.github/workflows/ci.yml`. Run `uv run ruff check --fix . && uv run ruff format .` before pushing — CI is the only gate, there is no pre-commit hook, by design.

Ruff's config is `[tool.ruff]` in `pyproject.toml`. The rule set is pinned with `select` (never `extend-select`, which would inherit Ruff's shifting ~415-rule default), and every non-obvious choice there carries a comment explaining why — read those before changing it. When the pinned Ruff version is bumped, re-run the formatter and check `ruff check --isolated --statistics` to see what the new defaults would add. The one-off bulk reformat is listed in `.git-blame-ignore-revs`; run `git config blame.ignoreRevsFile .git-blame-ignore-revs` once per clone so local `git blame` skips it.

Dependencies are managed with **uv** (PEP 621 `[project]` table). `pyproject.toml` is the declaration and `uv.lock` pins the full resolved tree — both are committed; there is **no `requirements.txt`**. `[tool.uv] package = false` (this is an app, not a distributable package, so uv installs the dependencies but never the project root itself). Dev-only tools go in the `dev` dependency group (`[dependency-groups] dev = [...]`) and are excluded by `--no-dev`. **NOTE:** the migration to uv (previously Poetry, before that a bare `requirements.txt`) was version-preserving, so `pyproject.toml` pins direct deps to exact versions **and** temporarily pins ~20 transitive deps at their earlier versions (the commented block) so no dependency changed. Loosen those to ranges and drop the transitive pins in a follow-up PR once test coverage exists — then `uv lock --upgrade` can move them.

Local dev needs a `.env` (copy `.env_example`). `consts.py` reads every setting from env via `python-dotenv` and will raise at import time if required ints (`NEWS_CHANNEL_ID`, `DB_POOL_SIZE`, `ADMIN_IDS`, etc.) are missing.

## Two run modes, one `main.py`

`main.py` builds both an `AsyncTeleBot` (`bot`) and a FastAPI `app`:
- **Production** runs `uvicorn main:app`; Telegram POSTs updates to `/webhook/` which feeds `bot.process_new_updates(...)`. `/up` is the healthcheck. The webhook is set once via `create_webhook.py`.
- **Local dev** runs `python main.py`, which falls into `__main__` and uses `bot.infinity_polling(...)` instead.

The `Dockerfile` is a multi-stage uv build: a build stage runs `uv sync --no-dev --frozen` to install the locked production deps into an in-project `.venv`, and the slim runtime stage copies just that venv. On start it runs `alembic upgrade heads` before starting uvicorn with 4 workers.

## Architecture

Requests flow: **Telegram update → middlewares → handler group → controller → model**.

### Middlewares (`middlewares/`, registered in `main.py` — order matters)

Telebot middlewares inject keyword args into every handler. Handlers receive `session`, `user`, `state` (and `bot` when registered with `pass_bot=True`).

- `SessionMiddleware` — opens a fresh `AsyncSession` per update into `data["session"]`. On success it **commits** (and bumps `user.commands_count` / `user.last_update`), then closes. Handlers/controllers should `session.flush()` and rely on this middleware to commit — don't commit yourself.
- `UserMiddleware` — `get_or_create`s the `User` by Telegram id into `data["user"]`; returns `SkipHandler()` for banned users.
- `ExceptionMiddleware` — forwards any unhandled exception (chunked) to the Telegram chat `EXCEPTION_CHAT_ID`.
- `StateMiddleware` — telebot's built-in FSM. State storage is Redis when `STATE_STORAGE=redis` (prod), else in-memory (dev).

### Handler groups (`handlers/`)

Each feature is a `*HandlerGroup` instantiated and `.register_handlers()`-ed in `main.py`. Two base shapes (`utils/handler_groups/`):

- **`BaseHandlerGroup`** — a `handlers: list[Type[BaseHandler]]` of individual handler classes. Used for menu/callback-driven features (review, administration, group_administration, feedback, game_application).
- **`RegistrationHandlerGroup`** — a **multi-step conversational form engine**. Defines `form_item_groups: tuple[FormItemGroup]`, a `command`, and a `form_prefix`. Flow is `first_step → each form item → last_step`. Used by `user_registration`, `user_profile`, `game_registration`, `game_edit`, and `filters`. Note `game_edit`/`filters` override `register_handlers` so every form item routes back through `last_step` (jump-to-any-field editing) rather than running strictly in sequence.

Individual handlers (`utils/handlers/`) subclass `BaseHandler` via `BaseMessageHandler` or `BaseCallbackHandler`. Each implements `register_handler()` (wires the telebot handler) plus `handle_message` / `on_action`. Callback handlers call `check_callback_not_processed()` first — it strips the inline keyboard so a button can't be processed twice; if that edit fails (already stripped), the action is skipped.

### Form items (`utils/form/`)

Reusable building blocks for the form engine, shared across registration/edit/filter flows:
- `FormTextItem` — free-text answer. Has a `state` (FSM `State`), `prepare_text`, built-in `validate_answer` (length cap, no links, no `prohibited_symbols` `* # _ \``), `save_answer`, and `on_answered` → calls `next_step`.
- `FormChoiceTextItem` / `FormChoiceItem` — inline-keyboard choice. `FormPhotoItem` — image upload.

Callback data is namespaced as **`{form_prefix}:{form_item_name}:{data}`**; `RegistrationHandlerGroup.create_func_for_filter` matches on this prefix to route callbacks to the right form item.

**To add a step to a form**: write a new form item class (set its `state` in the group's `states.py`) and add it to the group's `form_item_groups` tuple — `main` is the primary prompt, `side` items are conditional follow-ups (e.g. ask city only if format is offline).

### Controllers (`controllers/`)

Data-access layer. `CRUD` (`controllers/crud.py`) is the abstract base: `get_one`, `get_or_create`, `create`, `get_list`, `common_query`. Each controller sets `model` and may override `common_query()` to eager-load relationships (e.g. `UserController` adds `joinedload(User.city)`). Put non-trivial queries here, not in handlers. Note `UserController.get_user_ids_by_custom_filter` runs raw `text()` SQL — admin-only.

### Models (`models/`)

SQLAlchemy 2.0 declarative. `Base` lives in `models/base.py`; **every model must be imported in `models/__init__.py`** (it ends with `Base.registry.configure()`, and Alembic + relationship resolution depend on all models being loaded). Uses `Mapped[...]` / `mapped_column`. Enums are stored as `SMALLINT` `IntEnum`s (e.g. `GameFormat`, `GameType`) with parallel `*Text` `Enum`s holding the Russian display labels.

### FSM states

Defined per handler group in `states.py` files using telebot `StatesGroup` / `State`. The active state determines which message/callback handler fires.

## Migrations

Alembic with `target_metadata = Base.metadata`. `alembic/env.py` reads `DB_URL` from `consts.py` and strips `+asyncpg` (migrations run on a sync driver). Migration filenames are date-prefixed (`file_template` in `alembic.ini`). The app applies `alembic upgrade heads` automatically on container start.

## Deploy

Kamal (`config/deploy.yml`). Image `danuzh1k/dnd_hub`, host `dnd-hub.ru`, app port 8080, Postgres 17 + Redis 7.4 as accessories. Non-`clear` env vars come from `.kamal/secrets`. See `README.md` for the full command list (`kamal setup`, `kamal deploy`, `kamal remove`, plus `dotenv -f .env.production` variants).

Prod runs on the host behind the `dnd_hub` SSH alias; `deploy.yml` references hosts by alias, so every `kamal`/`ssh` command targets whatever `~/.ssh/config` maps `dnd_hub` to — repointing the alias moves the target without editing `deploy.yml`. Secrets come from **`.env.production` + `dotenv`** (not 1Password): every kamal command must be wrapped `dotenv -f .env.production kamal …`, and `.kamal/secrets` resolves each value as a plain `$VAR` passthrough. `.env.production` is gitignored.

`docs/` is gitignored — anything under it is temporary, local-only working notes that may be removed at any time. Don't reference `docs/` files from code/config or rely on them being present, and don't `git add` them.

A sibling Rails bot — https://github.com/sas145alex/dnd_spells_2024_bot — shares this Kamal + Backblaze-B2 backup playbook.

### Backups (Backblaze B2)

Off-host DB backups run as the **`backup` Kamal accessory** (`accessories.backup` in `deploy.yml`) — `tiredofit/db-backup:4.1.100` (bundles PG17 **and** PG18 clients). It joins the `kamal` network (no `network:` key) and reaches the DB by container name `dnd_hub-db`, runs a nightly (03:00 GMT) `pg_dump` of `dnd_hub_production` (user `postgres`) → gzip → **Backblaze B2** bucket `dnd-hub` (S3-compatible, `eu-central-003`), **7-day** retention. A post-backup hook (`.kamal/backup/notify.sh`, mounted to `/assets/scripts/post/`) POSTs a **Discord** embed on every run — it reports **FAILED if either the dump (`$1`) or the S3 upload (`$11`) errored** (the image passes them separately; checking only `$1` posts a false OK) — and pings **healthchecks.io** as a dead-man's-switch.

- Secrets in `.env.production`: `B2_KEY_ID`, `B2_APP_KEY`, `BACKUP_DISCORD_WEBHOOK`, `BACKUP_HEALTHCHECK_URL`; `DB01_PASS` reuses `POSTGRES_PASSWORD`.
- Boot/replace on a host: `dotenv -f .env.production kamal accessory boot backup` (travels with the config — re-run per host migration). On-demand run: `dotenv -f .env.production kamal backup-now`. Logs: `dotenv -f .env.production kamal backup-logs`.
- Restore (break-glass / verify): `bin/db-restore-local <dump.sql.gz> [db]` into local Postgres (**prefer this for test restores** — keeps prod untouched; local PG must be ≥ the dump's major) or `bin/db-restore-remote <dump.sql.gz> [db] [ssh_host]` over SSH into the prod container. No local `aws` CLI — pull a dump by streaming it from the backup container: `ssh dnd_hub "docker exec dnd_hub-backup sh -c 'AWS_ACCESS_KEY_ID=\$DB01_S3_KEY_ID AWS_SECRET_ACCESS_KEY=\$DB01_S3_KEY_SECRET aws --region \$DB01_S3_REGION --endpoint-url https://\$DB01_S3_HOST s3 cp s3://\$DB01_S3_BUCKET/\$DB01_S3_PATH/<file> -'" > <file>`.
- One-time external setup (in-browser): a **private B2 bucket** + a bucket-scoped **Read/Write application key**, a **Discord webhook**, and a **healthchecks.io check** — their values go in `.env.production`.
- A **Postgres major upgrade** (17→18) is **not** an image bump — `postgres:18` won't boot on a PG17 data dir; it needs a `pg_dump`/restore (the backup accessory / `bin/db-restore-*` are the tooling). The `nfrastack/db-backup` successor (post-EOL) is not publicly pullable yet, so we stay on `tiredofit`.

## Git

Commit messages: **English, short** — a single imperative sentence (~50 chars, no body). **No AI/agent trailers** — do not append `Co-Authored-By` or "Generated with …" lines.
