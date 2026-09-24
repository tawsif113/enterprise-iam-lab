# SSO Experiment

This lab intentionally separates three things:

1. **Keycloak SSO session** — the browser session maintained by Keycloak.
2. **Application session** — the `demo_session` cookie created independently by each demo app.
3. **Issued tokens** — ID/access tokens obtained during an OIDC authorization flow.

They are related, but they are not the same object.

## Experiment 1 — SSO across two applications

1. Open Employee Portal at `http://localhost:9001`.
2. Click **Login with Keycloak** and authenticate.
3. Open Ticket Console at `http://localhost:9002` in the same browser profile.
4. Click **Login with Keycloak**.
5. Keycloak should reuse the existing realm SSO session, so the second client should not require credentials again.

SSO does **not** mean the two applications share one access token. Each client performs its own authorization flow and obtains its own tokens; the shared element is the Keycloak browser authentication session.

## Experiment 2 — Local logout

While authenticated in Ticket Console:

1. Click **Local logout**.
2. Ticket Console removes only its own `demo_session`.
3. Employee Portal remains logged in.
4. Click **Login with Keycloak** in Ticket Console again.

Expected result: Keycloak still has the SSO session, so Ticket Console should log back in without asking for credentials.

Flow:

```text
Ticket Console local session
          X

Keycloak SSO session
          ✓

Ticket Console --/authorize--> Keycloak
                                |
                                +--> SSO session found
                                     no password prompt
```

## Experiment 3 — Keycloak SSO logout

While authenticated:

1. Click **Logout from Keycloak SSO**.
2. The app removes its local session.
3. The browser is sent to Keycloak's OIDC end-session endpoint.
4. Keycloak terminates the SSO session.
5. The browser returns to the application.

Now click **Login with Keycloak** again.

Expected result: credentials are required because the Keycloak SSO session no longer exists.

Important: another application may still have its own local `demo_session` and continue showing previously stored claims until that application performs a new authorization check or clears its own local session.

## Why this matters

```text
Browser
|
|-- Keycloak SSO cookie
|     "Is this browser authenticated at the IdP?"
|
|-- Employee Portal demo_session
|     "Does Employee Portal have a local app session?"
|
|-- Ticket Console demo_session
      "Does Ticket Console have a local app session?"
```

Logging out of one layer does not automatically mean every other layer has disappeared.

## Post-logout redirect configuration

The two OIDC clients use exact development post-logout redirects:

- Employee Portal: `http://localhost:9001/`
- Ticket Console: `http://localhost:9002/`

These correspond to Keycloak's **Valid Post Logout Redirect URIs** setting.
