#!/usr/bin/env python3
"""Execute the SQL layer against PostgreSQL using the psql client.

The scripts use psql's ``\\copy`` meta-command, so this runner shells out to
``psql`` rather than reimplementing the load in Python. It creates the target
database if it does not exist, runs the four scripts in dependency order and
writes each script's output to ``sql/output/``.

Examples
--------
Run against a local server with trust authentication::

    python scripts/run_sql.py --host 127.0.0.1 --port 5433 --user postgres

Run against a password-protected server::

    set PGPASSWORD=your-password
    python scripts/run_sql.py --host localhost --port 5432 --user postgres

Educational synthetic data only. Not an audit opinion.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SQL_DIR = BASE_DIR / "sql"
OUT_DIR = SQL_DIR / "output"

# Dependency order: schema -> load -> analysis -> control tests.
SCRIPTS = [
    "01_create_tables.sql",
    "03_load_data.sql",
    "02_variance_and_dq_queries.sql",
    "04_control_tests.sql",
]

WINDOWS_PG_ROOTS = [
    Path(r"C:\Program Files\PostgreSQL"),
    Path(r"C:\Program Files (x86)\PostgreSQL"),
]


def find_psql(explicit: str | None) -> str:
    if explicit:
        path = Path(explicit)
        if not path.exists():
            sys.exit(f"psql not found at {path}")
        return str(path)

    found = shutil.which("psql")
    if found:
        return found

    for root in WINDOWS_PG_ROOTS:
        if not root.exists():
            continue
        versions = sorted(
            (d for d in root.iterdir() if (d / "bin" / "psql.exe").exists()),
            key=lambda d: d.name,
            reverse=True,
        )
        if versions:
            return str(versions[0] / "bin" / "psql.exe")

    sys.exit(
        "psql not found. Add PostgreSQL's bin directory to PATH or pass --psql."
    )


def psql_env(password: str | None) -> dict[str, str]:
    env = os.environ.copy()
    env["PGCLIENTENCODING"] = "UTF8"
    env["PGCONNECT_TIMEOUT"] = env.get("PGCONNECT_TIMEOUT", "10")
    if password is not None:
        env["PGPASSWORD"] = password
    return env


def run_psql(
    psql: str,
    args: list[str],
    env: dict[str, str],
    cwd: Path,
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [psql, *args],
        cwd=str(cwd),
        env=env,
        capture_output=True,
        check=False,
    )


def decode(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")


def database_exists(
    psql: str, host: str, port: str, user: str, database: str, env: dict[str, str]
) -> bool:
    result = run_psql(
        psql,
        [
            "-h", host, "-p", port, "-U", user, "-d", "postgres",
            "-w", "-X", "-tAc",
            f"SELECT 1 FROM pg_database WHERE datname = '{database}'",
        ],
        env,
        BASE_DIR,
    )
    if result.returncode != 0:
        sys.stderr.write(decode(result.stderr))
        sys.exit("Could not connect to the PostgreSQL server.")
    return decode(result.stdout).strip() == "1"


def create_database(
    psql: str, host: str, port: str, user: str, database: str, env: dict[str, str]
) -> None:
    result = run_psql(
        psql,
        ["-h", host, "-p", port, "-U", user, "-d", "postgres", "-w",
         "-X", "-v", "ON_ERROR_STOP=1", "-c", f'CREATE DATABASE "{database}"'],
        env,
        BASE_DIR,
    )
    if result.returncode != 0:
        sys.stderr.write(decode(result.stderr))
        sys.exit(f"Could not create database {database}.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=os.environ.get("PGHOST", "localhost"))
    parser.add_argument("--port", default=os.environ.get("PGPORT", "5432"))
    parser.add_argument("--user", default=os.environ.get("PGUSER", "postgres"))
    parser.add_argument(
        "--database", default=os.environ.get("PGDATABASE", "finance_review")
    )
    parser.add_argument(
        "--password",
        default=os.environ.get("PGPASSWORD"),
        help="Password for the PostgreSQL user (or set PGPASSWORD).",
    )
    parser.add_argument(
        "--psql", default=None, help="Path to psql if it is not on PATH."
    )
    args = parser.parse_args()

    psql = find_psql(args.psql)
    env = psql_env(args.password)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"psql     : {psql}")
    print(f"server   : {args.host}:{args.port} (user {args.user})")
    print(f"database : {args.database}")

    if not database_exists(psql, args.host, args.port, args.user, args.database, env):
        print(f"creating database {args.database} ...")
        create_database(psql, args.host, args.port, args.user, args.database, env)

    failures = 0
    for name in SCRIPTS:
        script = SQL_DIR / name
        if not script.exists():
            sys.exit(f"missing script: {script}")

        result = run_psql(
            psql,
            [
                "-h", args.host, "-p", args.port, "-U", args.user,
                "-d", args.database, "-w", "-X", "-v", "ON_ERROR_STOP=1",
                "-P", "pager=off", "-f", str(script.relative_to(BASE_DIR)),
            ],
            env,
            BASE_DIR,
        )
        output = decode(result.stdout) + decode(result.stderr)
        (OUT_DIR / f"{script.stem}.txt").write_text(output, encoding="utf-8")

        status = "OK" if result.returncode == 0 else f"FAILED ({result.returncode})"
        print(f"{name:<38} {status}")
        if result.returncode != 0:
            failures += 1
            print(output[-2000:])

    print(f"\nOutputs written to {OUT_DIR.relative_to(BASE_DIR)}")
    if failures:
        sys.exit(f"{failures} script(s) failed")
    print("All scripts completed successfully.")


if __name__ == "__main__":
    main()
