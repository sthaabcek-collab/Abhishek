import json
import os
import tempfile
import unittest
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import threading
from http.server import HTTPServer

import app


class GrievanceMVPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        app.DB_PATH = Path(self.temp.name) / "test.db"
        app.init_db()

    def tearDown(self):
        self.temp.cleanup()

    def test_classification_and_fallback(self):
        self.assertEqual(app.classify("My ATM debit card failed")[0], "card_transaction")
        self.assertEqual(app.classify("I have an unusual issue")[0], "other_or_uncertain")

    def test_create_and_review_ticket_with_audit(self):
        ticket = app.create_ticket({"channel": "email", "message": "Mobile banking login fails"})
        self.assertTrue(ticket["ticket_id"].startswith("GRV-"))
        self.assertEqual(ticket["status"], "PENDING_HUMAN_REVIEW")
        reviewed = app.review_ticket(ticket["ticket_id"], {
            "decision": "approve", "reviewer": "test-reviewer", "note": "checked"
        })
        self.assertEqual(reviewed["status"], "READY_FOR_EXISTING_SYSTEM")
        events = app.audit_for(ticket["ticket_id"])
        self.assertEqual(len(events), 2)

    def test_required_fields(self):
        with self.assertRaises(ValueError):
            app.create_ticket({"channel": "email", "message": "  "})


if __name__ == "__main__":
    unittest.main()
