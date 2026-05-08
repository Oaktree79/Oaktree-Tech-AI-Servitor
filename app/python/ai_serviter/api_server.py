from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
import json
import os

from .auth import AuthManager
from .runtime import ServiterRuntime


class ServiterAPIHandler(BaseHTTPRequestHandler):
    runtime: ServiterRuntime = None  # type: ignore
    auth: AuthManager = None  # type: ignore

    def _json(self, status: int, payload):
        body = json.dumps(payload, indent=2, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length).decode("utf-8")) if length else {}

    def _require_auth(self):
        if os.getenv("SERVITER_DISABLE_AUTH") == "1":
            return True
        auth_header = self.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            self._json(401, {"error": "Missing bearer token"})
            return False
        token = auth_header.split(" ", 1)[1]
        user = self.auth.verify_token(token)
        if not user:
            self._json(401, {"error": "Invalid or expired token"})
            return False
        return True

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._json(200, {"ok": True})
            return
        if not self._require_auth():
            return
        if parsed.path == "/tasks":
            self._json(200, [t.__dict__ for t in self.runtime.queue.list()])
        elif parsed.path == "/git/status":
            self._json(200, self.runtime.git.status())
        else:
            self._json(404, {"error": "Not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/auth/login":
            body = self._read_json()
            user = self.auth.authenticate(body.get("username", ""), body.get("password", ""))
            if not user:
                self._json(401, {"error": "Invalid credentials"})
                return
            self._json(200, {"token": self.auth.issue_token(user), "role": user.role})
            return

        if not self._require_auth():
            return

        body = self._read_json()
        if parsed.path == "/tasks":
            task = self.runtime.submit(body.get("instruction", ""), priority=int(body.get("priority", 100)))
            self._json(201, task.__dict__)
        elif parsed.path.endswith("/approve"):
            task_id = parsed.path.split("/")[2]
            self.runtime.approvals.approve(task_id, approved_by=body.get("approved_by", "api-user"), reason=body.get("reason", ""))
            self._json(200, self.runtime.queue.get(task_id).__dict__)
        elif parsed.path == "/worker/run-once":
            self._json(200, self.runtime.run_once())
        elif parsed.path == "/system/pause":
            self._json(200, self.runtime.overrides.pause(body.get("reason", "")))
        elif parsed.path == "/system/resume":
            self._json(200, self.runtime.overrides.resume())
        else:
            self._json(404, {"error": "Not found"})


def run_api_server(root: str = ".", host: str = "127.0.0.1", port: int = 8765, db_path: str | None = None):
    runtime = ServiterRuntime(root=root, db_path=db_path)
    auth = AuthManager(runtime.db)
    admin_password = os.getenv("SERVITER_ADMIN_PASSWORD", "admin-change-me")
    auth.create_user("admin", admin_password, role="admin")
    ServiterAPIHandler.runtime = runtime
    ServiterAPIHandler.auth = auth
    server = ThreadingHTTPServer((host, port), ServiterAPIHandler)
    print(f"AI Serviter API listening on http://{host}:{port}")
    server.serve_forever()
