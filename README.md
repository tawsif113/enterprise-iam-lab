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

```bash
cp .env.example .env
cd infrastructure
docker compose --env-file ../.env up -d --build
```

Open:

- Keycloak: `http://localhost:8080`
- Employee Portal: `http://localhost:9001`
- Ticket Console: `http://localhost:9002`

Keycloak bootstrap admin values come from `.env`.

## First lab: local OIDC + SSO

The imported realm creates three clients:

- `employee-portal`
- `ticket-console`
- `ticket-api`

Create a temporary local user in Keycloak if you want to test OIDC before LDAP federation.

1. Log into Employee Portal.
2. Open Ticket Console in the same browser profile.
3. Login there too.
4. Observe that the second client reuses the Keycloak SSO session instead of asking for credentials again.

Read [`docs/sso.md`](docs/sso.md).

## Second lab: federated users from LDAP

OpenLDAP contains `alice` and `bob`. Connect the realm to LDAP using [`docs/ldap-federation.md`](docs/ldap-federation.md), then repeat the same two-client SSO experiment.

The important boundary is:

```text
LDAP     = directory / user source
Keycloak = authentication, SSO, token issuance
OIDC     = app-facing login protocol
OAuth2   = protected-resource authorization framework
JWT      = token format
```

## Ticket API

Run the Spring Boot API separately:

```bash
cd services/ticket-api
mvn spring-boot:run
```

Then call it with an access token whose audience includes `ticket-api`:

```bash
curl -H "Authorization: Bearer $ACCESS_TOKEN" http://localhost:8081/api/me
```

See [`docs/token-validation.md`](docs/token-validation.md).

## Learning order

1. OIDC Authorization Code + PKCE
2. JWT claims: `iss`, `sub`, `aud`, `exp`, `azp`, `nonce`, `kid`
3. SSO across two clients
4. LDAP federated users
5. LDAP group → Keycloak role mapping
6. Spring Boot issuer/audience/role validation
7. Identity brokering with an external OIDC IdP
8. Repeat brokering with SAML
9. Logout, session revocation and disabled-user behavior

## Security notes

This repository is a learning lab. Development passwords are intentionally simple and belong only in `.env`. Do not commit real credentials or tokens. Do not log authorization codes, access tokens, refresh tokens or client secrets.
