import base64
import hashlib
import html
import json
import os
import secrets
import urllib.error
import urllib.parse
import urllib.request
from http import cookies
from http.server import BaseHTTPRequestHandler, HTTPServer

APP_NAME = os.environ.get("APP_NAME", "OIDC Demo")
CLIENT_ID = os.environ["CLIENT_ID"]
PORT = int(os.environ.get("PORT", "9001"))
REDIRECT_URI = os.environ["REDIRECT_URI"]
POST_LOGOUT_REDIRECT_URI = os.environ.get(
    "POST_LOGOUT_REDIRECT_URI",
    f"http://localhost:{PORT}/",
)
API_BASE = os.environ.get("API_BASE")
REALM = os.environ.get("OIDC_REALM", "enterprise-lab")
PUBLIC_BASE = os.environ.get("OIDC_PUBLIC_BASE", "http://localhost:8080")
INTERNAL_BASE = os.environ.get("OIDC_INTERNAL_BASE", PUBLIC_BASE)
PUBLIC_ISSUER = f"{PUBLIC_BASE}/realms/{REALM}"
INTERNAL_ISSUER = f"{INTERNAL_BASE}/realms/{REALM}"

# Learning-only in-memory transaction/session state.
transactions = {}
sessions = {}


def b64url_sha256(value: str) -> str:
    digest = hashlib.sha256(value.encode()).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


def decode_jwt_part(segment: str) -> dict:
    segment += "=" * (-len(segment) % 4)
    return json.loads(base64.urlsafe_b64decode(segment).decode())


def decode_jwt_header(token: str) -> dict:
    return decode_jwt_part(token.split(".")[0])


def decode_jwt_payload(token: str) -> dict:
    return decode_jwt_part(token.split(".")[1])


def post_form(url: str, data: dict) -> dict:
    body = urllib.parse.urlencode(data).encode()
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode())


