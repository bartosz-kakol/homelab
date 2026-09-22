import json
import os
import re
import sys
import time

import psycopg
from psycopg import sql

CONFIG_PATH = os.environ.get("CONFIG_PATH", "/config/databases.json")
CONNECT_TIMEOUT = int(os.environ.get("CONNECT_TIMEOUT", "60"))
MARKER = "managed by db-provisioner"
NAME_RE = re.compile(r"[a-z_][a-z0-9_]{0,62}")


def log(msg):
    print(f"[provisioner] {msg}", flush=True)


def die(msg):
    log(f"ERROR: {msg}")
    sys.exit(1)


def load_config():
    try:
        with open(CONFIG_PATH) as f:
            raw = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        die(f"cannot read {CONFIG_PATH}: {e}")
    if not isinstance(raw, dict):
        die("config must be a JSON object of {name: ENV_VAR_NAME}")

    apps = {}
    for name, var in raw.items():
        if not NAME_RE.fullmatch(name):
            die(f"invalid app name {name!r}: use lowercase letters, digits, underscores")
        if not isinstance(var, str):
            die(f"value for {name!r} must be an environment variable name")
        password = os.environ.get(var)
        if not password:
            die(f"environment variable {var} (password for {name!r}) is unset or empty")
        apps[name] = password
    return apps


def connect():
    # Connection settings come from PGHOST / PGUSER / PGPASSWORD.
    deadline = time.monotonic() + CONNECT_TIMEOUT
    while True:
        try:
            return psycopg.connect(dbname="postgres", autocommit=True, connect_timeout=3)
        except psycopg.OperationalError as e:
            if time.monotonic() >= deadline:
                die(f"postgres not reachable after {CONNECT_TIMEOUT}s: {str(e).strip()}")
            log("waiting for postgres...")
            time.sleep(1)


def role_state(cur, name):
    cur.execute(
        "SELECT shobj_description(oid, 'pg_authid') FROM pg_roles WHERE rolname = %s",
        (name,),
    )
    row = cur.fetchone()
    if row is None:
        return "missing"
    return "managed" if row[0] == MARKER else "foreign"


def db_exists(cur, name):
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (name,))
    return cur.fetchone() is not None


def ensure_app(cur, name, password):
    ident = sql.Identifier(name)
    state = role_state(cur, name)

    if state == "foreign":
        die(f"role {name!r} exists but is not managed by the provisioner")
    if state == "missing":
        if db_exists(cur, name):
            die(f"database {name!r} exists but is not managed by the provisioner")
        cur.execute(sql.SQL("CREATE ROLE {} LOGIN").format(ident))
        cur.execute(sql.SQL("COMMENT ON ROLE {} IS {}").format(ident, sql.Literal(MARKER)))
        log(f"created role {name}")

    cur.execute(sql.SQL("ALTER ROLE {} PASSWORD {}").format(ident, sql.Literal(password)))

    if not db_exists(cur, name):
        cur.execute(sql.SQL("CREATE DATABASE {} OWNER {}").format(ident, ident))
        log(f"created database {name}")

    cur.execute(sql.SQL("REVOKE ALL ON DATABASE {} FROM PUBLIC").format(ident))


def prune(cur, desired):
    cur.execute(
        "SELECT rolname FROM pg_roles WHERE shobj_description(oid, 'pg_authid') = %s",
        (MARKER,),
    )
    stale = sorted({r[0] for r in cur.fetchall()} - set(desired))
    for name in stale:
        ident = sql.Identifier(name)
        cur.execute(sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(ident))
        cur.execute(sql.SQL("DROP ROLE {}").format(ident))
        log(f"dropped database and role {name}")


def main():
    apps = load_config()  # validate everything before touching the server
    log(f"configured apps: {', '.join(apps) or '(none)'}")
    with connect() as conn, conn.cursor() as cur:
        for name, password in apps.items():
            ensure_app(cur, name, password)
            log(f"ok: {name}")
        prune(cur, apps)
    log("done")


if __name__ == "__main__":
    main()
