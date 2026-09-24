# Enterprise IAM Lab

A compact, hands-on POC for understanding enterprise identity flows with Keycloak.

It focuses on the concepts that are commonly mixed together:

- SSO
- OAuth 2.0
- OpenID Connect (OIDC)
- Authorization Code + PKCE
- JWT access/ID tokens
- LDAP user federation
- roles, groups and API authorization
- identity brokering and where SAML fits

## Architecture

```text
OpenLDAP --LDAP--> Keycloak <--OIDC/PKCE--> Employee Portal
                      ^  ^                 Ticket Console
                      |  |
                      |  +-- OIDC/SAML --> External IdP (extension)
                      |
                      +-- issues JWT --> Ticket API
```

See [`docs/architecture.md`](docs/architecture.md) for the full diagram.

## Quick start

Start the IAM infrastructure and demo clients:

```bash
cp .env.example .env
cd infrastructure
docker compose --env-file ../.env up -d --build
```

In a second terminal start the Spring Boot resource server:

```bash
cd services/ticket-api
gradle bootRun
```

Open:

- Keycloak: `http://localhost:8080`
- Employee Portal: `http://localhost:9001`
- Ticket Console: `http://localhost:9002`
- Ticket API: `http://localhost:8081/public`

Keycloak bootstrap admin values come from `.env`.

## OIDC + SSO lab

The imported realm creates three clients:

- `employee-portal`
- `ticket-console`
- `ticket-api`

Create a temporary local user in Keycloak before LDAP federation.

1. Log into Employee Portal.
2. Open Ticket Console in the same browser profile.
3. Log in there too.
4. Observe that the second client reuses the Keycloak SSO session instead of asking for credentials again.
5. Compare local application logout with Keycloak SSO logout.

Read [`docs/sso.md`](docs/sso.md).

## Ticket API authorization lab

The Spring Boot resource server uses **Gradle (Groovy DSL)** and contains small in-memory ticket data so authorization is visible.

The demo web applications keep the access token server-side and can call:

- `/api/me`
- `/api/tickets`
- `/api/support/queue`
- `/api/admin/metrics`

The API uses Keycloak realm roles converted to Spring authorities:

```text
employee      -> ROLE_EMPLOYEE
support-agent -> ROLE_SUPPORT_AGENT
portal-admin  -> ROLE_PORTAL_ADMIN
```

Read [`docs/ticket-api.md`](docs/ticket-api.md) and test this with a local Keycloak user before moving to LDAP.

## LDAP lab

OpenLDAP contains `alice` and `bob`. After the OIDC, token and role experiments are clear, connect the realm to LDAP using [`docs/ldap-federation.md`](docs/ldap-federation.md).

The important boundary is:

```text
LDAP     = directory / user source
Keycloak = authentication, SSO, token issuance
OIDC     = app-facing login protocol
OAuth2   = protected-resource authorization framework
JWT      = token format
```

## Learning order

1. OIDC Authorization Code + PKCE
2. JWT header + claims: `kid`, `iss`, `sub`, `aud`, `exp`, `azp`, `nonce`
3. SSO across two clients
4. Local session vs Keycloak SSO session
5. Spring Boot JWT validation
6. Realm roles -> Spring authorities -> 200/403
7. LDAP federated users
8. LDAP group -> Keycloak role mapping
9. Identity brokering with an external OIDC IdP
10. Repeat brokering with SAML

## Security notes

This repository is a learning lab. Development passwords are intentionally simple and belong only in `.env`. Do not commit real credentials or tokens. Do not log authorization codes, access tokens, refresh tokens or client secrets.
