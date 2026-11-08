"""Unit tests for Acme Multi-Tenant Invoice Service.

CodeMender executes this suite via `build.command` inside the sandbox during
`cm fix` to guarantee that security patches do not break legitimate business flows.
"""

import os
import tempfile
import unittest

from src.invoice_service import (
    get_invoice_by_id_safe,
    init_db,
    read_invoice_template,
    search_invoices_by_customer,
)


class InvoiceServiceTest(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "invoices.db")
        self.templates_dir = os.path.join(self.temp_dir.name, "templates")
        os.makedirs(self.templates_dir, exist_ok=True)
        with open(
            os.path.join(self.templates_dir, "standard.txt"),
            "w",
            encoding="utf-8",
        ) as fh:
            fh.write("Invoice Header: Standard Terms Net-30\n")
        init_db(self.db_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_legitimate_customer_search_stays_scoped_to_tenant(self) -> None:
        rows = search_invoices_by_customer(self.db_path, "acme-corp", "alice")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1], "acme-corp")
        self.assertEqual(rows[0][2], "alice@acme.example")

    def test_safe_get_invoice_by_id(self) -> None:
        rows = search_invoices_by_customer(self.db_path, "acme-corp", "bob")
        invoice_id = rows[0][0]
        record = get_invoice_by_id_safe(self.db_path, "acme-corp", invoice_id)
        self.assertIsNotNone(record)
        self.assertEqual(record[2], "bob@acme.example")

    def test_legitimate_template_load(self) -> None:
        content = read_invoice_template(self.templates_dir, "standard.txt")
        self.assertIn("Net-30", content)


if __name__ == "__main__":
    unittest.main()
