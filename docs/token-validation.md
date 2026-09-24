# API Token Validation

The Spring Boot `ticket-api` is an OAuth 2.0 Resource Server.

It is configured to validate:

- JWT signature via the issuer's JWKS
- issuer (`iss`)
- audience (`aud`) = `ticket-api`
- expiration (`exp`)

Realm roles from `realm_access.roles` are deliberately converted to Spring `ROLE_*` authorities.

Experiments to perform:

1. Valid token → `/api/me` returns claims.
2. Expired token → 401.
3. Token from wrong issuer → 401.
4. Token without `ticket-api` audience → 401.
5. Valid user without `support-agent` → `/api/support` returns 403.
6. Add the role and retry → success.
