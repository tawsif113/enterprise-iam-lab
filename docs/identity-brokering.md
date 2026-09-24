# Identity Brokering vs LDAP Federation

These are deliberately separate concepts.

## LDAP federation

```text
Keycloak --LDAP--> Active Directory / OpenLDAP
```

Keycloak directly searches/authenticates directory users and can map directory attributes/groups.

## Identity brokering

```text
Application --OIDC--> Keycloak --OIDC or SAML--> External IdP
```

Keycloak redirects the browser to an external identity provider. The external IdP authenticates the user; Keycloak then creates/links a local representation and issues its own tokens to the application.

A later lab extension can add a second Keycloak instance as the external IdP, first using OIDC and then SAML.
