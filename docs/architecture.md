# Architecture

```mermaid
flowchart LR
    B[Browser]
    EP[Employee Portal\nOIDC client]
    TC[Ticket Console\nOIDC client]
    KC[Keycloak\nSSO / OIDC / OAuth 2.0]
    LDAP[(OpenLDAP\nFederated users)]
    API[Ticket API\nSpring Resource Server]
    PG[(PostgreSQL)]
    IDP[External IdP\nOIDC or SAML]

    B --> EP
    B --> TC
    EP <-->|Authorization Code + PKCE| KC
    TC <-->|Authorization Code + PKCE| KC
    KC <-->|LDAP user federation| LDAP
    KC -.->|Identity brokering| IDP
    KC --> PG
    EP -->|Bearer access JWT| API
    TC -->|Bearer access JWT| API
```

## Mental model

- **LDAP**: where a corporate user can come from.
- **OIDC**: how an application learns that the user authenticated.
- **OAuth 2.0**: how clients obtain tokens for protected resources.
- **JWT**: a signed token format used here for ID/access tokens.
- **SSO**: reuse of the Keycloak browser session across multiple clients.
- **SAML**: an alternative enterprise federation protocol, used here conceptually for external IdPs/legacy systems.
