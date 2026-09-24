# LDAP User Federation

OpenLDAP is seeded with two directory users:

- `alice` / `Alice123!`
- `bob` / `Bob123!`

Both are members of the LDAP group `ticket-agents`.

## Connect Keycloak to OpenLDAP

In `enterprise-lab`:

1. Open **User federation** → **Add LDAP providers**.
2. Use:
   - Vendor: `Other`
   - Connection URL: `ldap://openldap:389`
   - Users DN: `ou=people,dc=acme,dc=local`
  - Bind type: simple
   - Bind DN: `cn=admin,dc=acme,dc=local`
   - Bind credentials: the `LDAP_ADMIN_PASSWORD` value
   - Username LDAP attribute: `uid`
   - RDN LDAP attribute: `uid`
  - UID attribute: `entryUUID`
   - User object classes: `inetOrgPerson`
   - Edit mode: `READ_ONLY`
   - Import users: ON
3. Test connection and authentication.
4. Synchronize users or simply log in as Alice to trigger lookup/import.

## Group mapping

Add an LDAP group mapper if you want `cn=ticket-agents,ou=groups,...` exposed as Keycloak group membership. Then map that organizational group to an application role such as `support-agent`.

The directory remains the authoritative place for the user's corporate identity/credentials. Keycloak remains the application-facing authentication, SSO token layer.