def call_api(path: str, access_token: str):
    if not API_BASE:
        return 503, {"error": "API_BASE is not configured for this demo app"}

    request = urllib.request.Request(
        f"{API_BASE}{path}",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            raw = response.read().decode()
            return response.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as error:
        raw = error.read().decode()
        try:
            body = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            body = {"body": raw}
        return error.code, body
    except urllib.error.URLError as error:
        return 503, {"error": f"Ticket API unavailable: {error.reason}"}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Avoid logging authorization codes/tokens in callback URLs.
        if self.path.startswith("/callback"):
            return
        super().log_message(fmt, *args)

    def send_html(self, body: str, status=200, headers=None):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        if headers:
            for key, value in headers.items():
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body.encode())

    def session(self):
        raw = self.headers.get("Cookie")
        if not raw:
            return None, None

        jar = cookies.SimpleCookie()
        jar.load(raw)
        morsel = jar.get("demo_session")
        if not morsel:
            return None, None

        session_id = morsel.value
        return session_id, sessions.get(session_id)

    def redirect(self, location: str, clear_session_cookie: bool = False):
        self.send_response(302)
        self.send_header("Location", location)
        if clear_session_cookie:
            self.send_header(
                "Set-Cookie",
                "demo_session=; Max-Age=0; HttpOnly; SameSite=Lax; Path=/",
            )
        self.end_headers()

    def render_api_result(self, title: str, status: int, body):
        escaped = html.escape(json.dumps(body, indent=2, default=str))
        self.send_html(f"""
        <h1>{html.escape(title)}</h1>
        <p><strong>HTTP status:</strong> {status}</p>
        <pre>{escaped}</pre>
        <p><a href="/">Back</a></p>
        """)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/":
            _, session = self.session()
            if not session:
                self.send_html(f"""
                <h1>{html.escape(APP_NAME)}</h1>
                <p>Client: <code>{html.escape(CLIENT_ID)}</code></p>
                <p><a href="/login">Login with Keycloak</a></p>
                <p>
                  This application currently has no local session.
                  Keycloak may still have an SSO session in your browser.
                </p>
                """)
                return

            id_header = html.escape(json.dumps(session["id_header"], indent=2))
            id_claims = html.escape(json.dumps(session["id_claims"], indent=2))
            access_header = html.escape(json.dumps(session["access_header"], indent=2))
            access_claims = html.escape(json.dumps(session["access_claims"], indent=2))

            api_links = ""
            if API_BASE:
                api_links = """
                <h2>Ticket API experiments</h2>
                <p>The access token stays on this server. These links call Spring Boot with <code>Authorization: Bearer &lt;access-token&gt;</code>.</p>
                <ul>
                  <li><a href="/backend/me">Who did Spring authenticate?</a> — valid token required.</li>
                  <li><a href="/backend/tickets">View tickets</a> — EMPLOYEE role required.</li>
                  <li><a href="/backend/support">Support queue</a> — SUPPORT_AGENT role required.</li>
                  <li><a href="/backend/admin">Admin metrics</a> — PORTAL_ADMIN role required.</li>
                </ul>
                """

            self.send_html(f"""
            <h1>{html.escape(APP_NAME)}</h1>
            <p><strong>Authenticated:</strong> {html.escape(session['id_claims'].get('preferred_username', 'unknown'))}</p>

            <h2>Session experiments</h2>
            <ul>
              <li><a href="/login">Run authorization again</a> — contact Keycloak again.</li>
              <li><a href="/logout/local">Local logout</a> — remove only this application's session.</li>
              <li><a href="/logout/sso">Logout from Keycloak SSO</a> — remove this app session and terminate the Keycloak SSO session.</li>
            </ul>

            {api_links}

            <h2>ID token header</h2><pre>{id_header}</pre>
            <h2>ID token claims</h2><pre>{id_claims}</pre>
            <h2>Access token header</h2><pre>{access_header}</pre>
            <h2>Access token claims</h2><pre>{access_claims}</pre>
            <p>The JWT header shows values such as <code>alg</code> and <code>kid</code>. The Spring API performs the real signature/issuer/audience validation.</p>
            """)
            return

        backend_routes = {
            "/backend/me": ("Spring Security identity", "/api/me"),
            "/backend/tickets": ("Employee tickets", "/api/tickets"),
            "/backend/support": ("Support queue", "/api/support/queue"),
            "/backend/admin": ("Admin metrics", "/api/admin/metrics"),
        }

        if parsed.path in backend_routes:
            _, session = self.session()
            if not session:
                self.redirect("/login")
                return

            title, api_path = backend_routes[parsed.path]
            status, body = call_api(api_path, session["access_token"])
            self.render_api_result(title, status, body)
            return

        if parsed.path == "/login":
            state = secrets.token_urlsafe(24)
            nonce = secrets.token_urlsafe(24)
            verifier = secrets.token_urlsafe(64)
            challenge = b64url_sha256(verifier)
            transactions[state] = {"nonce": nonce, "verifier": verifier}

            params = {
                "client_id": CLIENT_ID,
                "response_type": "code",
                "scope": "openid profile email",
                "redirect_uri": REDIRECT_URI,
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                "state": state,
                "nonce": nonce,
            }
            location = f"{PUBLIC_ISSUER}/protocol/openid-connect/auth?{urllib.parse.urlencode(params)}"
            self.redirect(location)
            return

        if parsed.path == "/callback":
            params = urllib.parse.parse_qs(parsed.query)
            state = params.get("state", [None])[0]
            code = params.get("code", [None])[0]
            tx = transactions.pop(state, None)
            if not state or not code or not tx:
                self.send_html("<h1>Invalid callback</h1><p>Missing or unknown state/code.</p>", 400)
                return

            token_response = post_form(
                f"{INTERNAL_ISSUER}/protocol/openid-connect/token",
                {
                    "grant_type": "authorization_code",
                    "client_id": CLIENT_ID,
                    "code": code,
                    "redirect_uri": REDIRECT_URI,
                    "code_verifier": tx["verifier"],
                },
            )

            id_token = token_response["id_token"]
            access_token = token_response["access_token"]
            id_claims = decode_jwt_payload(id_token)

            if id_claims.get("nonce") != tx["nonce"]:
                self.send_html("<h1>Nonce validation failed</h1>", 400)
                return

            session_id = secrets.token_urlsafe(24)
            sessions[session_id] = {
                "id_token": id_token,
                "access_token": access_token,
                "id_header": decode_jwt_header(id_token),
                "id_claims": id_claims,
                "access_header": decode_jwt_header(access_token),
                "access_claims": decode_jwt_payload(access_token),
            }

            self.send_response(302)
            self.send_header("Location", "/")
            self.send_header(
                "Set-Cookie",
                f"demo_session={session_id}; HttpOnly; SameSite=Lax; Path=/",
            )
            self.end_headers()
            return

        if parsed.path == "/logout/local":
            session_id, _ = self.session()
            if session_id:
                sessions.pop(session_id, None)
            self.redirect("/", clear_session_cookie=True)
            return

        if parsed.path == "/logout/sso":
            session_id, session = self.session()

            if session_id:
                sessions.pop(session_id, None)

            if not session:
                self.redirect("/", clear_session_cookie=True)
                return

            params = {
                "client_id": CLIENT_ID,
                "id_token_hint": session["id_token"],
                "post_logout_redirect_uri": POST_LOGOUT_REDIRECT_URI,
            }
            logout_url = (
                f"{PUBLIC_ISSUER}/protocol/openid-connect/logout?"
                f"{urllib.parse.urlencode(params)}"
            )
            self.redirect(logout_url, clear_session_cookie=True)
            return

        self.send_html("<h1>404</h1>", 404)


print(f"{APP_NAME} listening on http://localhost:{PORT}")
HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
