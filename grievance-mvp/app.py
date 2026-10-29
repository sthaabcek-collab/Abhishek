"""Local grievance-ticket MVP; demo only, not production banking software."""
import json
import os
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

DB_PATH = Path(os.environ.get("GRIEVANCE_DB", "data/grievance.db"))
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))

# Example rules only. Replace with rules approved by Operations and Compliance.
RULES = [
    (("debit card", "credit card", "atm", "pos", "card transaction"),
     "card_transaction", "Cards Operations", 24),
    (("mobile banking", "mpin", "login", "mobile app", "otp"),
     "digital_banking", "Digital Banking Support", 48),
    (("branch", "counter", "staff service"),
     "branch_service", "Branch Operations Review", 48),
]
FALLBACK = ("other_or_uncertain", "Customer Care Review", 48)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def classify(message):
    text = " ".join(message.lower().split())
    for keywords, category, queue, hours in RULES:
        if any(word in text for word in keywords):
            return category, queue, hours, "keyword_match"
    return FALLBACK[0], FALLBACK[1], FALLBACK[2], "fallback_human_review"


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS tickets (
          ticket_id TEXT PRIMARY KEY,
          created_at TEXT NOT NULL,
          channel TEXT NOT NULL,
          message TEXT NOT NULL,
          category TEXT NOT NULL,
          queue_name TEXT NOT NULL,
          due_at TEXT NOT NULL,
          status TEXT NOT NULL,
          reviewed_by TEXT,
          review_note TEXT
        );
        CREATE TABLE IF NOT EXISTS audit_events (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          ticket_id TEXT NOT NULL,
          event TEXT NOT NULL,
          actor TEXT NOT NULL,
          detail TEXT NOT NULL,
          created_at TEXT NOT NULL
        );
        """)


def row_dict(row):
    return dict(row) if row else None


def create_ticket(payload):
    channel = str(payload.get("channel", "")).strip().lower()
    message = str(payload.get("message", "")).strip()
    if not channel or not message:
        raise ValueError("Both channel and message are required.")
    category, queue_name, hours, reason = classify(message)
    now = datetime.now(timezone.utc)
    ticket_id = "GRV-" + uuid.uuid4().hex[:10].upper()
    due_at = (now + timedelta(hours=hours)).isoformat()
    with connect() as db:
        db.execute(
            """INSERT INTO tickets
            (ticket_id, created_at, channel, message, category, queue_name,
             due_at, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (ticket_id, now.isoformat(), channel, message, category,
             queue_name, due_at, "PENDING_HUMAN_REVIEW"),
        )
        db.execute(
            """INSERT INTO audit_events
            (ticket_id, event, actor, detail, created_at)
            VALUES (?, ?, ?, ?, ?)""",
            (ticket_id, "TICKET_DRAFT_CREATED", "system",
             "Suggestion reason: " + reason + "; staff review required.",
             now.isoformat()),
        )
        ticket = row_dict(db.execute(
            "SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,)
        ).fetchone())
    return ticket


def list_tickets():
    with connect() as db:
        return [row_dict(r) for r in db.execute(
            "SELECT * FROM tickets ORDER BY created_at DESC"
        ).fetchall()]


def review_ticket(ticket_id, payload):
    decision = str(payload.get("decision", "")).strip().lower()
    reviewer = str(payload.get("reviewer", "")).strip()
    note = str(payload.get("note", "")).strip()
    if decision not in ("approve", "correct") or not reviewer:
        raise ValueError("decision must be approve/correct and reviewer is required.")
    with connect() as db:
        row = db.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,)).fetchone()
        if not row:
            return None
        category = str(payload.get("category", row["category"])).strip()
        queue_name = str(payload.get("queue_name", row["queue_name"])).strip()
        if not category or not queue_name:
            raise ValueError("category and queue_name cannot be empty.")
        status = "READY_FOR_EXISTING_SYSTEM" if decision == "approve" else "REVIEWED_CORRECTED"
        now = utc_now()
        db.execute(
            """UPDATE tickets SET category=?, queue_name=?, status=?,
               reviewed_by=?, review_note=? WHERE ticket_id=?""",
            (category, queue_name, status, reviewer, note, ticket_id),
        )
        db.execute(
            """INSERT INTO audit_events
            (ticket_id, event, actor, detail, created_at)
            VALUES (?, ?, ?, ?, ?)""",
            (ticket_id, "HUMAN_REVIEW_" + decision.upper(), reviewer,
             json.dumps({"category": category, "queue_name": queue_name, "note": note}),
             now),
        )
        return row_dict(db.execute(
            "SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,)
        ).fetchone())


def overdue_tickets():
    now = datetime.now(timezone.utc)
    with connect() as db:
        rows = db.execute(
            """SELECT * FROM tickets WHERE status NOT IN
               ('RESOLVED', 'CLOSED') ORDER BY due_at"""
        ).fetchall()
    return [row_dict(r) for r in rows
            if datetime.fromisoformat(r["due_at"]) < now]


def audit_for(ticket_id):
    with connect() as db:
        return [row_dict(r) for r in db.execute(
            "SELECT * FROM audit_events WHERE ticket_id=? ORDER BY id",
            (ticket_id,)
        ).fetchall()]


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        size = int(self.headers.get("Content-Length", "0"))
        if size > 100_000:
            raise ValueError("Request body too large.")
        return json.loads(self.rfile.read(size) or b"{}")

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            return self.send_json(200, {"status": "ok", "mode": "demo"})
        if path == "/tickets":
            return self.send_json(200, {"tickets": list_tickets()})
        if path == "/tickets/overdue":
            return self.send_json(200, {"tickets": overdue_tickets()})
        if path.startswith("/tickets/") and path.endswith("/audit"):
            ticket_id = path.split("/")[2]
            return self.send_json(200, {"events": audit_for(ticket_id)})
        return self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            payload = self.read_json()
            if path == "/tickets":
                return self.send_json(201, create_ticket(payload))
            if path.startswith("/tickets/") and path.endswith("/review"):
                ticket_id = path.split("/")[2]
                ticket = review_ticket(ticket_id, payload)
                if ticket is None:
                    return self.send_json(404, {"error": "Ticket not found"})
                return self.send_json(200, ticket)
            return self.send_json(404, {"error": "Not found"})
        except (ValueError, json.JSONDecodeError) as exc:
            return self.send_json(400, {"error": str(exc)})
        except Exception:
            # Avoid exposing internal database details in HTTP responses.
            return self.send_json(500, {"error": "Internal server error"})

    def log_message(self, fmt, *args):
        # Demo access log avoids printing request bodies/customer messages.
        super().log_message(fmt, *args)


if __name__ == "__main__":
    init_db()
    print(f"Demo API listening at http://{HOST}:{PORT}")
    HTTPServer((HOST, PORT), Handler).serve_forever()
