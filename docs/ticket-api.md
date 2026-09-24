# Ticket API Authorization Lab

This part of the lab makes the IAM flow visible through simple business data.

## Endpoints

| Endpoint | Requirement | Purpose |
| --- | --- | --- |
| `GET /public` | none | prove unauthenticated access |
| `GET /api/me` | valid access token | inspect the identity Spring accepted |
| `GET /api/tickets` | `ROLE_EMPLOYEE` | normal employee ticket access |
| `GET /api/tickets/{id}` | `ROLE_EMPLOYEE` | one ticket |
| `GET /api/support/queue` | `ROLE_SUPPORT_AGENT` | privileged support queue |
| `GET /api/admin/metrics` | `ROLE_PORTAL_ADMIN` | privileged admin metrics |

The data is intentionally in memory. The goal is IAM, not persistence.

## Role experiment before LDAP

Use your current local Keycloak user.

In Keycloak Admin:

1. Open `enterprise-lab`.
2. Go to **Users** and open your local test user.
3. Open **Role mapping**.
4. Assign only `employee`.
5. Log in again so Keycloak issues a fresh access token.

Expected result:

- `/api/me` -> 200
- `/api/tickets` -> 200
- `/api/support/queue` -> 403
- `/api/admin/metrics` -> 403

Then add `support-agent`, log in again, and retry.

Expected result:

- support queue changes from 403 to 200.

Finally add `portal-admin`, log in again, and retry the metrics endpoint.

This demonstrates:

```text
Keycloak realm role
        |
        v
access token realm_access.roles
        |
        v
SecurityConfig keycloakConverter()
        |
        v
Spring ROLE_...
        |
        v
@PreAuthorize
        |
        v
200 or 403
```

## Why log in again after changing roles?

The access token already issued to the application does not magically gain a new role when you edit Keycloak.

A new authorization flow produces a new access token containing the updated claims.
