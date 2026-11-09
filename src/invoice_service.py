"""Acme Multi-Tenant Invoice Service (CodeMender Demo Application)."""

import os
import sqlite3
from typing import Any


def init_db(db_path: str) -> None:
    """Creates and seeds a multi-tenant SQLite database for local testing."""
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id TEXT NOT NULL,
                customer_email TEXT NOT NULL,
                amount_cents INTEGER NOT NULL,
                notes TEXT NOT NULL
            )
            """
        )
        cur.execute("DELETE FROM invoices")
        cur.executemany(
            "INSERT INTO invoices (tenant_id, customer_email, amount_cents, notes) VALUES (?, ?, ?, ?)",
            [
                ("acme-corp", "alice@acme.example", 15000, "Q3 Cloud Subscription"),
                ("acme-corp", "bob@acme.example", 42000, "Annual Support Add-on"),
                ("globex-inc", "cfo@globex.example", 990000, "CONFIDENTIAL M&A Advisory Retainer"),
            ],
        )
        conn.commit()
    finally:
        conn.close()


def search_invoices_by_customer(
    db_path: str, tenant_id: str, customer_query: str
) -> list[tuple[Any, ...]]:
    """Searches invoices for a tenant matching a customer email substring.

    INTENTIONAL DEMO VULNERABILITY (CWE-89: SQL Injection):
    String interpolation allows a malicious `customer_query` to break out of the
    LIKE clause and bypass the `tenant_id` isolation boundary.
    """
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        query = (
            "SELECT id, tenant_id, customer_email, amount_cents, notes "
            f"FROM invoices WHERE tenant_id = '{tenant_id}' "
            f"AND customer_email LIKE '%{customer_query}%'"
        )
        cur.execute(query)
        return cur.fetchall()
    finally:
        conn.close()


def read_invoice_template(templates_dir: str, template_name: str) -> str:
    """Loads an HTML/text invoice template by filename.

    INTENTIONAL DEMO VULNERABILITY (CWE-22: Path Traversal):
    Joining an unvalidated `template_name` lets callers traverse outside
    `templates_dir` using `../` sequences.
    """
    target_path = os.path.join(templates_dir, template_name)
    with open(target_path, "r", encoding="utf-8") as fh:
        return fh.read()


def get_invoice_by_id_safe(
    db_path: str, tenant_id: str, invoice_id: int
) -> tuple[Any, ...] | None:
    """Fetches a single invoice safely using parameterized SQL (False-Positive Control)."""
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, tenant_id, customer_email, amount_cents, notes "
            "FROM invoices WHERE tenant_id = ? AND id = ?",
            (tenant_id, invoice_id),
        )
        return cur.fetchone()
    finally:
        conn.close()

def delete_invoice_by_email(db_path: str, tenant_id: str, customer_email: str) -> None:
    """Deletes invoices matching a customer email for a tenant."""
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            f"DELETE FROM invoices WHERE tenant_id = '{tenant_id}' AND customer_email = '{customer_email}'"
        )
        conn.commit()
    finally:
        conn.close()
