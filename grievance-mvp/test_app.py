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

    def test_sync_requires_review_and_uses_mock_adapter(self):
        ticket = app.create_ticket({"channel": "email", "message": "My debit card failed"})
        with self.assertRaises(ValueError):
            app.sync_ticket(ticket["ticket_id"])
        app.review_ticket(ticket["ticket_id"], {
            "decision": "approve", "reviewer": "test-reviewer", "note": "checked"
        })
        result = app.sync_ticket(ticket["ticket_id"])
        self.assertEqual(result["integration"]["adapter"], "mock")
        self.assertEqual(result["integration"]["result"], "SIMULATED_ONLY")
        self.assertTrue(result["integration"]["external_ticket_id"].startswith("MOCK-"))
        self.assertEqual(len(app.audit_for(ticket["ticket_id"])), 3)
        with self.assertRaises(ValueError):
            app.sync_ticket(ticket["ticket_id"])

    def test_end_to_end_root_cause_and_follow_up(self):
        ticket = app.create_ticket({"channel": "email", "message": "Mobile banking login fails"})
        app.review_ticket(ticket["ticket_id"], {
            "decision": "approve", "reviewer": "test-reviewer", "note": "checked"
        })
        assigned = app.workflow_action(ticket["ticket_id"], {
            "action": "assign", "actor": "agent", "owner": "Digital Banking Support"
        })
        self.assertEqual(assigned["status"], "ASSIGNED")
        started = app.workflow_action(ticket["ticket_id"], {
            "action": "start", "actor": "agent"
        })
        self.assertEqual(started["status"], "IN_PROGRESS")
        resolved = app.workflow_action(ticket["ticket_id"], {
            "action": "resolve", "actor": "case-owner",
            "root_cause": "Expired session",
            "resolution": "Reset session and guide customer"
        })
        self.assertEqual(resolved["status"], "RESOLVED_PENDING_FOLLOW_UP")
        closed = app.workflow_action(ticket["ticket_id"], {
            "action": "follow_up", "actor": "agent",
            "follow_up_note": "Customer confirmed access restored",
            "customer_outcome": "satisfied"
        })
        self.assertEqual(closed["status"], "CLOSED")
        self.assertEqual(closed["root_cause"], "Expired session")
        self.assertEqual(closed["customer_outcome"], "satisfied")
        self.assertGreaterEqual(len(app.audit_for(ticket["ticket_id"])), 6)

    def test_resolution_requires_root_cause_and_resolution(self):
        ticket = app.create_ticket({"channel": "email", "message": "Mobile banking login fails"})
        app.workflow_action(ticket["ticket_id"], {
            "action": "assign", "actor": "agent", "owner": "Digital Banking Support"
        })
        app.workflow_action(ticket["ticket_id"], {"action": "start", "actor": "agent"})
        with self.assertRaises(ValueError):
            app.workflow_action(ticket["ticket_id"], {
                "action": "resolve", "actor": "case-owner", "root_cause": ""
            })


if __name__ == "__main__":
    unittest.main()
