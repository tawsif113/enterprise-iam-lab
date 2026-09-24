# SSO Experiment

1. Open Employee Portal at `http://localhost:9001`.
2. Click Login and authenticate as the same Keycloak user.
3. Open Ticket Console at `http://localhost:9002` in the same browser profile.
4. Click Login.
5. Keycloak should reuse the existing realm SSO session, so the second client should not require credentials again.

SSO does **not** mean the two applications share one access token. Each client performs its own authorization flow and obtains its own tokens; the shared element is the Keycloak browser authentication session.

To prove the boundary, terminate the user's Keycloak session and repeat the Ticket Console login. Credentials should be required again.
