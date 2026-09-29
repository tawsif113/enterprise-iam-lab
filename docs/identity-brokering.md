# Identity Brokering Lab

## Goal

Compare LDAP user federation with OIDC identity brokering.

```text
LDAP federation:
Main Keycloak --LDAP--> OpenLDAP

OIDC brokering:
App --OIDC--> Main Keycloak --OIDC--> External Corporate IdP
```

The external IdP authenticates the user. Main Keycloak creates/links a local representation and issues its own application-facing tokens.

## Components

```text
Employee Portal / Ticket Console
            |
            | OIDC
            v
Main Keycloak (enterprise-lab)
localhost:8080
            |
            | OIDC broker
            v
External Keycloak (corporate)
localhost:8180
            |
            +-- external-alice
```

The second Keycloak is a lab stand-in for another OIDC IdP.

## Start

Add these to an existing `.env` if they are missing:

```dotenv
EXTERNAL_KEYCLOAK_ADMIN=external-admin
EXTERNAL_KEYCLOAK_ADMIN_PASSWORD=external_admin_dev_password
```

Then:

```bash
./scripts/configure-oidc-broker.sh
```

The script starts the external IdP, preserves the existing main Keycloak database, creates/updates the `corporate-oidc` broker, and adds an IdP mapper that grants brokered users the `employee` realm role.

## Demo external identity

```text
realm:    corporate
user:     external-alice
password: ExternalAlice123!
client:   enterprise-lab-broker
```

The external OIDC client redirects to:

```text
http://localhost:8080/realms/enterprise-lab/broker/corporate-oidc/endpoint
```

Browser authorization uses `localhost:8180`, while server-to-server token/UserInfo/JWKS calls use the Docker hostname `external-keycloak:8080`.

## Test

1. End the current main-Keycloak SSO session.
2. Open `http://localhost:9001`.
3. Click **Login with Keycloak**.
4. Choose **Corporate IdP (OIDC)**.
5. Sign in at the external Keycloak as `external-alice`.
6. Return through the main Keycloak broker to Employee Portal.
7. Inspect the application-facing access token.
8. Open Ticket Console and verify that the main Keycloak SSO session prevents a second credential prompt.

A first broker login can show a profile/account confirmation screen; that is part of Keycloak's first-broker-login flow.

## What proves brokering worked

In the main Keycloak:

```text
enterprise-lab -> Users -> external-alice
```

The user is linked to an external identity.

In the Employee Portal access token, the issuer should still be:

```text
http://localhost:8080/realms/enterprise-lab
```

not the external realm on port 8180. The external IdP authenticated the user, but Main Keycloak issued the token trusted by our applications and Spring API.

The broker mapper grants `employee`, so the new main-Keycloak access token should contain that role and `/api/tickets` should be allowed.

## Two OIDC relationships

```text
A) Main Keycloak = OIDC client
   External Keycloak = OIDC provider

B) Employee Portal / Ticket Console = OIDC clients
   Main Keycloak = OIDC provider
```

External-provider tokens are used inside the broker relationship. Our Spring API continues to trust only the access JWT issued by Main Keycloak.

## Next

Repeat the broker relationship with SAML while keeping the application-facing side OIDC.
